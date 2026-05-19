from celery_app import celeryApp
from backend.services.recognition_job_service import RecognitionJobService


@celeryApp.task(name="recognition.run_attendance_job")
def runRecognitionJobTask(jobId: str):
    from app import app

    RecognitionJobService.runJob(app=app, jobId=jobId)
