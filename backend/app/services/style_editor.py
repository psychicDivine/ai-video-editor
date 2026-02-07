"""
Style Editor Service - Applies style-specific effects and color grading to videos
"""
from pathlib import Path
from typing import Dict, List, Optional
import logging
import subprocess

logger = logging.getLogger(__name__)


class StyleEditor:
    """Handles style-specific video processing and color grading"""
    
    # Style configurations synced with frontend StyleSelector.tsx
    # These IDs must match exactly with frontend style IDs
    STYLE_CONFIGS = {
        "cinematic_drama": {
            "color_temperature": 5600,  # Cool tones
            "saturation": 0.9,  # Slightly desaturated
            "contrast": 1.1,
            "brightness": 0.95,
            "gamma": 1.05,
            "description": "Professional, dramatic, moody",
            "ai_prompt": """
Create a dramatic, emotionally impactful edit.
PACING: Slower, deliberate cuts (4-6 seconds per clip)
EFFECTS: Use slowmo on emotional peaks, subtle zoom on faces
TRANSITIONS: Prefer crossfade and dissolve for smooth flow
COLOR: Desaturated, cool tones, high contrast, add vignette
RHYTHM: Build tension, peak at 70%, gentle resolution
BEATS: Cut on every 2nd or 4th beat, not every beat
MOOD: Cinematic, thoughtful, powerful
            """.strip()
        },
        "energetic_dance": {
            "color_temperature": 2700,  # Warm tones
            "saturation": 1.2,  # +20% saturation
            "contrast": 1.15,
            "brightness": 1.05,
            "gamma": 0.95,
            "description": "Energetic, confident, fast-paced",
            "ai_prompt": """
Create high-energy, beat-synced edit for maximum engagement.
PACING: Fast cuts (1-2 seconds), cut ON strong beats
EFFECTS: Speed ramps (slow before beat, fast after), zoom punch on drops
TRANSITIONS: Whip, slide, quick cuts - avoid slow fades
COLOR: Vibrant, saturated, high contrast, flash white on impacts
RHYTHM: Constant energy, peak drops with zoom + flash
BEATS: Cut on EVERY strong beat, sync perfectly
MOOD: Energetic, hype, dynamic
            """.strip()
        },
        "luxe_travel": {
            "color_temperature": 3200,  # Warm golden
            "saturation": 1.1,
            "contrast": 1.05,
            "brightness": 1.02,
            "gamma": 1.0,
            "description": "Wanderlust, luxury, peaceful",
            "ai_prompt": """
Create aspirational, smooth travel content.
PACING: Medium cuts (3-4 seconds), flowing movement
EFFECTS: Ken Burns zoom, subtle speed adjustments, gentle motion
TRANSITIONS: Smooth slides, elegant dissolves
COLOR: Warm golden tones, lifted shadows, soft contrast
RHYTHM: Relaxed flow, showcase scenery
BEATS: Loose beat sync, prioritize visual flow over strict timing
MOOD: Dreamy, aspirational, serene
            """.strip()
        },
        "modern_minimal": {
            "color_temperature": 4500,  # Neutral
            "saturation": 0.95,
            "contrast": 1.0,
            "brightness": 1.0,
            "gamma": 1.0,
            "description": "Clean, professional, modern",
            "ai_prompt": """
Create clean, professional content.
PACING: Balanced cuts (2-3 seconds)
EFFECTS: Minimal - clean cuts preferred, subtle zoom only
TRANSITIONS: Simple cuts or short crossfades
COLOR: Neutral, clean whites, subtle contrast
RHYTHM: Steady, predictable, professional
BEATS: Moderate beat sync, not aggressive
MOOD: Professional, polished, trustworthy
            """.strip()
        },
        "viral_tiktok": {
            "color_temperature": 4000,  # Slightly warm
            "saturation": 1.3,  # High saturation
            "contrast": 1.2,
            "brightness": 1.05,
            "gamma": 0.95,
            "description": "Attention-grabbing, trend-optimized",
            "ai_prompt": """
Create attention-grabbing, trend-optimized content.
PACING: Very fast (0.5-1.5 seconds), hook in first 1 second
EFFECTS: Freeze frames, speed ramps, zoom punch, shake on impacts
TRANSITIONS: Whip, glitch, quick slides
COLOR: High saturation, punchy, eye-catching
RHYTHM: Immediate hook, constant stimulus, no boring moments
BEATS: Aggressive beat sync, visual on every beat
MOOD: Viral, engaging, scroll-stopping
            """.strip()
        }
    }
    
    # Alias for backward compatibility
    STYLE_CONFIGS["cinematic"] = STYLE_CONFIGS["cinematic_drama"]
    
    def __init__(self):
        """Initialize StyleEditor"""
        pass
    
    def get_available_styles(self) -> Dict[str, str]:
        """Get list of available styles with descriptions"""
        return {
            style: config["description"] 
            for style, config in self.STYLE_CONFIGS.items()
        }
    
    def apply_style_to_video(
        self, 
        video_path: str, 
        output_path: str, 
        style: str = "cinematic"
    ) -> bool:
        """
        Apply style-specific color grading and effects to video
        
        Args:
            video_path: Input video file path
            output_path: Output video file path
            style: Style preset to apply
            
        Returns:
            bool: Success status
        """
        try:
            # Normalize style name
            style = style.lower().replace(" ", "_").replace("-", "_")
            
            if style not in self.STYLE_CONFIGS:
                logger.warning(f"Unknown style '{style}', using 'cinematic' as default")
                style = "cinematic"
            
            config = self.STYLE_CONFIGS[style]
            
            logger.info(f"Applying {style} style to video: {video_path}")
            
            # Build FFmpeg filter for color grading
            filters = self._build_color_filter(config)
            
            # Apply style with FFmpeg
            success = self._apply_ffmpeg_filters(video_path, output_path, filters)
            
            if success:
                logger.info(f"Style '{style}' applied successfully to {output_path}")
            else:
                logger.error(f"Failed to apply style '{style}' to video")
            
            return success
            
        except Exception as e:
            logger.error(f"Error applying style: {e}")
            return False
    
    def _build_color_filter(self, config: Dict) -> str:
        """
        Build FFmpeg color filter string based on style configuration
        
        Args:
            config: Style configuration dictionary
            
        Returns:
            str: FFmpeg filter string
        """
        filters = []
        
        # Color temperature adjustment
        temp = config["color_temperature"]
        if temp < 4000:  # Warm
            # Add warmth (more red/yellow)
            filters.append(f"colorbalance=rs=0.1:gs=-0.05:bs=-0.15:rm=0.05:gm=-0.02:bm=-0.1")
        elif temp > 5000:  # Cool
            # Add coolness (more blue)
            filters.append(f"colorbalance=rs=-0.1:gs=0.02:bs=0.15:rm=-0.05:gm=0.01:bm=0.1")
        
        # Saturation
        sat = config["saturation"]
        if sat != 1.0:
            filters.append(f"hue=s={sat}")
        
        # Contrast and brightness
        contrast = config["contrast"]
        brightness = config["brightness"] - 1.0  # FFmpeg brightness is offset-based
        if contrast != 1.0 or brightness != 0.0:
            filters.append(f"eq=contrast={contrast}:brightness={brightness}")
        
        # Gamma correction
        gamma = config["gamma"]
        if gamma != 1.0:
            filters.append(f"eq=gamma={gamma}")
        
        # Join filters with comma
        return ",".join(filters) if filters else "null"
    
    def _apply_ffmpeg_filters(
        self, 
        input_path: str, 
        output_path: str, 
        filters: str
    ) -> bool:
        """
        Apply FFmpeg filters to video
        
        Args:
            input_path: Input video file
            output_path: Output video file
            filters: FFmpeg filter string
            
        Returns:
            bool: Success status
        """
        try:
            # Build FFmpeg command
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file
                "-i", input_path,
                "-vf", filters,
                "-c:a", "copy",  # Copy audio without re-encoding
                "-preset", "fast",  # Fast encoding
                output_path
            ]
            
            logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")
            
            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return False
            
            # Verify output file exists
            if not Path(output_path).exists():
                logger.error(f"Output file not created: {output_path}")
                return False
                
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg process timed out")
            return False
        except Exception as e:
            logger.error(f"Error running FFmpeg: {e}")
            return False
    
    def apply_style_to_segments(
        self, 
        segment_paths: List[str], 
        style: str = "cinematic"
    ) -> List[str]:
        """
        Apply style to multiple video segments
        
        Args:
            segment_paths: List of video segment file paths
            style: Style preset to apply
            
        Returns:
            List[str]: List of styled video file paths
        """
        styled_paths = []
        
        for i, segment_path in enumerate(segment_paths):
            try:
                # Create styled output path
                path_obj = Path(segment_path)
                styled_path = str(path_obj.parent / f"styled_{path_obj.name}")
                
                # Apply style
                success = self.apply_style_to_video(
                    segment_path, 
                    styled_path, 
                    style
                )
                
                if success:
                    styled_paths.append(styled_path)
                    logger.info(f"Styled segment {i+1}/{len(segment_paths)}")
                else:
                    # Fallback to original if styling fails
                    styled_paths.append(segment_path)
                    logger.warning(f"Style application failed for segment {i+1}, using original")
                    
            except Exception as e:
                logger.error(f"Error styling segment {i+1}: {e}")
                styled_paths.append(segment_path)  # Fallback to original
        
        return styled_paths
    
    def get_style_metadata(self, style: str) -> Dict:
        """
        Get metadata for a specific style
        
        Args:
            style: Style name
            
        Returns:
            Dict: Style configuration and metadata
        """
        style = style.lower().replace(" ", "_").replace("-", "_")
        
        if style in self.STYLE_CONFIGS:
            return self.STYLE_CONFIGS[style].copy()
        else:
            logger.warning(f"Unknown style '{style}', returning default")
            return self.STYLE_CONFIGS["cinematic"].copy()

    def get_ai_prompt(self, style: str) -> str:
        """
        Get the AI editing prompt for a specific style.
        Used by AI Director to understand editing instructions.
        
        Args:
            style: Style name
            
        Returns:
            str: AI prompt with editing instructions
        """
        style = style.lower().replace(" ", "_").replace("-", "_")
        
        if style in self.STYLE_CONFIGS:
            return self.STYLE_CONFIGS[style].get("ai_prompt", "")
        else:
            logger.warning(f"Unknown style '{style}', using cinematic_drama")
            return self.STYLE_CONFIGS["cinematic_drama"].get("ai_prompt", "")