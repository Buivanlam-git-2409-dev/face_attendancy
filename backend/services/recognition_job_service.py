import uuid
from datetime import datetime

from backend.celery_app import celeryApp
from backend.extensions import db
from backend.models import RecognitionJob
from backend.services.face_recognition_service import FaceRecognitionService


class RecognitionJobService:
    @staticmethod
    def createAndStartJob(app, course: str, lectureNo: int, markedBy: str, durationSeconds: int):
        job = RecognitionJob(
            job_id=uuid.uuid4().hex,
            course=course,
            lecture_no=lectureNo,
            marked_by=markedBy,
            duration_seconds=durationSeconds,
            status='queued',
        )
        db.session.add(job)
        db.session.commit()

        celeryApp.send_task("recognition.run_attendance_job", args=[job.job_id])
        return RecognitionJobService.serialize(job)

    @staticmethod
    def runJob(app, jobId: str):
        with app.app_context():
            job = RecognitionJob.query.filter_by(job_id=jobId).first()
            if job is None:
                return

            job.status = 'running'
            job.started_at = datetime.now()
            db.session.commit()

            try:
                result = FaceRecognitionService.runAttendanceLoop(
                    course=job.course,
                    lectureNo=job.lecture_no,
                    markedBy=job.marked_by,
                    displayWindow=False,
                    maxDurationSeconds=job.duration_seconds,
                )
                job.status = 'completed'
                job.marked_count = result.get('markedCount', 0)
                job.finished_at = datetime.now()
                db.session.commit()
            except Exception as error:
                job.status = 'failed'
                job.error_message = str(error)
                job.finished_at = datetime.now()
                db.session.commit()

    @staticmethod
    def getJob(jobId: str):
        job = RecognitionJob.query.filter_by(job_id=jobId).first()
        if job is None:
            return None
        return RecognitionJobService.serialize(job)

    @staticmethod
    def serialize(job: RecognitionJob):
        return {
            "jobId": job.job_id,
            "course": job.course,
            "lectureNo": job.lecture_no,
            "markedBy": job.marked_by,
            "durationSeconds": job.duration_seconds,
            "status": job.status,
            "markedCount": job.marked_count,
            "errorMessage": job.error_message,
            "startedAt": job.started_at.isoformat() if job.started_at else None,
            "finishedAt": job.finished_at.isoformat() if job.finished_at else None,
        }
