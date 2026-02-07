
import logging
import asyncio
from pathlib import Path
from typing import Dict, Optional, Any
import subprocess
import json
import sys

logger = logging.getLogger(__name__)

class YouTubeService:
    """
    Service to handle YouTube video downloads and metadata extraction using yt-dlp.
    """
    
    def __init__(self):
        self.output_dir = Path("uploads/youtube")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Fetch metadata for a YouTube video without downloading.
        """
        try:
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "--dump-json",
                "--no-playlist",
                "--skip-download",
                url
            ]
            
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: subprocess.run(cmd, capture_output=True, text=True, check=True)
            )
            
            info = json.loads(result.stdout)
            
            return {
                "title": info.get("title", "Unknown Title"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),
                "uploader": info.get("uploader"),
                "view_count": info.get("view_count"),
                "id": info.get("id"),
                "url": url
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"yt-dlp failed: {e.stderr}")
            raise Exception(f"Failed to fetch video info: {e.stderr}")
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            raise

    async def download_video(self, url: str, job_id: str) -> Dict[str, str]:
        """
        Download video from YouTube with caching support.
        """
        try:
            # Get video ID for caching
            video_info = await self.get_video_info(url)
            video_id = video_info.get("id", job_id)
            
            # Cache directory
            cache_dir = Path("storage/downloads_cache")
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            cached_path = cache_dir / f"{video_id}.mp4"
            target_path = self.output_dir / f"{job_id}.mp4"
            
            # 1. Check Cache
            if cached_path.exists():
                logger.info(f"Video found in cache: {cached_path}")
                import shutil
                # Copy from cache to job folder
                shutil.copy(cached_path, target_path)
                return {"video_path": str(target_path)}
            
            # 2. Download to Cache (if not found)
            logger.info(f"Starting download for {video_id} to cache...")
            
            # Output template for cache
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]", 
                "--merge-output-format", "mp4",
                "-o", str(cached_path),
                "--no-playlist",
                "--progress",
                "--newline",  # Required for clean log parsing
                url
            ]
            
            # Helper to log output line by line
            def log_process(proc):
                for line in proc.stdout:
                    line = line.decode('utf-8', errors='replace').strip()
                    if '[download]' in line and '%' in line:
                         # Filter noisy progress bars, maybe only log every 10%?
                         # For now just log it so users see movement
                         logger.info(f"yt-dlp: {line}")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: subprocess.run(cmd, check=True, stdout=None, stderr=None) # Just let it print to console which shows in celery logs
            )
            
            # 3. Copy to Job Folder
            if cached_path.exists():
                import shutil
                shutil.copy(cached_path, target_path)
                return {"video_path": str(target_path)}
                
            raise Exception("Download finished but file not found")

        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise
