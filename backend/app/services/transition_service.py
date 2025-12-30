import subprocess
from typing import List, Dict, Optional
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TransitionType(str, Enum):
    # Fades
    FADE = "fade"
    DISSOLVE = "dissolve"
    FADEBLACK = "fadeblack"
    FADEWHITE = "fadewhite"
    FADEGRAYS = "fadegrays"

    # Wipes
    WIPELEFT = "wipeleft"
    WIPERIGHT = "wiperight"
    WIPEUP = "wipeup"
    WIPEDOWN = "wipedown"

    # Slides
    SLIDELEFT = "slideleft"
    SLIDERIGHT = "slideright"
    SLIDEUP = "slideup"
    SLIDEDOWN = "slidedown"

    # Crops
    CIRCLECROP = "circlecrop"
    RECTCROP = "rectcrop"
    RADIAL = "radial"
    PIXELIZE = "pixelize"

    # Advanced
    CIRCLEOPEN = "circleopen"
    CIRCLECLOSE = "circleclose"
    DIAGTL = "diagtl"
    DIAGTR = "diagtr"


class TransitionService:
    """Handles FFmpeg xfade transitions and exposes a small API for routes.

    This implementation focuses on robust input validation and helpful
    errors rather than trying to support every corner-case of FFmpeg.
    """

    DESCRIPTIONS = {
        "fade": "Simple fade",
        "dissolve": "Cross-dissolve",
        "fadeblack": "Fade through black",
        "wipeleft": "Wipe from right to left",
        "wiperight": "Wipe from left to right",
        "slideleft": "Slide in from right",
        "slideright": "Slide in from left",
        "circlecrop": "Circular crop transition",
        "circleopen": "Circle opening",
        "pixelize": "Pixelate effect",
    }

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or (Path.cwd() / "tmp_outputs"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _get_video_duration(video_path: str) -> float:
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1:nokey=1",
                str(video_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout:
                return float(result.stdout.strip())
        except Exception as e:
            logger.debug(f"_get_video_duration error: {e}")
        return 5.0

    def get_all_transitions(self) -> Dict[str, Dict[str, str]]:
        transitions = {}
        for t in TransitionType:
            transitions[t.value] = {
                "name": t.value,
                "description": self.DESCRIPTIONS.get(t.value, f"{t.value} transition"),
            }
        return transitions

    def apply_transition(
        self,
        video1_path: str,
        video2_path: str,
        transition: TransitionType = TransitionType.DISSOLVE,
        duration: float = 1.0,
        offset: Optional[float] = None,
        output_name: str = "transition_output.mp4",
        preset: str = "fast",
    ) -> str:
        if not Path(video1_path).exists():
            raise ValueError(f"Video 1 not found: {video1_path}")
        if not Path(video2_path).exists():
            raise ValueError(f"Video 2 not found: {video2_path}")
        if duration < 0.5 or duration > 5.0:
            raise ValueError("Duration must be between 0.5 and 5.0 seconds")

        if offset is None:
            v1_duration = self._get_video_duration(video1_path)
            offset = max(0, v1_duration - duration)

        output_path = self.output_dir / output_name

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(video1_path),
            "-i",
            str(video2_path),
            "-filter_complex",
            f"xfade=transition={transition.value}:duration={duration}:offset={offset}",
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(output_path),
        ]

        logger.info(f"Applying transition {transition.value} between {video1_path} and {video2_path}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            raise Exception(f"FFmpeg error: {result.stderr}")

        return str(output_path)

    def apply_multiple_transitions(
        self,
        video_paths: List[str],
        transitions: List[Dict],
        output_name: str = "multi_transition_output.mp4",
        preset: str = "fast",
    ) -> str:
        if len(transitions) != len(video_paths) - 1:
            raise ValueError(f"Need {len(video_paths) - 1} transitions for {len(video_paths)} videos")

        for i, p in enumerate(video_paths):
            if not Path(p).exists():
                raise ValueError(f"Video {i} not found: {p}")

        filter_parts = []
        for i in range(len(video_paths) - 1):
            trans_config = transitions[i]
            trans_type = trans_config.get("type", "dissolve")
            duration = trans_config.get("duration", 1.0)
            if "offset" in trans_config:
                offset = trans_config["offset"]
            else:
                v1_duration = self._get_video_duration(video_paths[i])
                offset = max(0, v1_duration - duration)

            filter_parts.append(
                f"[{i}:v][{i+1}:v]xfade=transition={trans_type}:duration={duration}:offset={offset}[v{i}]"
            )

        filter_parts.append(f"[v{len(video_paths) - 2}]format=yuv420p[out]")
        complex_filter = ";".join(filter_parts)

        inputs = []
        for video_path in video_paths:
            inputs.extend(["-i", str(video_path)])

        output_path = self.output_dir / output_name

        cmd = [
            "ffmpeg",
            "-y",
            *inputs,
            "-filter_complex",
            complex_filter,
            "-map",
            "[out]",
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(output_path),
        ]

        logger.info(f"Applying {len(transitions)} transitions")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            raise Exception(f"FFmpeg error: {result.stderr}")

        return str(output_path)
