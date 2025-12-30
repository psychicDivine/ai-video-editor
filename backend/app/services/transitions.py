"""Transition registry and helpers for FFmpeg-based transitions.

This module defines a small registry of named transitions and the
corresponding FFmpeg `xfade` transition names. It is intentionally
minimal so we can extend it later with frei0r/OpenFX mappings.
"""

from typing import Dict

# Map a friendly name -> ffmpeg xfade transition name
TRANSITION_REGISTRY: Dict[str, Dict[str, str]] = {
    "crossfade": {"backend": "ffmpeg", "xfade": "fade"},
    "fade": {"backend": "ffmpeg", "xfade": "fade"},
    "slideleft": {"backend": "ffmpeg", "xfade": "slideleft"},
    "slideright": {"backend": "ffmpeg", "xfade": "slideright"},
    "slidetop": {"backend": "ffmpeg", "xfade": "slidetop"},
    "slidebottom": {"backend": "ffmpeg", "xfade": "slidebottom"},
    "wipeleft": {"backend": "ffmpeg", "xfade": "wipeleft"},
    "wiperight": {"backend": "ffmpeg", "xfade": "wiperight"},
}

DEFAULT_TRANSITION = "crossfade"

def get_xfade_name(name: str) -> str:
    """Return the FFmpeg `xfade` name for a friendly transition name.

    Falls back to the default if the requested name is not known.
    """
    entry = TRANSITION_REGISTRY.get(name)
    if entry and entry.get("backend") == "ffmpeg":
        return entry.get("xfade", TRANSITION_REGISTRY[DEFAULT_TRANSITION]["xfade"])
    return TRANSITION_REGISTRY[DEFAULT_TRANSITION]["xfade"]
