"""
Real-ESRGAN Video Enhancement Service
Upscales and enhances video quality using Real-ESRGAN
"""
import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class VideoEnhancementService:
    """Real-ESRGAN video quality enhancement"""
    
    def __init__(self):
        """Initialize enhancement service"""
        self.realesrgan_available = False
        self.model_path = None
        
        # Check if Real-ESRGAN is available
        try:
            result = subprocess.run(
                ["python", "-c", "import realesrgan; print('available')"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and "available" in result.stdout:
                self.realesrgan_available = True
                logger.info("Real-ESRGAN available for video enhancement")
            else:
                logger.warning("Real-ESRGAN not available - install with: pip install realesrgan")
        except Exception as e:
            logger.warning(f"Real-ESRGAN check failed: {e}")
    
    def enhance_video_quality(
        self,
        input_video_path: str,
        output_video_path: str,
        scale: int = 2,
        model_name: str = "RealESRGAN_x2plus"
    ) -> bool:
        """
        Enhance video quality using Real-ESRGAN
        
        Args:
            input_video_path: Path to input video
            output_video_path: Path for enhanced output
            scale: Upscaling factor (2 or 4)
            model_name: Real-ESRGAN model to use
            
        Returns:
            Success status
        """
        if not self.realesrgan_available:
            logger.warning("Real-ESRGAN not available, skipping enhancement")
            return self._fallback_enhancement(input_video_path, output_video_path)
        
        try:
            logger.info(f"Enhancing video quality with Real-ESRGAN (scale={scale})")
            
            # Extract frames, enhance, and reassemble
            temp_dir = Path(output_video_path).parent / "enhancement_temp"
            temp_dir.mkdir(exist_ok=True)
            
            # Step 1: Extract frames
            frames_dir = temp_dir / "frames"
            frames_dir.mkdir(exist_ok=True)
            
            extract_success = self._extract_frames(input_video_path, str(frames_dir))
            if not extract_success:
                return False
            
            # Step 2: Enhance frames with Real-ESRGAN
            enhanced_dir = temp_dir / "enhanced"
            enhanced_dir.mkdir(exist_ok=True)
            
            enhance_success = self._enhance_frames(
                str(frames_dir),
                str(enhanced_dir),
                scale,
                model_name
            )
            if not enhance_success:
                return False
            
            # Step 3: Reassemble video
            reassemble_success = self._reassemble_video(
                input_video_path,
                str(enhanced_dir),
                output_video_path
            )
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            if reassemble_success:
                logger.info(f"Video enhancement completed: {output_video_path}")
                return True
            else:
                logger.error("Failed to reassemble enhanced video")
                return False
                
        except Exception as e:
            logger.error(f"Error enhancing video: {e}")
            return False
    
    def _extract_frames(self, video_path: str, frames_dir: str) -> bool:
        """Extract all frames from video"""
        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-i", video_path,
                "-qscale:v", "2",
                f"{frames_dir}/frame_%06d.jpg"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                logger.error(f"Frame extraction failed: {result.stderr}")
                return False
            
            # Check if frames were created
            frame_files = list(Path(frames_dir).glob("frame_*.jpg"))
            if not frame_files:
                logger.error("No frames extracted from video")
                return False
            
            logger.debug(f"Extracted {len(frame_files)} frames")
            return True
            
        except Exception as e:
            logger.error(f"Error extracting frames: {e}")
            return False
    
    def _enhance_frames(
        self,
        frames_dir: str,
        enhanced_dir: str,
        scale: int,
        model_name: str
    ) -> bool:
        """Enhance frames using Real-ESRGAN"""
        try:
            # Use Real-ESRGAN CLI if available
            cmd = [
                "realesrgan-ncnn-vulkan",
                "-i", frames_dir,
                "-o", enhanced_dir,
                "-s", str(scale),
                "-n", model_name,
                "-f", "jpg"
            ]
            
            logger.debug(f"Real-ESRGAN command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode != 0:
                logger.warning(f"Real-ESRGAN CLI failed, trying Python interface: {result.stderr}")
                return self._enhance_frames_python(frames_dir, enhanced_dir, scale)
            
            # Check if enhanced frames were created
            enhanced_files = list(Path(enhanced_dir).glob("*.jpg"))
            if not enhanced_files:
                logger.error("No enhanced frames created")
                return False
            
            logger.debug(f"Enhanced {len(enhanced_files)} frames")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Real-ESRGAN enhancement timed out")
            return False
        except Exception as e:
            logger.error(f"Error enhancing frames: {e}")
            return False
    
    def _enhance_frames_python(
        self,
        frames_dir: str,
        enhanced_dir: str,
        scale: int
    ) -> bool:
        """Enhance frames using Real-ESRGAN Python interface"""
        try:
            from realesrgan import RealESRGANer
            from basicsr.archs.rrdbnet_arch import RRDBNet
            import cv2
            
            # Initialize model
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=scale)
            
            # Note: You would need to download the actual model weights
            # For now, this is a placeholder showing the structure
            upsampler = RealESRGANer(
                scale=scale,
                model_path='path/to/model/weights.pth',  # TODO: Add actual model path
                model=model,
                tile=256,
                tile_pad=10,
                pre_pad=0,
                half=False  # Set to True if using GPU with FP16
            )
            
            frame_files = sorted(Path(frames_dir).glob("frame_*.jpg"))
            
            for frame_file in frame_files:
                # Read frame
                img = cv2.imread(str(frame_file))
                if img is None:
                    continue
                
                # Enhance
                enhanced_img, _ = upsampler.enhance(img, outscale=scale)
                
                # Save enhanced frame
                output_path = Path(enhanced_dir) / frame_file.name
                cv2.imwrite(str(output_path), enhanced_img)
            
            logger.info(f"Enhanced {len(frame_files)} frames with Python interface")
            return True
            
        except ImportError:
            logger.error("Real-ESRGAN Python package not properly installed")
            return False
        except Exception as e:
            logger.error(f"Error with Python Real-ESRGAN: {e}")
            return False
    
    def _reassemble_video(
        self,
        original_video_path: str,
        enhanced_frames_dir: str,
        output_video_path: str
    ) -> bool:
        """Reassemble enhanced frames back into video"""
        try:
            # Get original video properties
            probe_cmd = [
                "ffprobe",
                "-v", "quiet",
                "-select_streams", "v:0",
                "-show_entries", "stream=r_frame_rate",
                "-of", "csv=p=0",
                original_video_path
            ]
            
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                fps = result.stdout.strip()
            else:
                fps = "30"  # Default fps
            
            # Reassemble video
            cmd = [
                "ffmpeg",
                "-y",
                "-framerate", fps,
                "-i", f"{enhanced_frames_dir}/frame_%06d.jpg",
                "-i", original_video_path,
                "-map", "0:v:0",
                "-map", "1:a:0?",  # Include audio if available
                "-c:v", "libx264",
                "-c:a", "copy",
                "-preset", "medium",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                output_video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                logger.error(f"Video reassembly failed: {result.stderr}")
                return False
            
            # Verify output exists
            if not Path(output_video_path).exists():
                logger.error(f"Enhanced video not created: {output_video_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error reassembling video: {e}")
            return False
    
    def _fallback_enhancement(
        self,
        input_video_path: str,
        output_video_path: str
    ) -> bool:
        """Fallback enhancement using FFmpeg filters"""
        try:
            logger.info("Using FFmpeg fallback for video enhancement")
            
            # Apply basic enhancement filters
            cmd = [
                "ffmpeg",
                "-y",
                "-i", input_video_path,
                "-filter_complex",
                "unsharp=5:5:1.0:5:5:0.0,eq=contrast=1.1:brightness=0.02:saturation=1.1",
                "-c:a", "copy",
                "-preset", "medium",
                "-crf", "20",
                output_video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                logger.error(f"Fallback enhancement failed: {result.stderr}")
                # Just copy the file if enhancement fails
                import shutil
                shutil.copy2(input_video_path, output_video_path)
                return True
            
            logger.info("Fallback enhancement completed")
            return True
            
        except Exception as e:
            logger.error(f"Error in fallback enhancement: {e}")
            return False
    
    def is_enhancement_needed(
        self,
        video_path: str,
        min_width: int = 1080,
        min_height: int = 1920
    ) -> bool:
        """Check if video needs quality enhancement"""
        try:
            # Get video dimensions
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=p=0",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return True  # Assume enhancement needed if can't check
            
            dimensions = result.stdout.strip().split(',')
            if len(dimensions) >= 2:
                width = int(dimensions[0])
                height = int(dimensions[1])
                
                # Check if resolution is below target
                if width < min_width or height < min_height:
                    logger.info(f"Enhancement needed: {width}x{height} < {min_width}x{min_height}")
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking if enhancement needed: {e}")
            return False