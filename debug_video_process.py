import sys
import os
from pathlib import Path
import logging

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock database functions
import app.routes.jobs
app.routes.jobs.update_job_progress = lambda *args: print(f"Progress: {args}")
app.routes.jobs.mark_job_complete = lambda *args: print(f"Complete: {args}")
app.routes.jobs.mark_job_failed = lambda *args: print(f"Failed: {args}")

from app.services.video_processor import VideoProcessor

logging.basicConfig(level=logging.INFO)

def run_test():
    processor = VideoProcessor()
    
    base_path = Path(r"C:\Office\editor\backend\uploads\input")
    video_paths = [
        str(base_path / "ANINI - Arunachal Pradesh #bindassjohn #shorts.mp4"),
        str(base_path / "Beautiful Road  Way to Anini, Arunachal Pradesh.mp4"),
        str(base_path / "Hills Arunachal Pradesh India #nature #video #naturelovers.mp4"),
        str(base_path / "menchukha-the-fairytale-village-of-arunachal-pradesh-isa-khan-720-ytshorts.savetube.me.mp4")
    ]
    
    music_path = str(base_path / "audio" / "QUESTIONS (OFFICIAL VIDEO) REAL BOSS ThugNationStudioz  Latest Punjabi Songs 2023 - Thug Nation Studios.mp3")
    
    output_dir = Path("backend/test_output")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("Starting processing...")
    try:
        processor.process_video(
            job_id="test_job_1",
            video_paths=video_paths,
            music_path=music_path,
            style="cinematic",
            output_dir=output_dir,
            music_start_time=0.0,
            music_end_time=30.0
        )
        print("Processing finished.")
    except Exception as e:
        print(f"Processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
