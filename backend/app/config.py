from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://editor:editor_pass@localhost:5432/ai_video_editor"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"

    # File Upload
    upload_dir: str = "./uploads"
    max_file_size: int = 104857600  # 100MB

    # Allowed Formats
    allowed_video_formats: str = "mp4,mov,avi"
    allowed_audio_formats: str = "mp3,wav,m4a"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    gemini_api_key: str = ""
    # Optional observability
    sentry_dsn: Optional[str] = None
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    @property
    def video_formats_list(self) -> list[str]:
        return [fmt.strip() for fmt in self.allowed_video_formats.split(",")]

    @property
    def audio_formats_list(self) -> list[str]:
        return [fmt.strip() for fmt in self.allowed_audio_formats.split(",")]


settings = Settings()
