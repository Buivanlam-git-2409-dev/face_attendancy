"""
FastAPI Attendance Routes.

Routes:
- GET /attendances: list attendance records, faculty only.
- GET /attendances/{att_id}: faculty or student owner.
- POST /attendances: mark attendance, faculty only.
- PUT /attendances/{att_id}: update attendance, faculty only.
- DELETE /attendances/{att_id}: delete attendance, faculty only.
"""

from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.api.error_handler import ErrorCode, error_response, success_response
from backend.api.v1.dependencies import get_current_user, require_faculty
from backend.api.v1.validation_models import (
    CreateAttendanceRequest,
    UpdateAttendanceRequest,
)
from backend.models import Faculty
from backend.services.attendance_service import AttendanceService


router = APIRouter()
log = structlog.get_logger(__name__)


def bad_request(message: str):
    response = error_response(ErrorCode.BAD_REQUEST, message, 400)
    raise HTTPException(status_code=400, detail=response["error"])


def forbidden(message: str):
    response = error_response(ErrorCode.FORBIDDEN, message, 403)
    raise HTTPException(status_code=403, detail=response["error"])


def not_found(message: str):
    response = error_response(ErrorCode.NOT_FOUND, message, 404)
    raise HTTPException(status_code=404, detail=response["error"])


def internal_error(message: str):
    response = error_response(ErrorCode.INTERNAL_ERROR, message, 500)
    raise HTTPException(status_code=500, detail=response["error"])


def parse_optional_int(value: Optional[str], field_name: str) -> Optional[int]:
    if value is None or value == "":
        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        bad_request(f"{field_name} must be an integer")


def get_record_rollno(record) -> Optional[int]:
    if isinstance(record, dict):
        return record.get("rollno")

    return getattr(record, "rollno", None)


@router.get("/attendances")
async def list_attendances_api(
    rollno: Optional[str] = Query(None),
    lecture_no: Optional[str] = Query(None),
    course: Optional[str] = Query(None),
    marked_by: Optional[str] = Query(None),
    current_faculty: Faculty = Depends(require_faculty),
):
    """List attendance records with optional filters. Faculty only."""
    log.info(
        "list_attendances_request",
        rollno=rollno,
        course=course,
        lecture_no=lecture_no,
        faculty=current_faculty.name,
    )

    try:
        rollno_int = parse_optional_int(rollno, "rollno")
        lecture_no_int = parse_optional_int(lecture_no, "lecture_no")

        data = AttendanceService.listAttendances(
            rollNo=rollno_int,
            course=course,
            lectureNo=lecture_no_int,
            markedBy=marked_by,
        )

        log.info(
            "list_attendances_success",
            count=len(data) if isinstance(data, list) else 0,
        )

        return success_response(data)

    except HTTPException:
        raise
    except Exception as e:
        log.error("list_attendances_error", error=str(e), exc_info=e)
        internal_error("Failed to retrieve attendance records")


@router.get("/attendances/{att_id}")
async def get_attendance_api(
    att_id: int,
    current_user_data: tuple = Depends(get_current_user),
):
    """Get specific attendance record. Faculty or student owner only."""
    log.info("get_attendance_request", att_id=att_id)

    try:
        data = AttendanceService.getAttendance(attId=att_id)

        if not data:
            log.warning("get_attendance_not_found", att_id=att_id)
            not_found("Attendance record not found")

        current_user, role = current_user_data
        record_rollno = get_record_rollno(data)

        if role == "student" and record_rollno != current_user.rollno:
            log.warning(
                "get_attendance_forbidden",
                att_id=att_id,
                student_rollno=current_user.rollno,
                record_rollno=record_rollno,
            )
            forbidden("Access denied to this record")

        return success_response(data)

    except HTTPException:
        raise
    except Exception as e:
        log.error("get_attendance_error", att_id=att_id, error=str(e), exc_info=e)
        internal_error("Failed to retrieve attendance record")


@router.post("/attendances", status_code=201)
async def mark_attendance_api(
    payload: CreateAttendanceRequest,
    current_faculty: Faculty = Depends(require_faculty),
):
    """Mark attendance for a student. Faculty only."""
    log.info(
        "mark_attendance_request",
        rollno=payload.rollno,
        course=payload.course,
        faculty=current_faculty.name,
    )

    try:
        rollno = payload.rollno
        lecture_no = payload.lecture_no or 0
        course = payload.course
        marked_by = current_faculty.name

        data, error = AttendanceService.markAttendance(
            rollNo=rollno,
            course=course,
            lectureNo=lecture_no,
            markedBy=marked_by,
        )

        if error is not None:
            log.warning("mark_attendance_failed", rollno=rollno, reason=error)
            response = error_response(ErrorCode.CONFLICT, error, 409)
            raise HTTPException(status_code=409, detail=response["error"])

        log.info("mark_attendance_success", rollno=rollno, course=course)
        return success_response(data)

    except HTTPException:
        raise
    except Exception as e:
        log.error(
            "mark_attendance_error",
            rollno=payload.rollno,
            error=str(e),
            exc_info=e,
        )
        internal_error("Failed to mark attendance")


@router.put("/attendances/{att_id}")
async def update_attendance_api(
    att_id: int,
    payload: UpdateAttendanceRequest,
    current_faculty: Faculty = Depends(require_faculty),
):
    """Update attendance record. Faculty only."""
    log.info(
        "update_attendance_request",
        att_id=att_id,
        faculty=current_faculty.name,
    )

    try:
        data, error = AttendanceService.updateAttendance(
            attId=att_id,
            rollNo=payload.rollno,
            course=payload.course,
            lectureNo=payload.lecture_no,
        )

        if error is not None:
            log.warning("update_attendance_not_found", att_id=att_id, reason=error)
            response = error_response(ErrorCode.NOT_FOUND, error, 404)
            raise HTTPException(status_code=404, detail=response["error"])

        log.info("update_attendance_success", att_id=att_id)
        return success_response(data)

    except HTTPException:
        raise
    except Exception as e:
        log.error("update_attendance_error", att_id=att_id, error=str(e), exc_info=e)
        internal_error("Failed to update attendance")


@router.delete("/attendances/{att_id}")
async def delete_attendance_api(
    att_id: int,
    current_faculty: Faculty = Depends(require_faculty),
):
    """Delete attendance record. Faculty only."""
    log.info(
        "delete_attendance_request",
        att_id=att_id,
        faculty=current_faculty.name,
    )

    try:
        success_flag, error = AttendanceService.deleteAttendance(att_id)

        if error is not None:
            log.warning("delete_attendance_not_found", att_id=att_id, reason=error)
            response = error_response(ErrorCode.NOT_FOUND, error, 404)
            raise HTTPException(status_code=404, detail=response["error"])

        log.info("delete_attendance_success", att_id=att_id)
        return success_response({"message": "Attendance record deleted"})

    except HTTPException:
        raise
    except Exception as e:
        log.error("delete_attendance_error", att_id=att_id, error=str(e), exc_info=e)
        internal_error("Failed to delete attendance")