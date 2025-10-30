"""Celery beat scheduler application."""

import logging
from celery import Celery
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import initialize_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize and validate settings
settings = initialize_settings()

# Create Celery app
celery_app = Celery(
    "citrature",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Define periodic tasks here when needed
celery_app.conf.beat_schedule = {
    # Example: clean up old task results
    # 'cleanup-task-results': {
    #     'task': 'services.worker.tasks.cleanup.cleanup_old_results',
    #     'schedule': crontab(hour=2, minute=0),
    # },
}

if __name__ == "__main__":
    celery_app.start()

