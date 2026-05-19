"""
FastAPI Attendance Routes
Migration of Flask attendance_routes.py to FastAPI.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from backend.services.attendance_service import AttendanceService

router = APIRouter()


class MarkAttendanceRequest(BaseModel):
    rollno: int
    lecture_no: int
    course: str


class UpdateAttendanceRequest(BaseModel):
    rollno: Optional[int] = None
    lecture_no: Optional[int] = None
    course: Optional[str] = None


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


@router.get("/attendances")
async def list_attendances_api(
    rollno: Optional[str] = Query(None),
    lecture_no: Optional[str] = Query(None),
    course: Optional[str] = Query(None),
    marked_by: Optional[str] = Query(None),
):
    """List attendance records with optional filters (faculty-only)."""
    # TODO: Add JWT faculty verification
    rollno_int = parse_int(rollno)
    lecture_no_int = parse_int(lecture_no)
    
    data = AttendanceService.listAttendances(
        rollNo=rollno_int,
        course=course,
        lectureNo=lecture_no_int,
        markedBy=marked_by,
    )
    return success_response(data)


@router.post("/attendances", status_code=201)
async def mark_attendance_api(payload: MarkAttendanceRequest):
    """Mark attendance for a student (faculty-only)."""
    # TODO: Add JWT faculty verification and extract marked_by from token
    rollNo = payload.rollno
    lectureNo = payload.lecture_no
    course = payload.course

    if rollNo is None or lectureNo is None or not course:
        error_response("INVALID_PAYLOAD", "rollno, course, lecture_no are required", 400)

    marked_by = "System"  # TODO: Extract from JWT token
    data, error = AttendanceService.markAttendance(
        rollNo=rollNo,
        course=course,
        lectureNo=lectureNo,
        markedBy=marked_by,
    )
    if error is not None:
        error_response("ALREADY_MARKED", error, 409)
    return success_response(data)


@router.put("/attendances/{att_id}")
async def update_attendance_api(att_id: int, payload: UpdateAttendanceRequest):
    """Update attendance record (faculty-only)."""
    # TODO: Add JWT faculty verification
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
        error_response("NOT_FOUND", error, 404)
    return success_response(data)


@router.delete("/attendances/{att_id}")
async def delete_attendance_api(att_id: int):
    """Delete attendance record (faculty-only)."""
    # TODO: Add JWT faculty verification
    success, error = AttendanceService.deleteAttendance(att_id)
    if error is not None:
        error_response("NOT_FOUND", error, 404)
    return success_response({"message": "Attendance record deleted"})
