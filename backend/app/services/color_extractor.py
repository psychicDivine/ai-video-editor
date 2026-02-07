
import cv2
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class ColorExtractor:
    """
    Service to extract dominant colors from video frames.
    Used to suggest caption colors that contrast with the video content.
    """
    
    def extract_dominant_colors(self, video_path: str, num_colors: int = 3, sample_count: int = 10) -> List[str]:
        """
        Extract dominant colors from video.
        Returns list of hex colors in ASS format (&H00RRGGBB).
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return ["&H00FFFFFF"] * num_colors

            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            step = max(1, frame_count // sample_count)
            
            sampled_pixels = []
            
            for i in range(0, frame_count, step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Resize to small image for speed
                small_frame = cv2.resize(frame, (50, 50))
                # OpenCV uses BGR, we want RGB for analysis usually, 
                # but ASS uses BGR (actually GBR? No, ASS is &HAABBGGRR usually, but typical hex is RRGGBB. 
                # ASS color format: &H00BBGGRR (Blue Green Red)
                
                # Let's keep BGR since ASS uses BGR order in the hex string (BBGGRR)
                pixels = small_frame.reshape(-1, 3)
                sampled_pixels.append(pixels)

            cap.release()
            
            if not sampled_pixels:
                return ["&H00FFFFFF"] * num_colors

            all_pixels = np.concatenate(sampled_pixels, axis=0)
            
            # Simple manual K-means implementation to avoid heavy sklearn dependency if not needed
            # Or just use histogram binning for speed
            
            # Implementation using simple binning/quantization for robustness
            # 1. Quantize colors to reduce space (e.g. 16x16x16 bins)
            # 2. Find most frequent
            
            # Alternatively, OpenCV has kmeans
            full_pixels = np.float32(all_pixels)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            flags = cv2.KMEANS_RANDOM_CENTERS
            compactness, labels, centers = cv2.kmeans(full_pixels, num_colors, None, criteria, 10, flags)
            
            dominant_colors = []
            for center in centers:
                # center is B, G, R
                b, g, r = int(center[0]), int(center[1]), int(center[2])
                # Format for ASS: &H00BBGGRR
                # Wait, ASS color code is &H00<Blue><Green><Red>
                # e.g. Red is &H000000FF  (Blue=00, Green=00, Red=FF)
                # Our hex string needs to be exactly that.
                
                # Let's format strictly:
                hex_color = f"&H00{b:02X}{g:02X}{r:02X}"
                dominant_colors.append(hex_color)
                
            return dominant_colors

        except Exception as e:
            logger.error(f"Error extracting colors: {e}")
            return ["&H00FFFFFF"] * num_colors

    def suggest_highlight_color(self, dominant_colors: List[str]) -> str:
        """
        Suggest a highlight color based on dominant colors.
        Returns ASS hex string.
        """
        # Improved logic:
        # If dominant is dark, use Yellow or Cyan
        # If dominant is light, use Dark Red or Blue
        # For now, default to Yellow (&H0000FFFF) as it stands out on most
        return "&H0000FFFF"
