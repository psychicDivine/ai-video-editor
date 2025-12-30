import os
import sys
import logging
from pathlib import Path
from unittest.mock import MagicMock
import subprocess

# Add current directory to path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the redis and job update functions BEFORE importing VideoProcessor
# because VideoProcessor imports them at module level
import app.routes.jobs
app.routes.jobs.update_job_progress = MagicMock()
app.routes.jobs.mark_job_complete = MagicMock()
app.routes.jobs.mark_job_failed = MagicMock()

from app.services.video_processor import VideoProcessor
from app.services.ffmpeg_handler import FFmpegHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_test_assets(output_dir: Path):
    """Generate dummy video and audio files for testing"""
    output_dir.mkdir(exist_ok=True)
    
    video_path = output_dir / "test_video.mp4"
    audio_path = output_dir / "test_audio.mp3"
    
    # Get ffmpeg path from handler
    handler = FFmpegHandler()
    ffmpeg_cmd = handler.ffmpeg_cmd
    
    # Generate 10s video
    if not video_path.exists():
        logger.info("Generating test video...")
        try:
            subprocess.run([
                ffmpeg_cmd, "-f", "lavfi", "-i", "testsrc=duration=10:size=1280x720:rate=30",
                "-c:v", "libx264", "-y", str(video_path)
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Video generation failed: {e.stderr.decode()}")
            raise

    # Generate 10s audio
    if not audio_path.exists():
        logger.info("Generating test audio...")
        try:
            subprocess.run([
                ffmpeg_cmd, "-f", "lavfi", "-i", "sine=frequency=1000:duration=10",
                "-c:a", "aac", "-y", str(audio_path)
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio generation failed: {e.stderr.decode()}")
            raise
        
    return str(video_path), str(audio_path)

def test_flow():
    base_dir = Path("test_output")
    base_dir.mkdir(exist_ok=True)
    
    # 1. Use Real Assets
    input_dir = Path(r"C:\Office\editor\backend\uploads\input")
    audio_dir = input_dir / "audio"
    
    video_paths = [
        str(input_dir / "ANINI - Arunachal Pradesh #bindassjohn #shorts.mp4"),
        str(input_dir / "Beautiful Road  Way to Anini, Arunachal Pradesh.mp4"),
        str(input_dir / "Hills Arunachal Pradesh India #nature #video #naturelovers.mp4"),
        str(input_dir / "menchukha-the-fairytale-village-of-arunachal-pradesh-isa-khan-720-ytshorts.savetube.me.mp4")
    ]
    
    music_path = str(audio_dir / "QUESTIONS (OFFICIAL VIDEO) REAL BOSS ThugNationStudioz  Latest Punjabi Songs 2023 - Thug Nation Studios.mp3")
    
    # 2. Setup Processor
    processor = VideoProcessor()
    job_id = "test_job_real_assets"
    output_dir = base_dir / job_id
    output_dir.mkdir(exist_ok=True)
    
    logger.info(f"Starting test processing for job {job_id}")
    logger.info(f"Using {len(video_paths)} video clips")
    logger.info(f"Using music: {music_path}")
    
    # 3. Run Processing
    try:
        success = processor.process_video(
            job_id=job_id,
            video_paths=video_paths,
            music_path=music_path,
            style="cinematic",
            output_dir=output_dir,
            music_start_time=46.0,  # 0:46
            music_end_time=76.0,    # 1:16 (30 seconds duration)
            transition_name="dissolve",
            export_mlt=True,
        )
        
        if success:
            logger.info("✅ Processing successful!")
            logger.info(f"Output directory: {output_dir}")
            logger.info(f"Check {output_dir / 'output.mp4'} for the final result")
        else:
            logger.error("❌ Processing failed")
            
    except Exception as e:
        logger.error(f"❌ Exception during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_flow()
