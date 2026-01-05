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
    
    # Style configurations based on project requirements
    STYLE_CONFIGS = {
        "cinematic_drama": {
            "color_temperature": 5600,  # Cool tones
            "saturation": 0.9,  # Slightly desaturated
            "contrast": 1.1,
            "brightness": 0.95,
            "gamma": 1.05,
            "description": "Professional, dramatic, moody"
        },
        "cinematic": {  # Alias for cinematic_drama
            "color_temperature": 5600,
            "saturation": 0.9,
            "contrast": 1.1,
            "brightness": 0.95,
            "gamma": 1.05,
            "description": "Professional, dramatic, moody"
        },
        "energetic_dance": {
            "color_temperature": 2700,  # Warm tones
            "saturation": 1.2,  # +20% saturation
            "contrast": 1.15,
            "brightness": 1.05,
            "gamma": 0.95,
            "description": "Energetic, confident, fast-paced"
        },
        "luxe_travel": {
            "color_temperature": 3200,  # Warm golden
            "saturation": 1.1,
            "contrast": 1.05,
            "brightness": 1.02,
            "gamma": 1.0,
            "description": "Wanderlust, luxury, peaceful"
        },
        "modern_minimal": {
            "color_temperature": 4500,  # Neutral
            "saturation": 0.95,
            "contrast": 1.0,
            "brightness": 1.0,
            "gamma": 1.0,
            "description": "Clean, professional, modern"
        }
    }
    
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