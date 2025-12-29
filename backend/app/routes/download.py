from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import uuid

from app.config import settings

router = APIRouter(prefix="/api", tags=["download"])


@router.get("/download/{job_id}")
async def download_video(job_id: str):
    """Download processed video"""
    try:
        # Validate job_id format
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    # Construct video path
    video_path = Path(settings.upload_dir) / job_id / "output.mp4"

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=f"video_{job_id}.mp4",
    )
