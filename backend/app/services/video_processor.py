import asyncio
from pathlib import Path
from typing import List, Optional
import logging

from app.services.ffmpeg_handler import FFmpegHandler
from app.services.transitions import get_xfade_name
from app.services.ai_director import AIDirector
from app.services.style_editor import StyleEditor
from app.services.ai_reframing import AIReframingService
from app.services.video_enhancement import VideoEnhancementService
from app.exporters.mlt_exporter import MLTExporter
from app.routes.jobs import update_job_progress, mark_job_complete, mark_job_failed

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Orchestrate video processing pipeline"""

    def __init__(self):
        self.ffmpeg = FFmpegHandler()
        self.ai_director = AIDirector()
        self.style_editor = StyleEditor()
        self.ai_reframing = AIReframingService()
        self.video_enhancer = VideoEnhancementService()

    def process_video(
        self,
        job_id: str,
        video_paths: List[str],
        music_path: str,
        style: str,
        output_dir: Path,
        music_start_time: float = 0.0,
        music_end_time: float = 30.0,
        cut_points: Optional[List[float]] = None,
        transition_name: Optional[str] = None,
        export_mlt: bool = False,
        enable_ai_reframing: bool = True,
        enable_quality_enhancement: bool = True,
    ) -> bool:
        """Process video: detect beats, cut segments, concatenate, transitions, mix audio"""
        try:
            update_job_progress(job_id, 10, "Validating files")

            # Step 1: Validate inputs
            for video_path in video_paths:
                if not Path(video_path).exists():
                    raise FileNotFoundError(f"Video not found: {video_path}")
            if not Path(music_path).exists():
                raise FileNotFoundError(f"Music not found: {music_path}")

            update_job_progress(job_id, 20, "Analyzing media")

            # Step 2: Get media info
            music_duration = self.ffmpeg.get_audio_info(music_path).get("duration", 30.0)
            target_duration = min(music_duration, music_end_time - music_start_time)
            
            # Determine Cuts Strategy
            cuts_metadata = []
            
            # Try AI Director
            if self.ai_director.model:
                try:
                    update_job_progress(job_id, 25, "AI Director analyzing footage...")
                    # Note: For MVP, AI director currently only processes the first video
                    ai_cuts = self.ai_director.get_ai_cuts(video_paths, style, target_duration)
                    
                    for cut in ai_cuts:
                        source_idx = cut.get("source_index", 0)
                        if source_idx < len(video_paths):
                            cuts_metadata.append({
                                "source_path": video_paths[source_idx],
                                "start": cut["start"],
                                "duration": cut["end"] - cut["start"]
                            })
                except Exception as e:
                    logger.error(f"AI Director failed, falling back to random cuts: {e}")

            # Fallback to Random Smart Cutting if no AI cuts
            if not cuts_metadata:
                # If cut_points were provided by upstream (beat detector), use them to create segments
                if cut_points:
                    logger.info("Using provided cut_points to build segments")
                    # cut_points are absolute times in the music; build segment boundaries
                    music_start = music_start_time
                    music_end = music_start_time + target_duration
                    boundaries = [music_start] + sorted([float(c) for c in cut_points]) + [music_end]
                    # Build segments from consecutive boundaries
                    for idx in range(len(boundaries) - 1):
                        seg_start_music = boundaries[idx]
                        seg_end_music = boundaries[idx + 1]
                        seg_duration = seg_end_music - seg_start_music
                        # Assign source video sequentially to avoid repeating the same timestamp
                        source_video = video_paths[idx % len(video_paths)]
                        video_info = self.ffmpeg.get_video_info(source_video)
                        source_duration = video_info.get("duration", 10.0)
                        # Center the cut in the source video to reduce repeated identical frames
                        max_start = max(0, source_duration - seg_duration)
                        start_time = max_start / 2.0
                        cuts_metadata.append({
                            "source_path": source_video,
                            "start": float(start_time),
                            "duration": float(seg_duration)
                        })
                else:
                    logger.info("Generating random smart cuts")
                    import random
                    num_clips = int(target_duration / 4)  # ~4 seconds per clip
                    
                    for i in range(num_clips):
                        source_video = video_paths[i % len(video_paths)] # Cycle through inputs
                        video_info = self.ffmpeg.get_video_info(source_video)
                        source_duration = video_info.get("duration", 10.0)
                        
                        clip_duration = target_duration / num_clips
                        max_start = max(0, source_duration - clip_duration)
                        start_time = random.uniform(0, max_start)
                        
                        cuts_metadata.append({
                            "source_path": source_video,
                            "start": start_time,
                            "duration": clip_duration
                        })

            # Create segments directory
            segments_dir = output_dir / "segments"
            segments_dir.mkdir(exist_ok=True)
            clips_to_concat = []

            update_job_progress(job_id, 30, "Cutting segments")
            
            # Step 3: Execute Cuts
            for i, cut in enumerate(cuts_metadata):
                segment_path = segments_dir / f"segment_{i}.mp4"
                if self.ffmpeg.trim_video(
                    cut["source_path"], 
                    str(segment_path), 
                    cut["start"], 
                    cut["duration"],
                    width=1080,
                    height=1920
                ):
                    clips_to_concat.append(str(segment_path))
            
            if not clips_to_concat:
                raise Exception("No video segments could be created")

            update_job_progress(job_id, 40, "Applying style processing")
            
            # Step 3.5: Apply Style to Segments
            styled_clips = []
            for i, clip_path in enumerate(clips_to_concat):
                styled_path = segments_dir / f"styled_segment_{i}.mp4"
                
                success = self.style_editor.apply_style_to_video(
                    clip_path,
                    str(styled_path),
                    style
                )
                
                if success:
                    styled_clips.append(str(styled_path))
                    logger.info(f"Applied {style} style to segment {i+1}/{len(clips_to_concat)}")
                else:
                    # Fallback to original if styling fails
                    styled_clips.append(clip_path)
                    logger.warning(f"Style processing failed for segment {i+1}, using original")
            
            clips_to_concat = styled_clips

            # Step 3.6: Apply AI Reframing (if enabled)
            if enable_ai_reframing:
                update_job_progress(job_id, 50, "Analyzing video for smart reframing")
                reframed_clips = []
                
                for i, clip_path in enumerate(clips_to_concat):
                    try:
                        reframed_path = segments_dir / f"reframed_segment_{i}.mp4"
                        
                        logger.info(f"Applying AI reframing to segment {i+1}/{len(clips_to_concat)}")
                        
                        # Analyze and reframe the segment
                        analyses = self.ai_reframing.analyze_video_for_reframing(clip_path, sample_rate=5)
                        
                        if analyses:
                            # Get reframing stats for logging
                            stats = self.ai_reframing.get_reframing_stats(analyses)
                            logger.info(f"Segment {i+1} analysis: {stats['subject_detection_rate']:.1%} subject detection, "
                                      f"{stats['average_engagement_score']:.2f} avg engagement")
                            
                            # Apply smart reframing
                            reframe_success = self.ai_reframing.apply_smart_reframing(
                                clip_path,
                                str(reframed_path),
                                analyses
                            )
                            
                            if reframe_success:
                                reframed_clips.append(str(reframed_path))
                                logger.info(f"Successfully reframed segment {i+1}")
                            else:
                                reframed_clips.append(clip_path)  # Use original if reframing fails
                                logger.warning(f"Reframing failed for segment {i+1}, using original")
                        else:
                            # No analysis data, use original
                            reframed_clips.append(clip_path)
                            logger.warning(f"No analysis data for segment {i+1}, using original")
                    
                    except Exception as e:
                        logger.error(f"Error reframing segment {i+1}: {e}")
                        reframed_clips.append(clip_path)  # Use original if error
                
                clips_to_concat = reframed_clips
                update_job_progress(job_id, 55, "AI reframing complete")

            update_job_progress(job_id, 60, "Concatenating videos")

            # Step 4: Concatenate segments (with transitions when requested)
            concat_path = output_dir / "concat.mp4"
            transition_duration = 1.2
            xfade_name = get_xfade_name(transition_name or "crossfade")

            if not self.ffmpeg.concatenate_with_transitions(
                clips_to_concat, str(concat_path), transition_name=xfade_name, transition_duration=transition_duration
            ):
                # Fallback to simple concat if transitions fail
                logger.warning("Transition concat failed, falling back to simple concat")
                if not self.ffmpeg.concatenate_videos(clips_to_concat, str(concat_path)):
                    raise Exception("Failed to concatenate videos")

            # Optionally export an MLT project for manual editing
            if export_mlt:
                try:
                    exporter = MLTExporter()
                    clips = []
                    # Build clip descriptors from cuts_metadata and produced segments
                    for i, cut in enumerate(cuts_metadata):
                        seg_path = (segments_dir / f"segment_{i}.mp4").as_posix()
                        clips.append({"path": seg_path, "transition": {"type": xfade_name, "duration": transition_duration}})
                    exporter.export(clips, str(output_dir / "project.mlt"), title=f"job_{job_id}")
                    logger.info("MLT export written")
                except Exception:
                    logger.exception("Failed to write MLT export")

            # Step 5: Resize skipped (handled in trim_video)
            # We now have a standardized 1080x1920 video at concat_path

            # Step 5.5: Apply Quality Enhancement (if enabled)
            if enable_quality_enhancement:
                update_job_progress(job_id, 75, "Enhancing video quality")
                
                # Check if enhancement is needed
                if self.video_enhancer.is_enhancement_needed(str(concat_path)):
                    enhanced_path = output_dir / "enhanced.mp4"
                    
                    logger.info("Applying AI-powered quality enhancement")
                    enhancement_success = self.video_enhancer.enhance_video_quality(
                        str(concat_path),
                        str(enhanced_path),
                        scale=2  # 2x upscaling
                    )
                    
                    if enhancement_success:
                        transition_path = enhanced_path
                        logger.info("Video quality enhancement completed")
                    else:
                        transition_path = concat_path
                        logger.warning("Quality enhancement failed, using original")
                else:
                    transition_path = concat_path
                    logger.info("Video quality sufficient, skipping enhancement")
            else:
                transition_path = concat_path

            update_job_progress(job_id, 80, "Style processing complete")

            # The `concat_path` already contains video-level transitions (video-only).
            # We'll mix the trimmed audio in the next step.
            transition_path = concat_path

            update_job_progress(job_id, 85, "Mixing audio")

            # Step 7: Mix audio with video (Final Step)
            # Trim audio to user selection
            trimmed_audio = output_dir / "trimmed_audio.mp3"
            if not self.ffmpeg.trim_audio(music_path, str(trimmed_audio), music_start_time, target_duration):
                 logger.warning("Failed to trim audio, using original")
                 trimmed_audio = music_path

            # Output directly to output.mp4
            output_path = output_dir / "output.mp4"
            if not self.ffmpeg.mix_audio(
                str(transition_path), str(trimmed_audio), str(output_path)
            ):
                raise Exception("Failed to mix audio")

            update_job_progress(job_id, 100, "Complete")

            # Mark job as complete
            mark_job_complete(job_id, f"/api/download/{job_id}")


            # Cleanup intermediate files
            self._cleanup_intermediate_files(output_dir)

            # Delete all uploads except output.mp4
            for f in output_dir.iterdir():
                if f.is_file() and f.name != "output.mp4":
                    try:
                        f.unlink()
                    except Exception as e:
                        logger.warning(f"Failed to delete {f}: {e}")

            logger.info(f"Video processing completed for job {job_id}")
            return True

        except Exception as e:
            logger.error(f"Error processing video for job {job_id}: {e}")
            mark_job_failed(job_id, str(e))
            return False

    def _cleanup_intermediate_files(self, output_dir: Path):
        """Remove intermediate files"""
        intermediate_files = [
            "concat.mp4",
            "resized.mp4",
            "transition.mp4",
            "mixed.mp4",
            "concat.txt",
            "trimmed_audio.mp3"
        ]
        for filename in intermediate_files:
            file_path = output_dir / filename
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete {filename}: {e}")
        
        # Clean up segments directory (including styled segments)
        segments_dir = output_dir / "segments"
        if segments_dir.exists():
            try:
                import shutil
                shutil.rmtree(segments_dir)
                logger.info("Cleaned up segments directory")
            except Exception as e:
                logger.warning(f"Failed to delete segments directory: {e}")

    async def process_video_async(
        self,
        job_id: str,
        video_paths: List[str],
        music_path: str,
        style: str,
        output_dir: Path,
    ) -> bool:
        """Process video asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.process_video,
            job_id,
            video_paths,
            music_path,
            style,
            output_dir,
        )
