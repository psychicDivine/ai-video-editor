"""
PlanRenderer - Executes an EditPlan to produce final video output
"""
import logging
import tempfile
from pathlib import Path
from typing import Optional
from uuid import UUID
import shutil

from app.schemas.edit_plan import EditPlan, EditClip, AudioTrack
from app.services.ffmpeg_handler import FFmpegHandler
from app.services.effects import EffectsService
from app.services.style_editor import StyleEditor
from app.config import get_settings

logger = logging.getLogger(__name__)


class PlanRenderer:
    """
    Renders an EditPlan into a final video.
    
    Pipeline:
    1. Prepare clips (trim from source, apply effects)
    2. Apply style color grading
    3. Concatenate with transitions
    4. Mix audio
    5. Final encode
    """
    
    def __init__(self):
        settings = get_settings()
        self.ffmpeg = FFmpegHandler()
        self.effects = EffectsService()
        self.style_editor = StyleEditor()
        self.output_dir = Path(settings.upload_folder) / "outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def render(
        self,
        plan: EditPlan,
        quality: str = "high",
        output_path: Optional[str] = None
    ) -> str:
        """
        Render the complete edit plan to a video file.
        
        Args:
            plan: The EditPlan to render
            quality: "draft" (fast), "medium", or "high" (slow, best quality)
            output_path: Optional custom output path
        
        Returns:
            Path to the rendered video
        """
        logger.info(f"Starting render for plan {plan.id} with {len(plan.clips)} clips")
        
        # Quality presets
        presets = {
            "draft": {"preset": "ultrafast", "crf": 28},
            "medium": {"preset": "medium", "crf": 23},
            "high": {"preset": "slow", "crf": 18}
        }
        preset_config = presets.get(quality, presets["high"])
        
        # Create temp directory for intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Step 1: Prepare clips (trim + effects)
            logger.info("Step 1: Preparing clips...")
            prepared_clips = await self._prepare_clips(plan.clips, temp_path)
            
            if not prepared_clips:
                raise ValueError("No clips prepared for rendering")
            
            # Step 2: Apply style color grading
            logger.info(f"Step 2: Applying style '{plan.style}'...")
            styled_clips = await self._apply_style(prepared_clips, plan.style, temp_path)
            
            # Step 3: Concatenate with transitions
            logger.info("Step 3: Concatenating with transitions...")
            concat_path = temp_path / "concat.mp4"
            
            # Build clip dicts for per-clip transitions
            clip_dicts = []
            for i, (clip, styled_path) in enumerate(zip(plan.clips, styled_clips)):
                clip_dicts.append({
                    "path": styled_path,
                    "transition_in": clip.transition_in if i > 0 else None,
                    "transition_in_duration": clip.transition_in_duration if i > 0 else 0.5
                })
            
            success = self.ffmpeg.concatenate_with_per_clip_transitions(
                clips=clip_dicts,
                output_path=str(concat_path),
                include_audio=False  # We'll mix audio separately
            )
            
            if not success:
                # Fallback to simple concat
                logger.warning("Per-clip transitions failed, using simple concat")
                success = self.ffmpeg.concatenate_videos(
                    styled_clips, str(concat_path)
                )
                if not success:
                    raise RuntimeError("Failed to concatenate clips")
            
            # Step 4: Mix audio
            logger.info("Step 4: Mixing audio...")
            audio_path = plan.audio.source_path
            mixed_path = temp_path / "mixed.mp4"
            
            # Trim audio to match video duration
            video_info = self.ffmpeg.get_video_info(str(concat_path))
            video_duration = video_info.get("duration", plan.total_duration)
            
            trimmed_audio = temp_path / "audio_trimmed.aac"
            self.ffmpeg.trim_audio(audio_path, str(trimmed_audio), 0, video_duration)
            
            success = self.ffmpeg.mix_audio(
                str(concat_path),
                str(trimmed_audio),
                str(mixed_path)
            )
            
            if not success:
                logger.warning("Audio mix failed, using video without music")
                mixed_path = concat_path
            
            # Step 5: Final encode
            logger.info("Step 5: Final encode...")
            if output_path is None:
                output_path = str(self.output_dir / f"{plan.job_id}_output.mp4")
            
            success = self.ffmpeg.render_final_video(
                str(mixed_path),
                output_path,
                preset=preset_config["preset"]
            )
            
            if not success:
                # Just copy the mixed file
                shutil.copy(str(mixed_path), output_path)
            
            logger.info(f"Render complete: {output_path}")
            return output_path
    
    async def _prepare_clips(
        self,
        clips: list[EditClip],
        temp_dir: Path
    ) -> list[str]:
        """
        Prepare each clip: trim from source and apply effects.
        """
        prepared = []
        
        for i, clip in enumerate(clips):
            clip_output = temp_dir / f"clip_{i:03d}.mp4"
            
            # Trim from source
            duration = clip.end_time - clip.start_time
            success = self.ffmpeg.trim_video(
                input_path=clip.source_path,
                output_path=str(clip_output),
                start_time=clip.start_time,
                duration=duration,
                width=1080,
                height=1920
            )
            
            if not success:
                logger.error(f"Failed to trim clip {i} from {clip.source_path}")
                continue
            
            # Apply effects if any
            if clip.effects:
                effects_output = temp_dir / f"clip_{i:03d}_fx.mp4"
                effects_list = [{"type": e.type, "params": e.params} for e in clip.effects]
                
                success = self.effects.apply_multiple_effects(
                    str(clip_output),
                    str(effects_output),
                    effects_list
                )
                
                if success:
                    clip_output = effects_output
                else:
                    logger.warning(f"Effects failed for clip {i}, using original")
            
            prepared.append(str(clip_output))
        
        return prepared
    
    async def _apply_style(
        self,
        clip_paths: list[str],
        style: str,
        temp_dir: Path
    ) -> list[str]:
        """
        Apply style color grading to all clips.
        """
        styled = []
        
        for i, clip_path in enumerate(clip_paths):
            styled_output = temp_dir / f"styled_{i:03d}.mp4"
            
            success = self.style_editor.apply_style(
                clip_path,
                str(styled_output),
                style
            )
            
            if success:
                styled.append(str(styled_output))
            else:
                # Use original if style fails
                logger.warning(f"Style application failed for clip {i}")
                styled.append(clip_path)
        
        return styled
    
    async def render_preview(
        self,
        plan: EditPlan,
        start_time: float = 0,
        duration: float = 5
    ) -> str:
        """
        Render a quick preview of a portion of the plan.
        Useful for UI preview without full render.
        """
        # Find clips that fall within the preview window
        preview_clips = []
        for clip in plan.clips:
            clip_start = clip.timeline_position
            clip_end = clip_start + (clip.end_time - clip.start_time)
            
            if clip_end > start_time and clip_start < (start_time + duration):
                preview_clips.append(clip)
        
        if not preview_clips:
            raise ValueError("No clips in preview range")
        
        # Create a mini plan for preview
        from copy import deepcopy
        preview_plan = deepcopy(plan)
        preview_plan.clips = preview_clips
        preview_plan.total_duration = duration
        
        # Render with draft quality
        return await self.render(preview_plan, quality="draft")
