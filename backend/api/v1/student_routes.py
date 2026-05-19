from flask import session, request

from backend.api.v1 import v1Blueprint
from backend.api.v1.responses import errorResponse, successResponse
from backend.services.attendance_service import AttendanceService
from backend.services.auth_service import AuthService
from backend.services.student_service import StudentService
from backend.security import require_faculty, require_student, require_jwt


def ensureFacultySession():
    if "fty_logged_in" not in session:
        return errorResponse("UNAUTHORIZED", "Faculty authentication required", 401)
    return None


def ensureStudentSession():
    if "std_logged_in" not in session:
        return errorResponse("UNAUTHORIZED", "Student authentication required", 401)
    return None


@v1Blueprint.route("/students/register", methods=["POST"])
def registerStudentApi():
    """Register a new student account (public endpoint)"""
    payload = request.get_json(silent=True) or {}
    rollno = payload.get("rollno")
    name = payload.get("name")
    semester = payload.get("semester")
    email = payload.get("email")
    password = payload.get("password")
    pic_path = payload.get("pic_path", "")

    if not all([rollno, name, email, password]):
        return errorResponse("INVALID_PAYLOAD", "rollno, name, email, and password are required", 400)

    try:
        student, error = AuthService.registerStudent(
            rollno=int(rollno),
            name=name,
            semester=semester or "",
            email=email,
            password=password,
            picPath=pic_path,
        )
        if error:
            return errorResponse("REGISTRATION_FAILED", error, 400)
        return successResponse({
            "message": "Student registered successfully",
            "user": {
                "rollno": student.rollno,
                "name": student.name,
                "email": student.email,
            },
        }, statusCode=201)
    except Exception as e:
        return errorResponse("REGISTRATION_ERROR", str(e), 400)


@v1Blueprint.route("/students", methods=["GET"])
def listStudentsApi():
    authError = ensureFacultySession()
    if authError is not None:
        return authError
    return successResponse(StudentService.listStudents())


@v1Blueprint.route("/students/<int:rollNo>", methods=["GET"])
def getStudentApi(rollNo: int):
    authError = ensureFacultySession()
    if authError is not None:
        return authError

    student = StudentService.getStudentByRollNo(rollNo)
    if student is None:
        return errorResponse("NOT_FOUND", "Student not found", 404)
    return successResponse(student)


@v1Blueprint.route("/students/<int:rollNo>/attendances", methods=["GET"])
def getStudentAttendanceApi(rollNo: int):
    authError = ensureFacultySession()
    if authError is not None:
        return authError

    student = StudentService.getStudentByRollNo(rollNo)
    if student is None:
        return errorResponse("NOT_FOUND", "Student not found", 404)
    data = AttendanceService.listAttendances(rollNo=rollNo)
    return successResponse(data)


@v1Blueprint.route("/me/attendances", methods=["GET"])
def getMyAttendancesApi():
    authError = ensureStudentSession()
    if authError is not None:
        return authError

    rollNo = session.get("roll_no")
    data = AttendanceService.listAttendances(rollNo=rollNo)
    return successResponse(data)
