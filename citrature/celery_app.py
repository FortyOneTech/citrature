"""Celery application configuration for job orchestration."""

from celery import Celery
from citrature.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "citrature",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
    include=[
        "citrature.tasks.ingest",
        "citrature.tasks.graph",
        "citrature.tasks.analysis",
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
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,  # 1 hour
    result_persistent=True,
    task_routes={
        "citrature.tasks.ingest.*": {"queue": "default"},
        "citrature.tasks.graph.*": {"queue": "default"},
        "citrature.tasks.analysis.*": {"queue": "default"},
    },
    task_annotations={
        "citrature.tasks.ingest.ingest_pdf_task": {
            "rate_limit": "10/m",
            "time_limit": 1800,  # 30 minutes
            "soft_time_limit": 1500,  # 25 minutes
        },
        "citrature.tasks.ingest.ingest_topic_task": {
            "rate_limit": "5/m",
            "time_limit": 600,  # 10 minutes
            "soft_time_limit": 480,  # 8 minutes
        },
        "citrature.tasks.graph.build_graph_task": {
            "rate_limit": "2/m",
            "time_limit": 3600,  # 1 hour
            "soft_time_limit": 3000,  # 50 minutes
        },
        "citrature.tasks.analysis.gap_analysis_task": {
            "rate_limit": "1/m",
            "time_limit": 1800,  # 30 minutes
            "soft_time_limit": 1500,  # 25 minutes
        },
    },
)

# Optional configuration for development
if settings.api_origin == "http://localhost:8000":
    celery_app.conf.update(
        task_always_eager=False,  # Set to True for testing
        task_eager_propagates=True,
    )
