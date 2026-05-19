"""
FastAPI Attendance Routes
Migration of Flask attendance_routes.py to FastAPI with validation and logging.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import structlog

from backend.api.v1.validation_models import (
    CreateAttendanceRequest,
    UpdateAttendanceRequest,
    AttendanceResponse,
)
from backend.api.error_handler import error_response, success_response, ErrorCode
from backend.services.attendance_service import AttendanceService
from backend.api.v1.dependencies import require_faculty
from backend.models import Faculty

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


@router.get("/attendances")
async def list_attendances_api(
    rollno: Optional[str] = Query(None),
    lecture_no: Optional[str] = Query(None),
    course: Optional[str] = Query(None),
    marked_by: Optional[str] = Query(None),
    current_faculty: Faculty = Depends(require_faculty),
):
    """List attendance records with optional filters (faculty-only)."""
    log.info("list_attendances_request", rollno=rollno, course=course, lecture_no=lecture_no, faculty=current_faculty.name)
    try:
        rollno_int = parse_int(rollno)
        lecture_no_int = parse_int(lecture_no)
        
        data = AttendanceService.listAttendances(
            rollNo=rollno_int,
            course=course,
            lectureNo=lecture_no_int,
            markedBy=marked_by,
        )
        log.info("list_attendances_success", count=len(data) if isinstance(data, list) else 0)
        return success_response(data)
    except Exception as e:
        log.error("list_attendances_error", error=str(e), exc_info=e)
        response = error_response(
            ErrorCode.INTERNAL_ERROR,
            "Failed to retrieve attendance records",
            500
        )
        raise HTTPException(status_code=500, detail=response["error"])


@router.post("/attendances", status_code=201)
async def mark_attendance_api(
    payload: CreateAttendanceRequest,
    current_faculty: Faculty = Depends(require_faculty),
):
    """Mark attendance for a student (faculty-only)."""
    log.info("mark_attendance_request", rollno=payload.rollno, course=payload.course, faculty=current_faculty.name)
    try:
        rollNo = payload.rollno
        lectureNo = payload.lecture_no or 0
        course = payload.course

        marked_by = current_faculty.name
        data, error = AttendanceService.markAttendance(
            rollNo=rollNo,
            course=course,
            lectureNo=lectureNo,
            markedBy=marked_by,
        )
        if error is not None:
            log.warning("mark_attendance_failed", rollno=rollNo, reason=error)
            response = error_response(
                ErrorCode.CONFLICT,
                error,
                409
            )
            raise HTTPException(status_code=409, detail=response["error"])

        log.info("mark_attendance_success", rollno=rollNo, course=course)
        return success_response(data)
    except HTTPException:
        raise
    except Exception as e:
        log.error("mark_attendance_error", rollno=payload.rollno, error=str(e), exc_info=e)
        response = error_response(
            ErrorCode.INTERNAL_ERROR,
            "Failed to mark attendance",
            500
        )
        raise HTTPException(status_code=500, detail=response["error"])


@router.put("/attendances/{att_id}")
async def update_attendance_api(
    att_id: int, 
    payload: UpdateAttendanceRequest,
    current_faculty: Faculty = Depends(require_faculty),
):
    """Update attendance record (faculty-only)."""
    log.info("update_attendance_request", att_id=att_id, faculty=current_faculty.name)
    try:
        rollNo = payload.rollno
        lectureNo = payload.lecture_no
        course = payload.course

        data, error = AttendanceService.updateAttendance(
            attId=att_id,
            rollNo=rollNo,
            course=course,
            lectureNo=lectureNo,
        )
        if error is not None:
            log.warning("update_attendance_not_found", att_id=att_id, reason=error)
            response = error_response(
                ErrorCode.NOT_FOUND,
                error,
                404
            )
            raise HTTPException(status_code=404, detail=response["error"])

        log.info("update_attendance_success", att_id=att_id)
        return success_response(data)
    except HTTPException:
        raise
    except Exception as e:
        log.error("update_attendance_error", att_id=att_id, error=str(e), exc_info=e)
        response = error_response(
            ErrorCode.INTERNAL_ERROR,
            "Failed to update attendance",
            500
        )
        raise HTTPException(status_code=500, detail=response["error"])


@router.delete("/attendances/{att_id}")
async def delete_attendance_api(
    att_id: int,
    current_faculty: Faculty = Depends(require_faculty),
):
    """Delete attendance record (faculty-only)."""
    log.info("delete_attendance_request", att_id=att_id, faculty=current_faculty.name)
    try:
        success_flag, error = AttendanceService.deleteAttendance(att_id)
        if error is not None:
            log.warning("delete_attendance_not_found", att_id=att_id, reason=error)
            response = error_response(
                ErrorCode.NOT_FOUND,
                error,
                404
            )
            raise HTTPException(status_code=404, detail=response["error"])

        log.info("delete_attendance_success", att_id=att_id)
        return success_response({"message": "Attendance record deleted"})
    except HTTPException:
        raise
    except Exception as e:
        log.error("delete_attendance_error", att_id=att_id, error=str(e), exc_info=e)
        response = error_response(
            ErrorCode.INTERNAL_ERROR,
            "Failed to delete attendance",
            500
        )
        raise HTTPException(status_code=500, detail=response["error"])

