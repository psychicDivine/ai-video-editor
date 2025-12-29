from sqlalchemy import Column, String, Integer, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.models import Base


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class StylePreset(str, enum.Enum):
    CINEMATIC_DRAMA = "cinematic_drama"
    ENERGETIC_DANCE = "energetic_dance"
    LUXE_TRAVEL = "luxe_travel"
    MODERN_MINIMAL = "modern_minimal"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    style = Column(String(50), default=StylePreset.CINEMATIC_DRAMA.value)
    progress = Column(Integer, default=0)
    current_step = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    output_video_path = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Job {self.id} - {self.status}>"
