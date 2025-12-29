from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import uuid
import json
import redis
from datetime import datetime
from app.config import settings

router = APIRouter(prefix="/api", tags=["jobs"])

# Initialize Redis client
redis_client = redis.from_url(settings.redis_url, decode_responses=True)
JOB_PREFIX = "job:"

def get_job_key(job_id: str) -> str:
    return f"{JOB_PREFIX}{job_id}"

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status"""
    try:
        # Validate job_id format
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    # Get job from Redis
    job_data = redis_client.get(get_job_key(job_id))
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    job = json.loads(job_data)

    return JSONResponse(
        status_code=200,
        content={
            "job_id": job["id"],
            "status": job["status"],
            "style": job.get("style"),
            "progress": job.get("progress", 0),
            "current_step": job.get("current_step"),
            "error_message": job.get("error_message"),
            "output_video_url": job.get("output_video_url"),
        },
    )


@router.post("/jobs")
async def create_job(style: str = "cinematic_drama"):
    """Create a new job"""
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "status": "PENDING",
        "style": style,
        "progress": 0,
        "current_step": "Initialized",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Save to Redis
    redis_client.set(get_job_key(job_id), json.dumps(job))
    # Set expiry for 24 hours
    redis_client.expire(get_job_key(job_id), 86400)

    return JSONResponse(
        status_code=201,
        content={
            "job_id": job_id,
            "status": "PENDING",
        },
    )


def update_job_progress(job_id: str, progress: int, current_step: str = None):
    """Update job progress"""
    key = get_job_key(job_id)
    job_data = redis_client.get(key)
    
    if job_data:
        job = json.loads(job_data)
        job["progress"] = progress
        if current_step:
            job["current_step"] = current_step
        job["updated_at"] = datetime.utcnow().isoformat()
        
        redis_client.set(key, json.dumps(job))
        # Refresh expiry
        redis_client.expire(key, 86400)


def mark_job_complete(job_id: str, output_video_url: str = None):
    """Mark job as complete"""
    key = get_job_key(job_id)
    job_data = redis_client.get(key)
    
    if job_data:
        job = json.loads(job_data)
        job["status"] = "COMPLETED"
        job["progress"] = 100
        job["current_step"] = "Complete"
        if output_video_url:
            job["output_video_url"] = output_video_url
        job["updated_at"] = datetime.utcnow().isoformat()
        
        redis_client.set(key, json.dumps(job))


def mark_job_failed(job_id: str, error_message: str):
    """Mark job as failed"""
    key = get_job_key(job_id)
    job_data = redis_client.get(key)
    
    if job_data:
        job = json.loads(job_data)
        job["status"] = "FAILED"
        job["error_message"] = error_message
        job["updated_at"] = datetime.utcnow().isoformat()
        
        redis_client.set(key, json.dumps(job))
