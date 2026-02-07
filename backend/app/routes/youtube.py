
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid
import logging
import traceback

from app.services.youtube_downloader import YouTubeService
from app.tasks.video_tasks import process_podcast_task
from app.routes.jobs import redis_client, get_job_key
from datetime import datetime
import json

router = APIRouter()
logger = logging.getLogger(__name__)
youtube_service = YouTubeService()

class YouTubeInfoRequest(BaseModel):
    url: str

class YouTubeDownloadRequest(BaseModel):
    url: str
    enable_smart_reels: bool = True

@router.post("/info")
async def get_youtube_info(request: YouTubeInfoRequest):
    """Get metadata for a YouTube video"""
    try:
        info = await youtube_service.get_video_info(request.url)
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/download")
async def download_youtube_video(request: YouTubeDownloadRequest, background_tasks: BackgroundTasks):
    """
    Start a background job to:
    1. Download the video
    2. Process it for viral reels
    """
    try:
        # Generate a job ID
        job_id = str(uuid.uuid4())
        
        # 0. Initialize Job in Redis (Fixes 404)
        job = {
            "id": job_id,
            "status": "PENDING",
            "type": "YOUTUBE",
            "progress": 0,
            "current_step": "Initialized",
            "created_at": datetime.utcnow().isoformat(),
        }
        redis_client.set(get_job_key(job_id), json.dumps(job))
        redis_client.expire(get_job_key(job_id), 86400)

        from app.tasks.video_tasks import process_youtube_task
        process_youtube_task.delay(job_id, request.url, request.enable_smart_reels)
        
        return {"job_id": job_id, "status": "queued"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
