"""
Effects Service - Visual effects for EditPlan clips
Supports: slowmo, speedup, speedramp, freeze, zoomPunch, kenburns, flashWhite, shake, vignette
"""
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
import logging
import tempfile
import shutil

logger = logging.getLogger(__name__)


class EffectType(str, Enum):
    """Available video effects"""
    SLOWMO = "slowmo"
    SPEEDUP = "speedup"
    SPEEDRAMP = "speedramp"
    FREEZE = "freeze"
    ZOOM_PUNCH = "zoomPunch"
    KENBURNS = "kenburns"
    FLASH_WHITE = "flashWhite"
    SHAKE = "shake"
    VIGNETTE = "vignette"
    COLOR_PULSE = "colorPulse"


# Effect metadata for UI/AI selection
EFFECT_CATALOG = {
    "slowmo": {
        "name": "Slow Motion",
        "description": "Slow down clip for dramatic effect",
        "params": {"speed": {"type": "float", "min": 0.25, "max": 0.75, "default": 0.5}},
        "energy": "low",
        "use_case": "Dramatic moments, reveals, impacts"
    },
    "speedup": {
        "name": "Speed Up",
        "description": "Speed up clip for energy",
        "params": {"speed": {"type": "float", "min": 1.5, "max": 4.0, "default": 2.0}},
        "energy": "high",
        "use_case": "Transitions, montages, filler reduction"
    },
    "speedramp": {
        "name": "Speed Ramp",
        "description": "Smooth speed transition within clip",
        "params": {
            "start_speed": {"type": "float", "min": 0.25, "max": 2.0, "default": 1.0},
            "end_speed": {"type": "float", "min": 0.25, "max": 2.0, "default": 0.5}
        },
        "energy": "medium",
        "use_case": "Action sequences, reveals"
    },
    "freeze": {
        "name": "Freeze Frame",
        "description": "Pause on specific frame",
        "params": {"duration": {"type": "float", "min": 0.5, "max": 3.0, "default": 1.0}},
        "energy": "low",
        "use_case": "Emphasis, text overlay moments"
    },
    "zoomPunch": {
        "name": "Zoom Punch",
        "description": "Quick zoom hit on beat",
        "params": {
            "intensity": {"type": "float", "min": 0.05, "max": 0.3, "default": 0.15},
            "duration": {"type": "float", "min": 0.1, "max": 0.5, "default": 0.2}
        },
        "energy": "high",
        "use_case": "Beat hits, emphasis, impacts"
    },
    "kenburns": {
        "name": "Ken Burns",
        "description": "Slow zoom/pan effect",
        "params": {
            "start_scale": {"type": "float", "min": 1.0, "max": 1.3, "default": 1.0},
            "end_scale": {"type": "float", "min": 1.0, "max": 1.3, "default": 1.15},
            "direction": {"type": "string", "options": ["in", "out"], "default": "in"}
        },
        "energy": "low",
        "use_case": "B-roll, establishing shots, photos"
    },
    "flashWhite": {
        "name": "Flash White",
        "description": "White flash transition effect",
        "params": {
            "duration": {"type": "float", "min": 0.1, "max": 0.5, "default": 0.2},
            "intensity": {"type": "float", "min": 0.5, "max": 1.0, "default": 0.8}
        },
        "energy": "high",
        "use_case": "Cut transitions, beat hits"
    },
    "shake": {
        "name": "Camera Shake",
        "description": "Add camera shake effect",
        "params": {
            "intensity": {"type": "float", "min": 2, "max": 15, "default": 5},
            "frequency": {"type": "float", "min": 10, "max": 30, "default": 20}
        },
        "energy": "high",
        "use_case": "Action, impacts, energy"
    },
    "vignette": {
        "name": "Vignette",
        "description": "Dark edges for cinematic look",
        "params": {"intensity": {"type": "float", "min": 0.1, "max": 0.5, "default": 0.3}},
        "energy": "low",
        "use_case": "Cinematic mood, focus attention"
    },
    "colorPulse": {
        "name": "Color Pulse",
        "description": "Saturation pulse on beat",
        "params": {
            "intensity": {"type": "float", "min": 0.1, "max": 0.5, "default": 0.2},
            "duration": {"type": "float", "min": 0.1, "max": 0.5, "default": 0.15}
        },
        "energy": "medium",
        "use_case": "Beat sync, music videos"
    }
}


class EffectsService:
    """Apply visual effects to video clips using FFmpeg"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_cmd = ffmpeg_path
        # Use matching ffprobe if available; fall back to PATH discovery
        self.ffprobe_cmd = shutil.which("ffprobe") or "ffprobe"

    def _get_duration_seconds(self, input_path: str) -> Optional[float]:
        """Return clip duration in seconds using ffprobe (fallback None on error)."""
        try:
            cmd = [
                self.ffprobe_cmd,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                input_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception:
            logger.warning("Could not probe duration for %s", input_path)
            return None

    def _has_audio_stream(self, input_path: str) -> bool:
        """Check if the input has an audio stream (used to avoid filter errors)."""
        try:
            cmd = [
                self.ffprobe_cmd,
                "-v",
                "error",
                "-select_streams",
                "a",
                "-show_entries",
                "stream=index",
                "-of",
                "csv=p=0",
                input_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return bool(result.stdout.strip())
        except Exception:
            logger.warning("Could not probe audio stream for %s", input_path)
            return False

    def apply_effect(
        self,
        input_path: str,
        output_path: str,
        effect_type: str,
        params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Apply a single effect to a video clip.
        
        Args:
            input_path: Path to input video
            output_path: Path to output video
            effect_type: Effect name from EffectType enum
            params: Effect parameters (uses defaults if not provided)
        
        Returns:
            True if successful, False otherwise
        """
        params = params or {}
        
        effect_handlers = {
            "slowmo": self._apply_slowmo,
            "speedup": self._apply_speedup,
            "speedramp": self._apply_speedramp,
            "freeze": self._apply_freeze,
            "zoomPunch": self._apply_zoom_punch,
            "kenburns": self._apply_kenburns,
            "flashWhite": self._apply_flash_white,
            "shake": self._apply_shake,
            "vignette": self._apply_vignette,
            "colorPulse": self._apply_color_pulse,
        }
        
        handler = effect_handlers.get(effect_type)
        if not handler:
            logger.error(f"Unknown effect type: {effect_type}")
            return False
        
        try:
            return handler(input_path, output_path, params)
        except Exception as e:
            logger.exception(f"Error applying {effect_type} effect: {e}")
            return False

    def apply_multiple_effects(
        self,
        input_path: str,
        output_path: str,
        effects: List[Dict[str, Any]]
    ) -> bool:
        """
        Apply multiple effects in sequence.
        
        Args:
            input_path: Path to input video
            output_path: Path to final output
            effects: List of {"type": "effectName", "params": {...}}
        
        Returns:
            True if all effects applied successfully
        """
        if not effects:
            shutil.copy(input_path, output_path)
            return True
        
        current_input = input_path
        temp_files = []
        
        try:
            for i, effect in enumerate(effects):
                is_last = (i == len(effects) - 1)
                if is_last:
                    current_output = output_path
                else:
                    # Create temp file for intermediate output
                    temp_file = tempfile.NamedTemporaryFile(
                        suffix=".mp4", delete=False
                    )
                    current_output = temp_file.name
                    temp_files.append(current_output)
                    temp_file.close()
                
                success = self.apply_effect(
                    current_input,
                    current_output,
                    effect.get("type"),
                    effect.get("params", {})
                )
                
                if not success:
                    logger.error(f"Failed to apply effect {effect.get('type')}")
                    return False
                
                current_input = current_output
            
            return True
        finally:
            # Cleanup temp files
            for temp_file in temp_files:
                try:
                    Path(temp_file).unlink(missing_ok=True)
                except:
                    pass

    def _apply_slowmo(self, input_path: str, output_path: str, params: Dict) -> bool:
        """Apply slow motion effect"""
        speed = params.get("speed", 0.5)
        # setpts increases presentation timestamps, atempo slows audio
        # For speed < 1, we need multiple atempo filters (each 0.5-2.0 range)
        
        video_filter = f"setpts={1/speed}*PTS"
        
        # Build audio filter chain for slow speeds
        audio_filters = []
        remaining_speed = speed
        while remaining_speed < 0.5:
            audio_filters.append("atempo=0.5")
            remaining_speed *= 2
        if remaining_speed != 1.0:
            audio_filters.append(f"atempo={remaining_speed}")
        
        audio_filter = ",".join(audio_filters) if audio_filters else f"atempo={speed}"

        has_audio = self._has_audio_stream(input_path)

        if has_audio:
            cmd = [
                self.ffmpeg_cmd, "-y", "-i", input_path,
                "-filter_complex", f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "192k",
                output_path
            ]
        else:
            # No audio stream: apply video-only slowmo and keep output silent
            cmd = [
                self.ffmpeg_cmd, "-y", "-i", input_path,
                "-vf", video_filter,
                "-an",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                output_path
            ]
        
        return self._run_ffmpeg(cmd, "slowmo")

    def _apply_speedup(self, input_path: str, output_path: str, params: Dict) -> bool:
        """Apply speed up effect"""
        speed = params.get("speed", 2.0)
        
        video_filter = f"setpts={1/speed}*PTS"
        
        # Build audio filter chain for fast speeds
        audio_filters = []
        remaining_speed = speed
        while remaining_speed > 2.0:
            audio_filters.append("atempo=2.0")
            remaining_speed /= 2
        if remaining_speed != 1.0:
            audio_filters.append(f"atempo={remaining_speed}")
        
        audio_filter = ",".join(audio_filters) if audio_filters else f"atempo={speed}"
        
        cmd = [
            self.ffmpeg_cmd, "-y", "-i", input_path,
            "-filter_complex", f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            output_path
        ]
        
        return self._run_ffmpeg(cmd, "speedup")

    def _apply_speedramp(self, input_path: str, output_path: str, params: Dict) -> bool:
        """Apply speed ramp (smooth speed change)"""
        start_speed = params.get("start_speed", 1.0)
        end_speed = params.get("end_speed", 0.5)
        duration = self._get_duration_seconds(input_path) or 5.0
        
        # Use ffmpeg's setpts with variable expression
        # This creates a smooth transition from start to end speed
        # t = time in seconds, we ramp linearly
        ramp_expr = f"setpts=PTS/({start_speed}+({end_speed}-{start_speed})*T/{duration})"
        # Audio ramping is non-trivial; keep video-only for now
        
        cmd = [
            self.ffmpeg_cmd, "-y", "-i", input_path,
            "-vf", ramp_expr,
            "-an",  # Speed ramp on audio is complex, drop it
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            output_path
        ]
        
        return self._run_ffmpeg(cmd, "speedramp")

    def _apply_freeze(self, input_path: str, output_path: str, params: Dict) -> bool:
        """Apply freeze frame at end of clip"""
        duration = params.get("duration", 1.0)
        
        # Get last frame and loop it
        cmd = [
            self.ffmpeg_cmd, "-y",
            "-i", input_path,
            "-filter_complex",
            f"[0:v]split[main][freeze];[freeze]trim=end_frame=1,loop=loop={int(duration*30)}:size=1,setpts=N/30/TB[frozen];[main][frozen]concat=n=2:v=1:a=0[v]",
            "-map", "[v]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-an",
            output_path
        ]
        
        return self._run_ffmpeg(cmd, "freeze")

    def _apply_zoom_punch(self, input_path: str, output_path: str, params: Dict) -> bool:
        """Apply quick zoom punch effect"""
        intensity = params.get("intensity", 0.15)
        duration = params.get("duration", 0.2)
        
        # Calculate zoom parameters
        max_zoom = 1 + intensity  # e.g., 1.15
        frames = int(duration * 30)  # Assuming 30fps
        
        # Zoom in quickly, zoom out quickly
        # zoompan filter: z (zoom), d (duration frames), x/y (position)
        zoom_filter = (
            f"zoompan=z='if(lt(on,{frames}),min(zoom+{intensity/frames},{max_zoom}),"
            f"max(zoom-{intensity/frames},1))':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920"
        )
        
        cmd = [
            self.ffmpeg_cmd, "-y", "-i", input_path,
            "-vf", zoom_filter,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy",
            output_path
        ]
        
        return self._run_ffmpeg(cmd, "zoomPunch")

    def _apply_kenburns(self, input_path: str, output_path: str, params: Dict) -> bool:
        """Apply Ken Burns (slow zoom/pan) effect"""
        start_scale = params.get("start_scale", 1.0)
        end_scale = params.get("end_scale", 1.15)
        direction = params.get("direction", "in")
        duration = self._get_duration_seconds(input_path) or 5.0
        total_frames = max(1, int(duration * 30))
        
        if direction == "out":
            start_scale, end_scale = end_scale, start_scale
        
        # Smooth zoom over entire clip duration
        zoom_filter = (
            f"zoompan=z='min({start_scale}+({end_scale}-{start_scale})*on/{total_frames},{end_scale})':"
            f"d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"
        )
        
        cmd = [
            self.ffmpeg_cmd, "-y", "-i", input_path,
            "-vf", zoom_filter,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy",
            output_path
        ]
        
        return self._run_ffmpeg(cmd, "kenburns")

    def _apply_flash_white(self, input_path: str, output_path: str, params: Dict) -> bool:
        """Apply white flash at start of clip"""
        duration = params.get("duration", 0.2)
        intensity = params.get("intensity", 0.8)
        
        # Fade from white at start
        flash_filter = (
            f"fade=type=in:duration={duration}:color=white,"
            f"eq=brightness={intensity}:enable='lt(t,{duration/2})'"
        )
        
        cmd = [
            self.ffmpeg_cmd, "-y", "-i", input_path,
            "-vf", flash_filter,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy",
            output_path
        ]
        
        return self._run_ffmpeg(cmd, "flashWhite")

    def _apply_shake(self, input_path: str, output_path: str, params: Dict) -> bool:
        """Apply camera shake effect"""
        intensity = params.get("intensity", 5)
        frequency = params.get("frequency", 20)
        
        # Use ffmpeg's crop with random offsets simulated via expressions
        shake_filter = (
            f"crop=in_w-{intensity*2}:in_h-{intensity*2}:"
            f"'{intensity}+{intensity}*sin({frequency}*t)':"
            f"'{intensity}+{intensity}*cos({frequency}*t*1.1)',"
            f"scale=1080:1920"
        )
        
        cmd = [
            self.ffmpeg_cmd, "-y", "-i", input_path,
            "-vf", shake_filter,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy",
            output_path
        ]
        
        return self._run_ffmpeg(cmd, "shake")

    def _apply_vignette(self, input_path: str, output_path: str, params: Dict) -> bool:
        """Apply vignette (dark edges) effect"""
        intensity = params.get("intensity", 0.3)
        
        # FFmpeg vignette filter: angle controls falloff, aspect for shape
        vignette_filter = f"vignette=angle={intensity}:mode=forward"
        
        cmd = [
            self.ffmpeg_cmd, "-y", "-i", input_path,
            "-vf", vignette_filter,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy",
            output_path
        ]
        
        return self._run_ffmpeg(cmd, "vignette")

    def _apply_color_pulse(self, input_path: str, output_path: str, params: Dict) -> bool:
        """Apply saturation pulse effect"""
        intensity = params.get("intensity", 0.2)
        duration = params.get("duration", 0.15)
        
        # Increase saturation briefly at start
        pulse_filter = (
            f"eq=saturation='1+{intensity}*exp(-t/{duration})'"
        )
        
        cmd = [
            self.ffmpeg_cmd, "-y", "-i", input_path,
            "-vf", pulse_filter,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy",
            output_path
        ]
        
        return self._run_ffmpeg(cmd, "colorPulse")

    def _run_ffmpeg(self, cmd: List[str], effect_name: str) -> bool:
        """Execute FFmpeg command with error handling"""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True
            )
            logger.info(f"Applied {effect_name} effect successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg {effect_name} failed: {e.stderr}")
            return False

    @staticmethod
    def get_effect_catalog() -> Dict:
        """Return available effects with metadata for UI/AI selection."""
        return EFFECT_CATALOG
    
    @staticmethod
    def get_effects_for_energy(energy_level: str) -> List[str]:
        """Get effects suitable for a given energy level (low/medium/high)."""
        return [
            name for name, meta in EFFECT_CATALOG.items()
            if meta.get("energy") == energy_level
        ]
    
    @staticmethod
    def get_default_params(effect_type: str) -> Dict[str, Any]:
        """Get default parameters for an effect."""
        effect = EFFECT_CATALOG.get(effect_type, {})
        params = effect.get("params", {})
        return {
            key: spec.get("default") 
            for key, spec in params.items()
        }
