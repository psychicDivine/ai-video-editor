from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID


class StylePreset(str, Enum):
    CINEMATIC_DRAMA = "cinematic_drama"
    ENERGETIC_DANCE = "energetic_dance"
    LUXE_TRAVEL = "luxe_travel"
    MODERN_MINIMAL = "modern_minimal"


class JobStatus(str, Enum):
    PENDING = "PENDING"
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JobCreate(BaseModel):
    style: StylePreset = Field(default=StylePreset.CINEMATIC_DRAMA)
    duration: int = Field(default=30, ge=10, le=60)
    aspect_ratio: str = Field(default="9:16")


class JobResponse(BaseModel):
    id: UUID
    status: JobStatus
    style: str
    progress: int
    current_step: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    output_video_url: Optional[str]

    class Config:
        from_attributes = True
