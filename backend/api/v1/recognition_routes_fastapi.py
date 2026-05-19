"""
FastAPI Recognition Routes
Migration of Flask recognition_routes.py to FastAPI.
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional
import numpy as np
import cv2
import face_recognition

from backend.api.v1.validation_models import CreateRecognitionJobRequest
from backend.services.recognition_job_service import RecognitionJobService
from backend.services.face_recognition_service import FaceRecognitionService
from backend.api.v1.dependencies import require_faculty
from backend.api.error_handler import error_response, success_response, ErrorCode
from backend.models import Faculty
import structlog

router = APIRouter()
log = structlog.get_logger(__name__)

def queue_recognition_job(payload: CreateRecognitionJobRequest, current_faculty: Faculty):
    """Queue a recognition job using valid faculty context."""
    # MVP: Sync execution within the request for simplicity, or queue to Celery
    # Since FastAPI is async, we call service directly for MVP stability.
    # If app context is needed, pass 'None' as app, and update service logic.
    
    # Validation logic
    if not payload.course or payload.lecture_no is None:
        raise HTTPException(status_code=400, detail="course and lecture_no are required")
        
    # Logic to start job
    job = RecognitionJobService.createAndStartJob(
        app=None, # Context handling should be done inside service if Celery is used
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
    """Verify face from uploaded frame and mark attendance."""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        knownFaceEncodings, knownFaceNames = FaceRecognitionService.loadKnownFacesFromDb()
        
        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        results = []
        for face_encoding in face_encodings:
            name = FaceRecognitionService.resolveFaceName(face_encoding, knownFaceEncodings, knownFaceNames)
            if name != "Unknown":
                marked = FaceRecognitionService.markAttendanceFromRecognition(name, course, lecture_no, current_faculty.name)
                results.append({"rollno": name, "marked": marked})
        
        return success_response({"results": results})
        
    except Exception as e:
        log.error("verification_error", error=str(e))
        raise HTTPException(status_code=500, detail="Verification failed")

@router.post("/recognition/attendance/run", status_code=202)
async def run_recognition_attendance_api(
    payload: CreateRecognitionJobRequest,
    current_faculty: Faculty = Depends(require_faculty),
):
    """Start face recognition job."""
    job = queue_recognition_job(payload, current_faculty)
    return success_response({"message": "Recognition job queued", "job": job})

@router.get("/recognition/jobs/{job_id}")
async def get_recognition_job_api(
    job_id: str,
    current_faculty: Faculty = Depends(require_faculty),
):
    job = RecognitionJobService.getJob(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Recognition job not found")
    return success_response(job)


