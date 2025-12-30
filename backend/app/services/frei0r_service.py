"""Simple frei0r detection and presets helper.

Provides:
- `is_frei0r_available()` to detect if FFmpeg exposes frei0r filters
- `apply_frei0r_filter()` to apply a frei0r filter via FFmpeg
- `FREI0R_PRESETS` dictionary with a few common presets
"""

import subprocess
from pathlib import Path
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


FREI0R_PRESETS: Dict[str, Dict] = {
    "pixelize_small": {"filter": "pixelize", "params": "0.03"},
    "pixelize_large": {"filter": "pixelize", "params": "0.15"},
    "blur_light": {"filter": "blur", "params": "1.0"},
    "hsv_shift": {"filter": "hsvshift", "params": "0.1|0.2|0.1"},
}


def is_frei0r_available() -> bool:
    """Return True if FFmpeg lists frei0r filter support."""
    try:
        result = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True, timeout=5)
        out = (result.stdout or "") + (result.stderr or "")
        return "frei0r" in out
    except Exception as e:
        logger.debug(f"frei0r detection failed: {e}")
        return False


def apply_frei0r_filter(input_path: str, output_path: str, frei0r_name: str, params: Optional[str] = None) -> bool:
    """Apply a frei0r filter via FFmpeg; returns True on success."""
    if not Path(input_path).exists():
        logger.error("Input not found for frei0r filter")
        return False

    if not is_frei0r_available():
        logger.error("frei0r not available in FFmpeg on this system")
        return False

    vf = f"frei0r={frei0r_name}"
    if params:
        vf = f"{vf}:{params}"

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        str(output_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            logger.error(f"frei0r ffmpeg error: {result.stderr}")
            return False
        return True
    except Exception as e:
        logger.error(f"frei0r apply failed: {e}")
        return False
