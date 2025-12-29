from celery import Celery
from app.config import settings
import platform

# Create Celery app
celery_app = Celery(
    "ai_video_editor",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Configure Celery
celery_config = {
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_time_limit": 30 * 60,  # 30 minutes hard limit
    "task_soft_time_limit": 25 * 60,  # 25 minutes soft limit
}

# Use solo pool on Windows to avoid multiprocessing issues
if platform.system() == "Windows":
    celery_config["worker_pool"] = "solo"

celery_app.conf.update(celery_config)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])


@celery_app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
