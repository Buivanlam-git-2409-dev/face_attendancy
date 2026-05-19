"""
FastAPI Student Routes.

Routes:
- POST /students/register: register new student account.
- GET /students: faculty only.
- GET /students/{rollno}: faculty or the student owner.
- GET /students/{rollno}/attendances: faculty or the student owner.
- GET /me/attendances: current student only.
"""

from fastapi import APIRouter, Depends, HTTPException
import structlog

from backend.api.error_handler import ErrorCode, error_response, success_response
from backend.api.v1.dependencies import get_current_user, require_faculty, require_student
from backend.api.v1.validation_models import RegisterStudentRequest
from backend.models import Faculty, Student
from backend.services.attendance_service import AttendanceService
from backend.services.auth_service import AuthService
from backend.services.student_service import StudentService


router = APIRouter()
log = structlog.get_logger(__name__)


def forbidden(message: str):
    response = error_response(ErrorCode.FORBIDDEN, message, 403)
    raise HTTPException(status_code=403, detail=response["error"])


def not_found(message: str):
    response = error_response(ErrorCode.NOT_FOUND, message, 404)
    raise HTTPException(status_code=404, detail=response["error"])


def internal_error(message: str):
    response = error_response(ErrorCode.INTERNAL_ERROR, message, 500)
    raise HTTPException(status_code=500, detail=response["error"])


@router.post("/students/register", status_code=201)
async def register_student_api(payload: RegisterStudentRequest):
    """
    Register a new student account.

    Current mode: public endpoint for demo/MVP.
    Production recommendation: restrict this endpoint to faculty/admin.
    """
    rollno = payload.rollno
    name = payload.name
    email = payload.email
    password = payload.password
    semester = payload.semester or ""
    pic_path = payload.pic_path or ""

    log.info("student_registration_attempt", rollno=rollno, email=email)

    try:
        student, error = AuthService.register_student(
            rollno=int(rollno),
            name=name,
            semester=semester,
            email=email,
            password=password,
            pic_path=pic_path,
        )

        if error:
            log.warning(
                "student_registration_failed",
                rollno=rollno,
                email=email,
                reason=error,
            )

            response = error_response(
                ErrorCode.CONFLICT,
                error,
                409,
            )
            raise HTTPException(status_code=409, detail=response["error"])

        log.info("student_registration_success", rollno=rollno, email=email)

        return success_response(
            {
                "message": "Student registered successfully",
                "user": {
                    "rollno": student.rollno,
                    "name": student.name,
                    "email": student.email,
                },
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(
            "student_registration_error",
            rollno=rollno,
            error=str(e),
            exc_info=e,
        )
        response = error_response(
            ErrorCode.INTERNAL_ERROR,
            "Registration failed",
            500,
        )
        raise HTTPException(status_code=500, detail=response["error"])


@router.get("/students")
async def list_students_api(current_faculty: Faculty = Depends(require_faculty)):
    """List all students. Faculty only."""
    log.info("list_students_request", faculty=current_faculty.name)

    try:
        students = StudentService.listStudents()
        return success_response(students)

    except Exception as e:
        log.error("list_students_error", error=str(e), exc_info=e)
        internal_error("Failed to retrieve students")


@router.get("/students/{rollno}")
async def get_student_api(
    rollno: int,
    current_user_data: tuple = Depends(get_current_user),
):
    """Get student by roll number. Faculty or student owner only."""
    log.info("get_student_request", rollno=rollno)

    current_user, role = current_user_data

    if role == "student" and current_user.rollno != rollno:
        log.warning(
            "get_student_forbidden",
            requested_rollno=rollno,
            current_rollno=current_user.rollno,
        )
        forbidden("Cannot access other student data")

    try:
        student = StudentService.getStudentByRollNo(rollno)

        if student is None:
            log.warning("get_student_not_found", rollno=rollno)
            not_found("Student not found")

        log.info("get_student_success", rollno=rollno)
        return success_response(student)

    except HTTPException:
        raise
    except Exception as e:
        log.error("get_student_error", rollno=rollno, error=str(e), exc_info=e)
        internal_error("Failed to retrieve student")


@router.get("/students/{rollno}/attendances")
async def get_student_attendance_api(
    rollno: int,
    current_user_data: tuple = Depends(get_current_user),
):
    """Get student's attendance records. Faculty or student owner only."""
    log.info("get_student_attendance_request", rollno=rollno)

    current_user, role = current_user_data

    if role == "student" and current_user.rollno != rollno:
        log.warning(
            "get_student_attendance_forbidden",
            requested_rollno=rollno,
            current_rollno=current_user.rollno,
        )
        forbidden("Cannot access other student data")

    try:
        student = StudentService.getStudentByRollNo(rollno)

        if student is None:
            log.warning("get_student_attendance_not_found", rollno=rollno)
            not_found("Student not found")

        data = AttendanceService.listAttendances(rollNo=rollno)

        log.info(
            "get_student_attendance_success",
            rollno=rollno,
            count=len(data),
        )

        return success_response(data)
    except HTTPException:
        raise
    except Exception as e:
        log.error(
            "get_student_attendance_error",
            rollno=rollno,
            error=str(e),
            exc_info=e,
        )
        internal_error("Failed to retrieve attendance")


@router.get("/me/attendances")
async def get_my_attendances_api(current_student: Student = Depends(require_student)):
    """Get current student's attendance records."""
    log.info("get_my_attendances", rollno=current_student.rollno)

    try:
        data = AttendanceService.listAttendances(rollNo=current_student.rollno)
        return success_response(data)
    except Exception as e:
        log.error(
            "get_my_attendances_error",
            rollno=current_student.rollno,
            error=str(e),
            exc_info=e,
        )
        internal_error("Failed to retrieve attendance")