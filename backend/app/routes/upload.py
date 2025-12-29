from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import logging
from pathlib import Path

from app.config import settings
from app.models.job import Job, JobStatus, StylePreset
from app.models.video import Video, Audio
from app.schemas.job import JobResponse
from app.tasks.video_tasks import process_video_task
from app.routes.jobs import jobs_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_files(
    videos: list[UploadFile] = File(...),
    music: UploadFile = File(...),
    style: str = Form(default="cinematic_drama"),
    music_start_time: float = Form(default=0.0),
    music_end_time: float = Form(default=30.0),
):
    """Upload videos and music, create a job and trigger processing"""
    try:
        # Validate style
        try:
            StylePreset(style)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid style")

        # Validate files
        if not videos:
            raise HTTPException(status_code=400, detail="At least one video is required")
        if not music:
            raise HTTPException(status_code=400, detail="Music file is required")

        # Create job
        job_id = str(uuid.uuid4())
        job_dir = UPLOAD_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # Save videos
        video_paths = []
        for video_file in videos:
            if not video_file.filename:
                continue

            # Validate file size
            content = await video_file.read()
            if len(content) > settings.max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {video_file.filename} exceeds max size",
                )

            # Save file
            file_path = job_dir / video_file.filename
            with open(file_path, "wb") as f:
                f.write(content)
            video_paths.append(str(file_path))

        # Save music
        music_content = await music.read()
        if len(music_content) > settings.max_file_size:
            raise HTTPException(status_code=400, detail="Music file exceeds max size")

        music_path = job_dir / (music.filename or "music.mp3")
        with open(music_path, "wb") as f:
            f.write(music_content)

        # Create job record
        job = {
            "id": job_id,
            "status": "PENDING",
            "style": style,
            "progress": 0,
            "current_step": "Files uploaded",
            "video_paths": video_paths,
            "music_path": str(music_path),
            "music_start_time": music_start_time,
            "music_end_time": music_end_time,
        }
        jobs_db[job_id] = job

        # Trigger Celery task for async processing
        try:
            process_video_task.delay(
                job_id=job_id,
                video_paths=video_paths,
                music_path=str(music_path),
                style=style,
                music_start_time=music_start_time,
                music_end_time=music_end_time,
            )
        except Exception as celery_error:
            logger.error(f"Celery task error: {str(celery_error)}", exc_info=True)
            # Still return success to frontend, but log the error
            # The job will be marked as pending and can be retried

        return JSONResponse(
            status_code=201,
            content={
                "job_id": job_id,
                "status": "PENDING",
                "message": "Files uploaded successfully. Processing started.",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
