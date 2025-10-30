"""Celery worker application."""

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
    include=[
        "services.worker.tasks.ingest",
        "services.worker.tasks.graph",
        "services.worker.tasks.analysis",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,
    result_persistent=True,
    task_routes={
        "services.worker.tasks.ingest.*": {"queue": "default"},
        "services.worker.tasks.graph.*": {"queue": "default"},
        "services.worker.tasks.analysis.*": {"queue": "default"},
    },
    task_annotations={
        "services.worker.tasks.ingest.ingest_pdf_task": {
            "rate_limit": "10/m",
            "time_limit": 1800,
            "soft_time_limit": 1500,
        },
        "services.worker.tasks.ingest.ingest_topic_task": {
            "rate_limit": "5/m",
            "time_limit": 600,
            "soft_time_limit": 480,
        },
        "services.worker.tasks.graph.build_graph_task": {
            "rate_limit": "2/m",
            "time_limit": 3600,
            "soft_time_limit": 3000,
        },
        "services.worker.tasks.analysis.gap_analysis_task": {
            "rate_limit": "1/m",
            "time_limit": 1800,
            "soft_time_limit": 1500,
        },
    },
)

if __name__ == "__main__":
    celery_app.start()
