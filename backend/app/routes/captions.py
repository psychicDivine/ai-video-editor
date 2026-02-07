
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
from pathlib import Path
from datetime import datetime

from app.config import settings
from app.services.caption_styles import CAPTION_STYLES, get_style
from app.services.caption_service import CaptionService
from app.services.ffmpeg_handler import FFmpegHandler
from app.routes.jobs import get_job_key, redis_client

import json

router = APIRouter(prefix="/api/captions", tags=["captions"])
logger = logging.getLogger(__name__)

class RestyleRequest(BaseModel):
    style: str # classic, tiktok, hormozi, neon

@router.get("/styles")
async def list_available_styles():
    """List all available caption styles with details."""
    styles = {}
    for key, val in CAPTION_STYLES.items():
        styles[key] = {
            "name": val["name"],
            "description": val["description"],
            "preview_color": val["primary_color"]
        }
    return JSONResponse(content=styles)

@router.post("/restyle/{job_id}")
async def restyle_job_captions(job_id: str, request: RestyleRequest):
    """
    Quickly re-render captions for a completed job.
    Does NOT re-analyze video, only re-burns subtitles.
    """
    try:
        if request.style not in CAPTION_STYLES:
            raise HTTPException(status_code=400, detail=f"Invalid style. Available: {list(CAPTION_STYLES.keys())}")

        job_dir = Path(settings.upload_dir) / job_id / "reels"
        if not job_dir.exists():
             raise HTTPException(status_code=404, detail="Job files not found. Job may be expired.")
        
        # We need to find all reels and re-burn them
        # Typically reels are named reel_1_reframed.mp4, reel_1_captions.ass, reel_1_final.mp4
        
        # Find all caption/video pairs
        # We start from 'reframed' (clean) and burn new 'captions' to 'final'
        
        reels = list(job_dir.glob("*_reframed.mp4"))
        if not reels:
            raise HTTPException(status_code=404, detail="No source reels found to restyle.")
            
        caption_service = CaptionService()
        ffmpeg_service = FFmpegHandler()
        
        processed_reels = []
        
        for reframed_path in reels:
            # e.g. reel_1_reframed.mp4 -> reel_1
            reel_name = reframed_path.stem.replace("_reframed", "")
            
            # Paths
            json_path = job_dir / f"{reel_name}_audio.json" # Basic Whisper JSON
            ass_path = job_dir / f"{reel_name}_captions.ass"
            final_path = job_dir / f"{reel_name}_final.mp4"
            
            # Check if we have the transcript to regenerate ASS
            if not json_path.exists():
                logger.warning(f"No transcript found for {reel_name}, skipping.")
                # Fallback: maybe we can't restyle this one
                continue
                
            # Load transcript
            with open(json_path, 'r', encoding='utf-8') as f:
                transcript_data = json.load(f)
                segments = transcript_data.get("segments", [])
                
            # Regenerate ASS with new style
            logger.info(f"Restyling {reel_name} to {request.style}")
            caption_service.generate_ass_file(segments, str(ass_path), style=request.style)
            
            # Burn subtitles (fast re-encode)
            # Use 'fast' or 'veryfast' preset for UI responsiveness
            cmd_success = ffmpeg_service.burn_subtitles(
                str(reframed_path), 
                str(final_path), 
                str(ass_path)
            )
            
            if cmd_success:
                processed_reels.append(str(final_path))
            else:
                logger.error(f"Failed to burn subtitles for {reel_name}")

        if not processed_reels:
             raise HTTPException(status_code=500, detail="Failed to re-render any reels.")

        # Re-zip if needed (optional for quick preview, but good for download)
        # We can trigger a background zip update or do it here if fast
        
        # Return success with preview URL of first reel
        first_reel_filename = Path(processed_reels[0]).name
        preview_url = f"/api/preview/{job_id}/{first_reel_filename}"
        
        return JSONResponse(content={
            "success": True,
            "message": f"Restyled with {request.style}",
            "preview_url": preview_url,
            "style": request.style
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Restyle error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
