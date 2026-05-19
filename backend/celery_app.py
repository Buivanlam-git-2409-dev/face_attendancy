from celery import Celery

celeryApp = Celery("attendance_worker")

# Lazy load Config to avoid circular imports
def init_celery_config():
    from backend.config import Config
    celeryApp.conf.update(
        broker_url=Config.CELERY_BROKER_URL,
        result_backend=Config.CELERY_RESULT_BACKEND,
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
