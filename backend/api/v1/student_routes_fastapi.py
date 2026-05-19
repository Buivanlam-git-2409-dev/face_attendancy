"""
FastAPI Student Routes
Migration of Flask student_routes.py to FastAPI with validation and logging.
"""
from fastapi import APIRouter, HTTPException, Depends
import structlog

from backend.api.v1.validation_models import (
    RegisterStudentRequest,
    StudentResponse,
)
from backend.api.error_handler import error_response, success_response, ErrorCode
from backend.services.attendance_service import AttendanceService
from backend.services.auth_service import AuthService
from backend.services.student_service import StudentService
from backend.api.v1.dependencies import require_faculty, require_student, get_current_user
from backend.models import Student

router = APIRouter()
log = structlog.get_logger(__name__)


@router.post("/students/register", status_code=201)
async def register_student_api(payload: RegisterStudentRequest):
    """Register a new student account (public endpoint)."""
    rollno = payload.rollno
    name = payload.name
    email = payload.email
    password = payload.password
    semester = payload.semester or ""
    pic_path = payload.pic_path or ""

    log.info("student_registration_attempt", rollno=rollno, email=email)

    try:
        student, error = AuthService.registerStudent(
            rollno=int(rollno),
            name=name,
            semester=semester,
            email=email,
            password=password,
            picPath=pic_path,
        )
        if error:
            log.warning("student_registration_failed", rollno=rollno, email=email, reason=error)
            response = error_response(
                ErrorCode.CONFLICT,
                error,
                400
            )
            raise HTTPException(status_code=400, detail=response["error"])

        log.info("student_registration_success", rollno=rollno, email=email)
        return success_response({
            "message": "Student registered successfully",
            "user": {
                "rollno": student.rollno,
                "name": student.name,
                "email": student.email,
            },
        })
    except Exception as e:
        log.error("student_registration_error", rollno=rollno, error=str(e), exc_info=e)
        if isinstance(e, HTTPException):
            raise
        response = error_response(
            ErrorCode.INTERNAL_ERROR,
            "Registration failed",
            400
        )
        raise HTTPException(status_code=400, detail=response["error"])


@router.get("/students")
async def list_students_api(current_faculty: tuple = Depends(require_faculty)):
    """List all students (faculty only)."""
    log.info("list_students_request")
    try:
        students = StudentService.listStudents()
        return success_response(students)
    except Exception as e:
        log.error("list_students_error", error=str(e), exc_info=e)
        response = error_response(
            ErrorCode.INTERNAL_ERROR,
            "Failed to retrieve students",
            500
        )
        raise HTTPException(status_code=500, detail=response["error"])


@router.get("/students/{rollno}")
async def get_student_api(rollno: int, current_user_data: tuple = Depends(get_current_user)):
    """Get student by roll number (faculty or own student)."""
    log.info("get_student_request", rollno=rollno)
    
    current_user, role = current_user_data
    if role == "student" and current_user.rollno != rollno:
        response = error_response(ErrorCode.UNAUTHORIZED, "Cannot access other student data", 403)
        raise HTTPException(status_code=403, detail=response["error"])

    try:
        student = StudentService.getStudentByRollNo(rollno)
        if student is None:
            log.warning("get_student_not_found", rollno=rollno)
            response = error_response(
                ErrorCode.NOT_FOUND,
                "Student not found",
                404
            )
            raise HTTPException(status_code=404, detail=response["error"])

        log.info("get_student_success", rollno=rollno)
        return success_response(student)
    except HTTPException:
        raise
    except Exception as e:
        log.error("get_student_error", rollno=rollno, error=str(e), exc_info=e)
        response = error_response(
            ErrorCode.INTERNAL_ERROR,
            "Failed to retrieve student",
            500
        )
        raise HTTPException(status_code=500, detail=response["error"])


@router.get("/students/{rollno}/attendances")
async def get_student_attendance_api(rollno: int, current_user_data: tuple = Depends(get_current_user)):
    """Get student's attendance records (faculty or own student)."""
    log.info("get_student_attendance_request", rollno=rollno)
    
    current_user, role = current_user_data
    if role == "student" and current_user.rollno != rollno:
        response = error_response(ErrorCode.UNAUTHORIZED, "Cannot access other student data", 403)
        raise HTTPException(status_code=403, detail=response["error"])

    try:
        student = StudentService.getStudentByRollNo(rollno)
        if student is None:
            log.warning("get_student_attendance_not_found", rollno=rollno)
            response = error_response(
                ErrorCode.NOT_FOUND,
                "Student not found",
                404
            )
            raise HTTPException(status_code=404, detail=response["error"])

        data = AttendanceService.listAttendances(rollNo=rollno)
        log.info("get_student_attendance_success", rollno=rollno)
        return success_response(data)
    except HTTPException:
        raise
    except Exception as e:
        log.error("get_student_attendance_error", rollno=rollno, error=str(e), exc_info=e)
        response = error_response(
            ErrorCode.INTERNAL_ERROR,
            "Failed to retrieve attendance",
            500
        )
        raise HTTPException(status_code=500, detail=response["error"])


@router.get("/me/attendances")
async def get_my_attendances_api(current_student: Student = Depends(require_student)):
    """Get current student's attendance records."""
    log.info("get_my_attendances", rollno=current_student.rollno)
    try:
        data = AttendanceService.listAttendances(rollNo=current_student.rollno)
        return success_response(data)
    except Exception as e:
        log.error("get_my_attendances_error", rollno=current_student.rollno, error=str(e))
        response = error_response(
            ErrorCode.INTERNAL_ERROR,
            "Failed to retrieve attendance",
            500
        )
        raise HTTPException(status_code=500, detail=response["error"])

