"""
FastAPI Student Routes
Migration of Flask student_routes.py to FastAPI.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.attendance_service import AttendanceService
from backend.services.auth_service import AuthService
from backend.services.student_service import StudentService

router = APIRouter()


class RegisterStudentRequest(BaseModel):
    rollno: int
    name: str
    email: str
    password: str
    semester: str = ""
    pic_path: str = ""


def success_response(data):
    """Standardized success response."""
    return {"success": True, "data": data, "error": None}


def error_response(code: str, message: str, status_code: int):
    """Standardized error response."""
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message}
    )


@router.post("/students/register", status_code=201)
async def register_student_api(payload: RegisterStudentRequest):
    """Register a new student account (public endpoint)."""
    rollno = payload.rollno
    name = payload.name
    email = payload.email
    password = payload.password
    semester = payload.semester or ""
    pic_path = payload.pic_path or ""

    if not all([rollno, name, email, password]):
        error_response("INVALID_PAYLOAD", "rollno, name, email, and password are required", 400)

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
            error_response("REGISTRATION_FAILED", error, 400)
        return success_response({
            "message": "Student registered successfully",
            "user": {
                "rollno": student.rollno,
                "name": student.name,
                "email": student.email,
            },
        })
    except Exception as e:
        error_response("REGISTRATION_ERROR", str(e), 400)


@router.get("/students")
async def list_students_api():
    """List all students (faculty only)."""
    # TODO: Add JWT faculty verification
    return success_response(StudentService.listStudents())


@router.get("/students/{rollno}")
async def get_student_api(rollno: int):
    """Get student by roll number (faculty only)."""
    # TODO: Add JWT faculty verification
    student = StudentService.getStudentByRollNo(rollno)
    if student is None:
        error_response("NOT_FOUND", "Student not found", 404)
    return success_response(student)


@router.get("/students/{rollno}/attendances")
async def get_student_attendance_api(rollno: int):
    """Get student's attendance records (faculty only)."""
    # TODO: Add JWT faculty verification
    student = StudentService.getStudentByRollNo(rollno)
    if student is None:
        error_response("NOT_FOUND", "Student not found", 404)
    data = AttendanceService.listAttendances(rollNo=rollno)
    return success_response(data)


@router.get("/me/attendances")
async def get_my_attendances_api():
    """Get current student's attendance records."""
    # TODO: Add JWT student verification and extract rollno from token
    error_response("UNAUTHORIZED", "JWT token required in Authorization header", 401)
