"""
EditPlan Schema - Central data structure for AI-driven video editing
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


class EffectType(str, Enum):
    """Available video effects"""
    SLOWMO = "slowmo"
    SPEEDUP = "speedup"
    SPEEDRAMP = "speedramp"
    FREEZE = "freeze"
    ZOOM_PUNCH = "zoomPunch"
    KENBURNS = "kenburns"
    FLASH_WHITE = "flashWhite"
    SHAKE = "shake"
    VIGNETTE = "vignette"
    COLOR_PULSE = "colorPulse"


class TransitionType(str, Enum):
    """Available transitions"""
    FADE = "fade"
    DISSOLVE = "dissolve"
    FADEBLACK = "fadeblack"
    FADEWHITE = "fadewhite"
    WIPELEFT = "wipeleft"
    WIPERIGHT = "wiperight"
    WIPEUP = "wipeup"
    WIPEDOWN = "wipedown"
    SLIDELEFT = "slideleft"
    SLIDERIGHT = "slideright"
    SLIDEUP = "slideup"
    SLIDEDOWN = "slidedown"
    CIRCLECROP = "circlecrop"
    CIRCLEOPEN = "circleopen"
    CIRCLECLOSE = "circleclose"
    PIXELIZE = "pixelize"
    RADIAL = "radial"


class StyleType(str, Enum):
    """Available editing styles"""
    CINEMATIC_DRAMA = "cinematic_drama"
    ENERGETIC_DANCE = "energetic_dance"
    LUXE_TRAVEL = "luxe_travel"
    MODERN_MINIMAL = "modern_minimal"
    VIRAL_TIKTOK = "viral_tiktok"


# ============== EFFECT MODELS ==============

class Effect(BaseModel):
    """Single effect applied to a clip"""
    type: str = Field(..., description="Effect type from EffectType enum")
    params: Dict[str, Any] = Field(default_factory=dict, description="Effect parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "zoomPunch",
                "params": {"intensity": 0.15, "duration": 0.2}
            }
        }


# ============== CLIP MODELS ==============

class EditClipBase(BaseModel):
    """Base clip in the edit plan"""
    source_video_id: Optional[str] = Field(None, description="UUID of source video in database")
    source_path: str = Field(..., description="Path to source video file")
    start_time: float = Field(0.0, ge=0, description="Start time in source video (seconds)")
    end_time: float = Field(..., gt=0, description="End time in source video (seconds)")


class EditClip(EditClipBase):
    """Complete clip with timeline position, transitions, and effects"""
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique clip ID")
    timeline_position: float = Field(0.0, ge=0, description="Position on output timeline (seconds)")
    
    # Transition before this clip (ignored for first clip)
    transition_in: Optional[str] = Field(None, description="Transition type before this clip")
    transition_in_duration: float = Field(0.5, ge=0.1, le=2.0, description="Transition duration")
    
    # Effects applied to this clip
    effects: List[Effect] = Field(default_factory=list, description="Effects applied to this clip")
    
    # Metadata
    label: Optional[str] = Field(None, description="User-visible label for the clip")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "clip-1",
                "source_video_id": "550e8400-e29b-41d4-a716-446655440000",
                "source_path": "/uploads/job/video1.mp4",
                "start_time": 0.0,
                "end_time": 3.5,
                "timeline_position": 0.0,
                "transition_in": "fade",
                "transition_in_duration": 0.5,
                "effects": [{"type": "zoomPunch", "params": {"intensity": 0.15}}],
                "label": "Intro shot"
            }
        }


# ============== AUDIO MODELS ==============

class AudioTrack(BaseModel):
    """Audio track for the edit"""
    source_path: str = Field(..., description="Path to audio file")
    duration: float = Field(..., gt=0, description="Audio duration in seconds")
    beats: List[float] = Field(default_factory=list, description="Beat timestamps in seconds")
    bpm: Optional[float] = Field(None, description="Beats per minute")
    volume: float = Field(1.0, ge=0, le=2.0, description="Volume multiplier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_path": "/uploads/job/music.mp3",
                "duration": 30.0,
                "beats": [0.5, 1.0, 1.5, 2.0, 2.5],
                "bpm": 120,
                "volume": 1.0
            }
        }


# ============== EDIT PLAN MODELS ==============

class EditPlanCreate(BaseModel):
    """Request to create/generate an edit plan"""
    job_id: UUID
    style: StyleType = Field(default=StyleType.CINEMATIC_DRAMA)
    target_duration: float = Field(30.0, ge=5, le=180, description="Target output duration")
    video_paths: List[str] = Field(..., min_length=1, description="Paths to input videos")
    audio_path: str = Field(..., description="Path to audio file")


class EditPlanBase(BaseModel):
    """Base edit plan structure"""
    job_id: UUID
    style: str = Field(default="cinematic_drama")
    audio: AudioTrack
    clips: List[EditClip] = Field(default_factory=list)
    total_duration: float = Field(0.0, ge=0)


class EditPlan(EditPlanBase):
    """Complete edit plan with metadata"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Generation metadata
    ai_model: Optional[str] = Field(None, description="AI model used to generate plan")
    generation_prompt: Optional[str] = Field(None, description="Prompt used for generation")
    
    # Render status
    rendered: bool = Field(default=False)
    output_path: Optional[str] = Field(None, description="Path to rendered output")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "job_id": "550e8400-e29b-41d4-a716-446655440001",
                "style": "cinematic_drama",
                "audio": {
                    "source_path": "/uploads/job/music.mp3",
                    "duration": 30.0,
                    "beats": [0.5, 1.0, 1.5, 2.0],
                    "bpm": 120,
                    "volume": 1.0
                },
                "clips": [
                    {
                        "id": "clip-1",
                        "source_path": "/uploads/job/video1.mp4",
                        "start_time": 0.0,
                        "end_time": 3.5,
                        "timeline_position": 0.0,
                        "transition_in": "fade",
                        "transition_in_duration": 0.5,
                        "effects": []
                    }
                ],
                "total_duration": 30.0,
                "created_at": "2026-01-24T10:00:00Z",
                "updated_at": "2026-01-24T10:00:00Z",
                "ai_model": "gemini-2.0-flash",
                "rendered": False
            }
        }


class EditPlanUpdate(BaseModel):
    """Update an existing edit plan (from UI edits)"""
    clips: Optional[List[EditClip]] = None
    audio: Optional[AudioTrack] = None
    style: Optional[str] = None


class EditPlanResponse(BaseModel):
    """API response for edit plan"""
    success: bool
    plan: Optional[EditPlan] = None
    message: Optional[str] = None


class RenderRequest(BaseModel):
    """Request to render an edit plan"""
    plan_id: UUID
    quality: str = Field(default="high", pattern="^(draft|medium|high)$")
    output_format: str = Field(default="mp4", pattern="^(mp4|mov|webm)$")
