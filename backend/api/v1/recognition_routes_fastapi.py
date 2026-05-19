"""
FastAPI Recognition Routes
Migration of Flask recognition_routes.py to FastAPI.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from backend.api.v1.validation_models import CreateRecognitionJobRequest
from backend.services.recognition_job_service import RecognitionJobService
from backend.api.v1.dependencies import require_faculty
from backend.api.error_handler import error_response, success_response, ErrorCode
from backend.models import Faculty
import structlog

router = APIRouter()
log = structlog.get_logger(__name__)


def parse_int(value: Optional[str]) -> Optional[int]:
    """Parse string to integer safely."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def queue_recognition_job(payload: CreateRecognitionJobRequest, marked_by: str):
    """Queue a recognition job with validation."""
    course = payload.course
    lecture_no = payload.lecture_no
    duration_seconds = payload.duration_seconds or 30

    if not course or lecture_no is None or not marked_by:
        response = error_response(ErrorCode.INVALID_PAYLOAD, "course and lecture_no are required", 400)
        raise HTTPException(status_code=400, detail=response["error"])
        
    if duration_seconds < 5 or duration_seconds > 600:
        response = error_response(ErrorCode.INVALID_PAYLOAD, "duration_seconds must be between 5 and 600", 400)
        raise HTTPException(status_code=400, detail=response["error"])

    # TODO: Pass app context properly for Celery job creation
    job = RecognitionJobService.createAndStartJob(
        app=None,
        course=course,
        lectureNo=lecture_no,
        markedBy=marked_by,
        durationSeconds=duration_seconds,
    )
    return job


@router.post("/recognition/attendance/run", status_code=202)
async def run_recognition_attendance_api(
    payload: CreateRecognitionJobRequest,
    current_faculty: Faculty = Depends(require_faculty),
):
    """Start face recognition for attendance marking (faculty-only)."""
    try:
        job = queue_recognition_job(payload, current_faculty.name)
        return success_response({"message": "Recognition job queued", "job": job})
    except HTTPException:
        raise
    except Exception as e:
        log.error("run_recognition_error", error=str(e))
        response = error_response(ErrorCode.INTERNAL_ERROR, "Failed to start recognition job", 500)
        raise HTTPException(status_code=500, detail=response["error"])


@router.post("/recognition/jobs", status_code=202)
async def create_recognition_job_api(
    payload: CreateRecognitionJobRequest,
    current_faculty: Faculty = Depends(require_faculty),
):
    """Create a recognition job (faculty-only)."""
    try:
        job = queue_recognition_job(payload, current_faculty.name)
        return success_response(job)
    except HTTPException:
        raise
    except Exception as e:
        log.error("create_job_error", error=str(e))
        response = error_response(ErrorCode.INTERNAL_ERROR, "Failed to create recognition job", 500)
        raise HTTPException(status_code=500, detail=response["error"])


@router.get("/recognition/jobs/{job_id}")
async def get_recognition_job_api(
    job_id: str,
    current_faculty: Faculty = Depends(require_faculty),
):
    """Get recognition job status (faculty-only)."""
    job = RecognitionJobService.getJob(job_id)
    if job is None:
        response = error_response(ErrorCode.NOT_FOUND, "Recognition job not found", 404)
        raise HTTPException(status_code=404, detail=response["error"])
    return success_response(job)

