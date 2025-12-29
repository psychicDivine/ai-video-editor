import asyncio
from pathlib import Path
from typing import List, Optional
import logging

from app.services.ffmpeg_handler import FFmpegHandler
from app.services.ai_director import AIDirector
from app.routes.jobs import update_job_progress, mark_job_complete, mark_job_failed

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Orchestrate video processing pipeline"""

    def __init__(self):
        self.ffmpeg = FFmpegHandler()
        self.ai_director = AIDirector()

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

            update_job_progress(job_id, 50, "Concatenating videos")

            # Step 4: Concatenate segments
            concat_path = output_dir / "concat.mp4"
            if not self.ffmpeg.concatenate_videos(clips_to_concat, str(concat_path)):
                raise Exception("Failed to concatenate videos")

            # Step 5: Resize skipped (handled in trim_video)
            # We now have a standardized 1080x1920 video at concat_path

            update_job_progress(job_id, 70, "Applying transitions")

            # Step 6: Apply fade transitions
            transition_path = output_dir / "transition.mp4"
            if not self.ffmpeg.apply_fade_transition(
                str(concat_path), str(transition_path), fade_duration=0.5
            ):
                raise Exception("Failed to apply transitions")

            update_job_progress(job_id, 80, "Mixing audio")

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
            import shutil
            if segments_dir.exists():
                shutil.rmtree(segments_dir)

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
