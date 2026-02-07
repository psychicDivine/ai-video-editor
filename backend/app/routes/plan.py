"""
Plan Routes - API endpoints for EditPlan generation and rendering
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
import logging

from app.schemas.edit_plan import (
    EditPlan, EditPlanCreate, EditPlanUpdate, EditPlanResponse,
    RenderRequest, AudioTrack, EditClip
)
from app.models.job import Job, JobStatus
from app.services.beat_detector import BeatDetector
from app.services.ai_director import AIDirector
from app.services.plan_renderer import PlanRenderer
from app.services.effects import EffectsService, EFFECT_CATALOG
from app.services.ffmpeg_handler import FFmpegHandler, TRANSITION_CATALOG
from app.config import get_db, get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/plan", tags=["plan"])

# In-memory plan storage (replace with DB in production)
_plans: dict[str, EditPlan] = {}


@router.post("/generate", response_model=EditPlanResponse)
async def generate_plan(
    request: EditPlanCreate,
    db: Session = Depends(get_db)
):
    """
    Generate an EditPlan from inputs using AI.
    
    This endpoint:
    1. Analyzes the audio for beats
    2. Analyzes video clips for content
    3. Uses AI Director to create optimal edit plan
    4. Returns the plan for preview/editing
    """
    try:
        # Verify job exists
        job = db.query(Job).filter(Job.id == request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Update job status
        job.status = JobStatus.PROCESSING
        job.current_step = "Analyzing audio..."
        db.commit()
        
        # 1. Analyze audio for beats
        beat_detector = BeatDetector()
        beats_result = beat_detector.detect_beats(request.audio_path)
        
        audio_track = AudioTrack(
            source_path=request.audio_path,
            duration=beats_result.get("duration", request.target_duration),
            beats=beats_result.get("beats", []),
            bpm=beats_result.get("bpm"),
            volume=1.0
        )
        
        # 2. Update status
        job.current_step = "AI analyzing content..."
        db.commit()
        
        # 3. Use AI Director to generate plan
        ai_director = AIDirector()
        
        plan = await ai_director.generate_edit_plan(
            video_paths=request.video_paths,
            audio_track=audio_track,
            style=request.style.value,
            target_duration=request.target_duration,
            job_id=request.job_id
        )
        
        # 4. Store plan
        _plans[str(plan.id)] = plan
        
        # 5. Update job
        job.current_step = "Plan generated - ready for preview"
        db.commit()
        
        return EditPlanResponse(
            success=True,
            plan=plan,
            message="Edit plan generated successfully"
        )
        
    except Exception as e:
        logger.exception(f"Failed to generate plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plan_id}", response_model=EditPlanResponse)
async def get_plan(plan_id: UUID):
    """Get an existing edit plan by ID"""
    plan = _plans.get(str(plan_id))
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return EditPlanResponse(success=True, plan=plan)


@router.put("/{plan_id}", response_model=EditPlanResponse)
async def update_plan(plan_id: UUID, update: EditPlanUpdate):
    """
    Update an existing edit plan (from UI edits).
    
    Users can:
    - Reorder clips
    - Change transitions
    - Add/remove effects
    - Adjust timing
    """
    plan = _plans.get(str(plan_id))
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Apply updates
    if update.clips is not None:
        plan.clips = update.clips
    if update.audio is not None:
        plan.audio = update.audio
    if update.style is not None:
        plan.style = update.style
    
    # Recalculate total duration
    if plan.clips:
        last_clip = max(plan.clips, key=lambda c: c.timeline_position + (c.end_time - c.start_time))
        plan.total_duration = last_clip.timeline_position + (last_clip.end_time - last_clip.start_time)
    
    from datetime import datetime
    plan.updated_at = datetime.utcnow()
    plan.rendered = False  # Mark as needing re-render
    
    _plans[str(plan_id)] = plan
    
    return EditPlanResponse(
        success=True,
        plan=plan,
        message="Plan updated successfully"
    )


@router.post("/{plan_id}/render", response_model=EditPlanResponse)
async def render_plan(
    plan_id: UUID,
    request: RenderRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Render an edit plan to final video.
    
    This is the "Create Reel" action - executes the plan.
    """
    plan = _plans.get(str(plan_id))
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Get job
    job = db.query(Job).filter(Job.id == plan.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Update job status
    job.status = JobStatus.PROCESSING
    job.current_step = "Rendering video..."
    db.commit()
    
    # Start rendering in background
    background_tasks.add_task(
        _render_plan_task,
        plan=plan,
        job_id=str(plan.job_id),
        quality=request.quality
    )
    
    return EditPlanResponse(
        success=True,
        plan=plan,
        message="Rendering started"
    )


async def _render_plan_task(plan: EditPlan, job_id: str, quality: str):
    """Background task to render the plan"""
    from app.config import get_db_session
    
    try:
        renderer = PlanRenderer()
        output_path = await renderer.render(plan, quality=quality)
        
        # Update plan
        plan.rendered = True
        plan.output_path = output_path
        _plans[str(plan.id)] = plan
        
        # Update job
        with get_db_session() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = JobStatus.COMPLETED
                job.current_step = "Complete"
                job.output_video_path = output_path
                db.commit()
                
    except Exception as e:
        logger.exception(f"Render failed: {e}")
        with get_db_session() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                db.commit()


@router.get("/catalog/effects")
async def get_effects_catalog():
    """Get available effects with metadata"""
    return {
        "success": True,
        "effects": EFFECT_CATALOG
    }


@router.get("/catalog/transitions")
async def get_transitions_catalog():
    """Get available transitions with metadata"""
    return {
        "success": True,
        "transitions": TRANSITION_CATALOG
    }


@router.get("/catalog/styles")
async def get_styles_catalog():
    """Get available editing styles"""
    from app.services.style_editor import StyleEditor
    
    editor = StyleEditor()
    styles = {}
    
    for style_id in ["cinematic_drama", "energetic_dance", "luxe_travel", "modern_minimal", "viral_tiktok"]:
        config = editor.get_style_config(style_id)
        if config:
            styles[style_id] = {
                "name": config.get("name", style_id),
                "description": config.get("description", ""),
                "ai_prompt": config.get("ai_prompt", "")
            }
    
    return {
        "success": True,
        "styles": styles
    }
