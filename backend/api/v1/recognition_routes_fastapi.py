"""
FastAPI Recognition Routes.

Routes:
- POST /recognition/verify: upload one frame/image and mark attendance.
- POST /recognition/attendance/run: start legacy/MVP recognition job.
- GET /recognition/jobs/{job_id}: get recognition job status.
"""

import cv2
import face_recognition
import numpy as np
import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from backend.api.error_handler import ErrorCode, error_response, success_response
from backend.api.v1.dependencies import require_faculty
from backend.api.v1.validation_models import CreateRecognitionJobRequest
from backend.models import Faculty
from backend.services.face_recognition_service import FaceRecognitionService
from backend.services.recognition_job_service import RecognitionJobService


router = APIRouter()
log = structlog.get_logger(__name__)


def bad_request(message: str):
    response = error_response(ErrorCode.BAD_REQUEST, message, 400)
    raise HTTPException(status_code=400, detail=response["error"])


def not_found(message: str):
    response = error_response(ErrorCode.NOT_FOUND, message, 404)
    raise HTTPException(status_code=404, detail=response["error"])


def internal_error(message: str):
    response = error_response(ErrorCode.INTERNAL_ERROR, message, 500)
    raise HTTPException(status_code=500, detail=response["error"])


def queue_recognition_job(
    payload: CreateRecognitionJobRequest,
    current_faculty: Faculty,
):
    """
    Queue/start a recognition job.

    Note:
    This is still a legacy/MVP flow. The preferred MVP route for frontend camera
    is POST /recognition/verify, where frontend uploads a frame/image.
    """
    if not payload.course or payload.lecture_no is None:
        bad_request("course and lecture_no are required")

    job = RecognitionJobService.createAndStartJob(
        app=None,
        course=payload.course,
        lectureNo=payload.lecture_no,
        markedBy=current_faculty.name,
        durationSeconds=payload.duration_seconds or 30,
    )

    return job


@router.post("/recognition/verify")
async def verify_face_api(
    file: UploadFile = File(...),
    course: str = Form(...),
    lecture_no: int = Form(...),
    current_faculty: Faculty = Depends(require_faculty),
):
    """
    Verify face from an uploaded frame/image and mark attendance.

    Faculty only.
    """
    log.info(
        "recognition_verify_request",
        filename=file.filename,
        course=course,
        lecture_no=lecture_no,
        faculty=current_faculty.name,
    )

    try:
        contents = await file.read()

        if not contents:
            bad_request("Uploaded file is empty")

        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            bad_request("Invalid image file")

        known_face_encodings, known_face_names = (
            FaceRecognitionService.loadKnownFacesFromDb()
        )

        if not known_face_encodings:
            return success_response(
                {
                    "results": [],
                    "message": "No known faces available",
                }
            )

        rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(
            rgb_frame,
            face_locations,
        )

        results = []

        for face_encoding in face_encodings:
            recognized_identity = FaceRecognitionService.resolveFaceName(
                face_encoding,
                known_face_encodings,
                known_face_names,
            )

            if recognized_identity == "Unknown":
                results.append(
                    {
                        "identity": "Unknown",
                        "marked": False,
                    }
                )
                continue

            marked = FaceRecognitionService.markAttendanceFromRecognition(
                recognized_identity,
                course,
                lecture_no,
                current_faculty.name,
            )

            results.append(
                {
                    "identity": recognized_identity,
                    "marked": marked,
                }
            )

        log.info(
            "recognition_verify_success",
            detected_faces=len(face_encodings),
            recognized_faces=len(
                [item for item in results if item["identity"] != "Unknown"]
            ),
        )

        return success_response(
            {
                "results": results,
                "detectedFaces": len(face_encodings),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error("recognition_verify_error", error=str(e), exc_info=e)
        internal_error("Verification failed")


@router.post("/recognition/attendance/run", status_code=202)
async def run_recognition_attendance_api(
    payload: CreateRecognitionJobRequest,
    current_faculty: Faculty = Depends(require_faculty),
):
    """
    Start face recognition job.

    Faculty only.
    """
    log.info(
        "recognition_job_start_request",
        course=payload.course,
        lecture_no=payload.lecture_no,
        faculty=current_faculty.name,
    )

    try:
        job = queue_recognition_job(payload, current_faculty)

        return success_response(
            {
                "message": "Recognition job queued",
                "job": job,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error("recognition_job_start_error", error=str(e), exc_info=e)
        internal_error("Failed to start recognition job")


@router.get("/recognition/jobs/{job_id}")
async def get_recognition_job_api(
    job_id: str,
    current_faculty: Faculty = Depends(require_faculty),
):
    """
    Get recognition job status.

    Faculty only.
    """
    log.info(
        "recognition_job_get_request",
        job_id=job_id,
        faculty=current_faculty.name,
    )

    try:
        job = RecognitionJobService.getJob(job_id)

        if not job:
            not_found("Recognition job not found")

        return success_response(job)

    except HTTPException:
        raise
    except Exception as e:
        log.error(
            "recognition_job_get_error",
            job_id=job_id,
            error=str(e),
            exc_info=e,
        )
        internal_error("Failed to retrieve recognition job")