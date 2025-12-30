from pathlib import Path
import logging

from app.config import settings
from app.services.video_processor import VideoProcessor
from app.services.beat_detector import BeatDetector
from app.routes.jobs import update_job_progress, mark_job_complete, mark_job_failed

logger = logging.getLogger(__name__)

# Try to import the configured Celery app; if unavailable (tests), provide a dummy decorator
try:
    from app.celery_app import celery_app
except Exception:
    class _DummyCelery:
        def task(self, *args, **kwargs):
            def _decorator(f):
                return f

            return _decorator

        def __getattr__(self, _):
            return lambda *a, **k: None

    celery_app = _DummyCelery()


@celery_app.task(bind=True)
def process_video_task(
    self,
    job_id: str,
    video_paths: list,
    music_path: str,
    style: str,
    music_start_time: float = 0.0,
    music_end_time: float = 30.0,
):
    """Celery task to process video asynchronously"""
    try:
        output_dir = Path(settings.upload_dir) / job_id
        output_dir.mkdir(parents=True, exist_ok=True)

        update_job_progress(job_id, 5, "Initializing video processor")

        # Initialize services
        processor = VideoProcessor()
        beat_detector = BeatDetector()

        update_job_progress(job_id, 10, "Detecting beats in music")

        # Detect beats for optimal cutting
        beat_times, tempo = beat_detector.detect_beats(music_path)
        logger.info(f"Detected {len(beat_times)} beats at {tempo:.1f} BPM")

        update_job_progress(job_id, 15, "Analyzing video segments")

        # Get optimal cut points based on beats
        num_cuts = max(2, len(video_paths) - 1)
        cut_points = beat_detector.get_cut_points(music_path, num_cuts)

        # Persist cut points for diagnostics/frontend use
        try:
            import json

            (output_dir / "cut_points.json").write_text(json.dumps({"cut_points": cut_points}))
            update_job_progress(job_id, 18, "Cut points computed and saved")
        except Exception:
            logger.exception("Failed to write cut_points.json")

        update_job_progress(job_id, 20, "Processing videos")

        # Process video with beat-synced cuts
        success = processor.process_video(
            job_id=job_id,
            video_paths=video_paths,
            music_path=music_path,
            style=style,
            output_dir=output_dir,
            music_start_time=music_start_time,
            music_end_time=music_end_time,
            cut_points=cut_points,
        )

        if success:
            logger.info(f"Video processing completed for job {job_id}")
            mark_job_complete(job_id, f"/api/download/{job_id}")
        else:
            mark_job_failed(job_id, "Video processing failed")

        return {"job_id": job_id, "success": success}

    except Exception as e:
        logger.error(f"Error in video processing task: {e}")
        mark_job_failed(job_id, str(e))
        raise


@celery_app.task
def cleanup_old_jobs(days: int = 7):
    """Cleanup old job files"""
    try:
        from datetime import datetime, timedelta
        import shutil

        upload_dir = Path(settings.upload_dir)
        cutoff_time = datetime.now() - timedelta(days=days)

        for job_dir in upload_dir.iterdir():
            if job_dir.is_dir():
                mtime = datetime.fromtimestamp(job_dir.stat().st_mtime)
                if mtime < cutoff_time:
                    shutil.rmtree(job_dir)
                    logger.info(f"Deleted old job directory: {job_dir}")

    except Exception as e:
        logger.error(f"Error cleaning up old jobs: {e}")


@celery_app.task
def cleanup_old_outputs(hours: int = 1):
    """Delete output.mp4 files older than N hours (default: 1 hour)"""
    try:
        from datetime import datetime, timedelta

        upload_dir = Path(settings.upload_dir)
        cutoff_time = datetime.now() - timedelta(hours=hours)

        for job_dir in upload_dir.iterdir():
            if job_dir.is_dir():
                output_file = job_dir / "output.mp4"
                if output_file.exists():
                    mtime = datetime.fromtimestamp(output_file.stat().st_mtime)
                    if mtime < cutoff_time:
                        try:
                            output_file.unlink()
                            logger.info(f"Deleted old output: {output_file}")
                        except Exception as e:
                            logger.warning(f"Failed to delete {output_file}: {e}")
    except Exception as e:
        logger.error(f"Error cleaning up old outputs: {e}")
