import subprocess
import json
from pathlib import Path
from typing import List, Optional
import logging
import os
import shutil

logger = logging.getLogger(__name__)


class FFmpegHandler:
    """Handle FFmpeg operations for video processing"""

    def __init__(self):
        # Try to find ffmpeg in PATH first, otherwise use full path
        self.ffmpeg_cmd = shutil.which("ffmpeg") or r"C:\Users\HimanshuRajp_ytpbwj3\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
        self.ffprobe_cmd = shutil.which("ffprobe") or r"C:\Users\HimanshuRajp_ytpbwj3\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffprobe.exe"
        
        logger.info(f"Using ffmpeg: {self.ffmpeg_cmd}")
        logger.info(f"Using ffprobe: {self.ffprobe_cmd}")

    def get_video_info(self, video_path: str) -> dict:
        """Get video information using ffprobe"""
        try:
            cmd = [
                self.ffprobe_cmd,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height,duration",
                "-of",
                "json",
                video_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            if data.get("streams"):
                stream = data["streams"][0]
                return {
                    "width": stream.get("width", 1920),
                    "height": stream.get("height", 1080),
                    "duration": float(stream.get("duration", 0)),
                }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
        return {"width": 1920, "height": 1080, "duration": 0}

    def get_audio_info(self, audio_path: str) -> dict:
        """Get audio information using ffprobe"""
        try:
            cmd = [
                self.ffprobe_cmd,
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=duration,sample_rate",
                "-of",
                "json",
                audio_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            if data.get("streams"):
                stream = data["streams"][0]
                return {
                    "duration": float(stream.get("duration", 0)),
                    "sample_rate": stream.get("sample_rate", 44100),
                }
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
        return {"duration": 0, "sample_rate": 44100}

    def trim_video(
        self, 
        input_path: str, 
        output_path: str, 
        start_time: float, 
        duration: float,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30
    ) -> bool:
        """Trim video segment and standardize resolution/fps"""
        try:
            # We use re-encoding (libx264) instead of stream copy (-c copy)
            # because stream copy on non-keyframes causes black frames/freezing.
            # We also enforce resolution and frame rate here to ensure all segments
            # are identical before concatenation.
            
            # Filter complex for scaling and fps
            # scale: resize to fit within box
            # pad: fill remaining space with black to match exact aspect ratio
            # fps: force constant frame rate
            vf_filter = (
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
                f"fps={fps}"
            )

            cmd = [
                self.ffmpeg_cmd,
                "-ss",
                str(start_time),
                "-i",
                input_path,
                "-t",
                str(duration),
                "-vf",
                vf_filter,
                "-c:v",
                "libx264",
                "-preset",
                "faster", # Use faster preset for intermediate segments
                "-c:a",
                "aac",
                "-ar", "44100", # Standardize audio sample rate
                "-ac", "2",     # Standardize audio channels
                "-y",
                output_path,
            ]
            
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            logger.info(f"Video trimmed and standardized: {start_time}s + {duration}s")
            return True
        except Exception as e:
            logger.error(f"Error trimming video: {e}")
            return False

    def concatenate_videos(
        self, video_paths: List[str], output_path: str, transition_duration: float = 0.5
    ) -> bool:
        """Concatenate multiple videos with transitions"""
        try:
            # Create concat demuxer file
            concat_file = Path(output_path).parent / "concat.txt"
            with open(concat_file, "w") as f:
                for video_path in video_paths:
                    # Convert to absolute path and use forward slashes for FFmpeg
                    abs_path = str(Path(video_path).absolute()).replace("\\", "/")
                    f.write(f"file '{abs_path}'\n")

            # FFmpeg command for concatenation
            cmd = [
                self.ffmpeg_cmd,
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                "-y",
                output_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Videos concatenated to {output_path}")
            concat_file.unlink()  # Clean up concat file
            return True
        except Exception as e:
            logger.error(f"Error concatenating videos: {e}")
            return False

    def trim_audio(
        self, input_path: str, output_path: str, start_time: float, duration: float
    ) -> bool:
        """Trim audio segment"""
        try:
            cmd = [
                self.ffmpeg_cmd,
                "-ss",
                str(start_time),
                "-i",
                input_path,
                "-t",
                str(duration),
                "-c:a",
                "libmp3lame" if output_path.endswith(".mp3") else "aac",
                "-y",
                output_path,
            ]
            
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Audio trimmed: {start_time}s + {duration}s")
            return True
        except Exception as e:
            logger.error(f"Error trimming audio: {e}")
            return False

    def mix_audio(
        self, video_path: str, audio_path: str, output_path: str
    ) -> bool:
        """Mix audio with video, always re-encode to ensure audio is present"""
        try:
            cmd = [
                self.ffmpeg_cmd,
                "-i", video_path,
                "-i", audio_path,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-movflags", "+faststart",
                "-y", output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Audio mixed to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error mixing audio: {e}")
            return False

    def resize_video(
        self, input_path: str, output_path: str, width: int = 1080, height: int = 1920
    ) -> bool:
        """Resize video to target dimensions"""
        try:
            cmd = [
                self.ffmpeg_cmd,
                "-i",
                input_path,
                "-vf",
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
                "-c:a",
                "copy",
                "-y",
                output_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Video resized to {width}x{height}")
            return True
        except Exception as e:
            logger.error(f"Error resizing video: {e}")
            return False

    def apply_fade_transition(
        self, input_path: str, output_path: str, fade_duration: float = 0.5
    ) -> bool:
        """Apply fade transition effect with final quality encoding"""
        try:
            # Get video duration first
            video_info = self.get_video_info(input_path)
            duration = video_info.get("duration", 0)
            
            if duration == 0:
                logger.warning("Could not get video duration, skipping fade transition")
                import shutil
                shutil.copy(input_path, output_path)
                return True
            
            # Calculate fade out start time
            fade_out_start = max(0, duration - fade_duration)
            
            cmd = [
                self.ffmpeg_cmd,
                "-i",
                input_path,
                "-vf",
                f"fade=t=in:st=0:d={fade_duration},fade=t=out:st={fade_out_start}:d={fade_duration}",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-c:a",
                "copy",
                "-y",
                output_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Fade transition applied with final quality settings")
            return True
        except Exception as e:
            logger.error(f"Error applying fade transition: {e}")
            return False

    def render_final_video(
        self, input_path: str, output_path: str, preset: str = "medium"
    ) -> bool:
        """Render final video with H.264 codec"""
        try:
            cmd = [
                self.ffmpeg_cmd,
                "-i",
                input_path,
                "-c:v",
                "libx264",
                "-preset",
                preset,
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-y",
                output_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Final video rendered to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error rendering final video: {e}")
            return False
