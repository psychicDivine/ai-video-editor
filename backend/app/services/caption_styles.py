
"""
Caption Style Definitions
Defines the visual appearance of captions for different themes.
"""

CAPTION_STYLES = {
    "classic": {
        "name": "Classic",
        "description": "Clean white text with black outline",
        "font": "Arial",
        "fontsize": 70,
        "primary_color": "&H00FFFFFF",  # White
        "outline_color": "&H00000000",  # Black
        "back_color": "&H64000000",     # Semi-transparent shadow
        "bold": -1,
        "border_style": 1,
        "outline": 3,
        "shadow": 0,
        "alignment": 2,                  # Bottom Center
        "margin_v": 250,
        "animation": "none"
    },
    "tiktok": {
        "name": "TikTok Viral",
        "description": "Bold with yellow highlight and pop animation",
        "font": "Montserrat", # Fallback to Arial if not present
        "fontsize": 65,
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0000FFFF", # Yellow in ASS (BBGGRR) -> 00FFFF is Yellow
        "outline_color": "&H00000000",
        "back_color": "&H64000000",
        "bold": -1,
        "border_style": 1,
        "outline": 4,
        "shadow": 0,
        "alignment": 2,
        "margin_v": 400,
        "animation": "pop"
    },
    "hormozi": {
        "name": "Hormozi",
        "description": "Impactful top-positioned uppercase text",
        "font": "Impact",  # Fallback: Arial Black
        "fontsize": 80,
        "primary_color": "&H00FFFFFF",   # White
        "highlight_color": "&H0000FF00", # Greenish highlight
        "outline_color": "&H00000000",
        "back_color": "&H00000000",
        "bold": -1,
        "border_style": 1,
        "outline": 5,
        "shadow": 0,
        "alignment": 6,                  # Top Center
        "margin_v": 150,
        "animation": "none"
    },
    "neon": {
        "name": "Neon",
        "description": "Glowing text with electric colors",
        "font": "Arial",
        "fontsize": 60,
        "primary_color": "&H00FF00FF",   # Magenta
        "outline_color": "&H00FFFF00",   # Cyan
        "back_color": "&H00000000",
        "bold": -1,
        "border_style": 1,
        "outline": 2,
        "shadow": 0,
        "alignment": 2,
        "margin_v": 400,
        "animation": "typewriter"
    }
}

def get_style(style_name: str) -> dict:
    """Get style definition by name, defaulting to classic."""
    return CAPTION_STYLES.get(style_name.lower(), CAPTION_STYLES["classic"])
