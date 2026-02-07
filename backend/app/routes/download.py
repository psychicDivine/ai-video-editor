from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import uuid

from app.config import settings

router = APIRouter(prefix="/api", tags=["download"])


@router.get("/download/{job_id}")
async def download_video(job_id: str):
    """Download processed video (only if output exists)"""
    try:
        # Validate job_id format
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    # Construct video path
    video_path = Path(settings.upload_dir) / job_id / "output.mp4"

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Output video not found or expired. Please re-upload and process your files.")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=f"video_{job_id}.mp4",
    )

@router.get("/download/zip/{job_id}")
async def download_zip(job_id: str):
    """Download zipped collection of viral reels"""
    try:
        # Validate job_id format
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    # Construct zip path
    zip_path = Path(settings.upload_dir) / job_id / "viral_reels.zip"

    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Viral reels ZIP not found or expired.")

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"viral_reels_{job_id}.zip",
    )

@router.get("/preview/{job_id}/{filename}")
async def preview_reel(job_id: str, filename: str):
    """Serve individual reel for preview"""
    try:
        # Validate job_id format
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    # Construct reel path (inside reels directory)
    reel_path = Path(settings.upload_dir) / job_id / "reels" / filename

    if not reel_path.exists():
        raise HTTPException(status_code=404, detail="Preview video not found.")

    return FileResponse(
        path=reel_path,
        media_type="video/mp4",
        filename=filename,
    )
