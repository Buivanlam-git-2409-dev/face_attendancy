"""
FastAPI Recognition Routes
Migration of Flask recognition_routes.py to FastAPI.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services.recognition_job_service import RecognitionJobService

router = APIRouter()


class CreateRecognitionJobRequest(BaseModel):
    course: Optional[str] = None
    lecture_no: Optional[int] = None
    duration_seconds: Optional[int] = 30


def parse_int(value: Optional[str]) -> Optional[int]:
    """Parse string to integer safely."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def success_response(data):
    """Standardized success response."""
    return {"success": True, "data": data, "error": None}


def error_response(code: str, message: str, status_code: int):
    """Standardized error response."""
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message}
    )


def queue_recognition_job(payload: CreateRecognitionJobRequest):
    """Queue a recognition job with validation."""
    course = payload.course
    lecture_no = payload.lecture_no
    duration_seconds = payload.duration_seconds or 30
    marked_by = "System"  # TODO: Extract from JWT token

    if not course or lecture_no is None or not marked_by:
        return None, error_response("INVALID_PAYLOAD", "course and lecture_no are required", 400)
    if duration_seconds < 5 or duration_seconds > 600:
        return None, error_response("INVALID_PAYLOAD", "duration_seconds must be between 5 and 600", 400)

    # TODO: Pass app context properly for Celery job creation
    job = RecognitionJobService.createAndStartJob(
        app=None,
        course=course,
        lectureNo=lecture_no,
        markedBy=marked_by,
        durationSeconds=duration_seconds,
    )
    return job, None


@router.post("/recognition/attendance/run", status_code=202)
async def run_recognition_attendance_api(payload: CreateRecognitionJobRequest):
    """Start face recognition for attendance marking (faculty-only)."""
    # TODO: Add JWT faculty verification
    job, error = queue_recognition_job(payload)
    if error is not None:
        raise error
    return success_response({"message": "Recognition job queued", "job": job})


@router.post("/recognition/jobs", status_code=202)
async def create_recognition_job_api(payload: CreateRecognitionJobRequest):
    """Create a recognition job (faculty-only)."""
    # TODO: Add JWT faculty verification
    job, error = queue_recognition_job(payload)
    if error is not None:
        raise error
    return success_response(job)


@router.get("/recognition/jobs/{job_id}")
async def get_recognition_job_api(job_id: str):
    """Get recognition job status (faculty-only)."""
    # TODO: Add JWT faculty verification
    job = RecognitionJobService.getJob(job_id)
    if job is None:
        error_response("NOT_FOUND", "Recognition job not found", 404)
    return success_response(job)
