from flask import request, session

from backend.api.v1 import v1Blueprint
from backend.api.v1.responses import errorResponse, successResponse
from backend.services.auth_service import AuthService
from models import Faculty
from backend.extensions import db


def ensureFacultySession():
    if "fty_logged_in" not in session:
        return errorResponse("UNAUTHORIZED", "Faculty authentication required", 401)
    return None


def ensureAdminSession():
    if "fty_logged_in" not in session:
        return errorResponse("UNAUTHORIZED", "Faculty authentication required", 401)
    if not session.get("is_admin", False):
        return errorResponse("FORBIDDEN", "Admin access required", 403)
    return None


def serializeFaculty(faculty: Faculty):
    """Convert Faculty model to dict"""
    return {
        "id": faculty.f_id,
        "name": faculty.name,
        "email": faculty.email,
        "course": faculty.course,
        "isAdmin": bool(faculty.is_admin),
        "registeredOn": faculty.registered_on.isoformat() if faculty.registered_on else None,
    }


@v1Blueprint.route("/faculty", methods=["GET"])
def listFacultyApi():
    """List all faculty members (faculty-only)"""
    authError = ensureFacultySession()
    if authError is not None:
        return authError

    faculty_list = Faculty.query.all()
    return successResponse([serializeFaculty(f) for f in faculty_list])


@v1Blueprint.route("/faculty/<int:facultyId>", methods=["GET"])
def getFacultyApi(facultyId: int):
    """Get single faculty member (faculty-only)"""
    authError = ensureFacultySession()
    if authError is not None:
        return authError

    faculty = Faculty.query.filter_by(f_id=facultyId).first()
    if not faculty:
        return errorResponse("NOT_FOUND", "Faculty member not found", 404)
    return successResponse(serializeFaculty(faculty))


@v1Blueprint.route("/faculty", methods=["POST"])
def createFacultyApi():
    """Create new faculty member (admin-only)"""
    authError = ensureAdminSession()
    if authError is not None:
        return authError

    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    course = payload.get("course")
    email = payload.get("email")
    password = payload.get("password")
    is_admin = payload.get("isAdmin", False)

    if not all([name, email, password]):
        return errorResponse("INVALID_PAYLOAD", "name, email, and password are required", 400)

    faculty, error = AuthService.registerFaculty(
        name=name,
        course=course or "",
        email=email,
        password=password,
        isAdmin=bool(is_admin),
    )
    if error:
        return errorResponse("REGISTRATION_FAILED", error, 400)
    return successResponse(serializeFaculty(faculty), statusCode=201)


@v1Blueprint.route("/faculty/<int:facultyId>", methods=["PUT"])
def updateFacultyApi(facultyId: int):
    """Update faculty member (admin-only or own profile for faculty)"""
    authError = ensureFacultySession()
    if authError is not None:
        return authError

    current_faculty_id = session.get("fty_id")
    is_admin = session.get("is_admin", False)
    
    if facultyId != current_faculty_id and not is_admin:
        return errorResponse("FORBIDDEN", "Cannot update other faculty profiles", 403)

    faculty = Faculty.query.filter_by(f_id=facultyId).first()
    if not faculty:
        return errorResponse("NOT_FOUND", "Faculty member not found", 404)

    payload = request.get_json(silent=True) or {}
    
    if "name" in payload:
        faculty.name = payload.get("name")
    if "course" in payload:
        faculty.course = payload.get("course")
    if "email" in payload:
        faculty.email = payload.get("email")
    if is_admin and "isAdmin" in payload:
        faculty.is_admin = bool(payload.get("isAdmin"))

    db.session.commit()
    return successResponse(serializeFaculty(faculty))


@v1Blueprint.route("/faculty/<int:facultyId>", methods=["DELETE"])
def deleteFacultyApi(facultyId: int):
    """Delete faculty member (admin-only)"""
    authError = ensureAdminSession()
    if authError is not None:
        return authError

    faculty = Faculty.query.filter_by(f_id=facultyId).first()
    if not faculty:
        return errorResponse("NOT_FOUND", "Faculty member not found", 404)

    db.session.delete(faculty)
    db.session.commit()
    return successResponse({"message": "Faculty member deleted"})
