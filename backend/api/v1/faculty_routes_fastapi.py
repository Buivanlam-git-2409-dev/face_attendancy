"""
FastAPI Faculty Routes
Migration of Flask faculty_routes.py to FastAPI.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

from backend.services.auth_service import AuthService
from backend.models import Faculty
from backend.extensions import db

router = APIRouter()


class CreateFacultyRequest(BaseModel):
    name: str
    email: str
    password: str
    course: str = ""
    isAdmin: bool = False


class UpdateFacultyRequest(BaseModel):
    name: str = None
    email: str = None
    course: str = None
    isAdmin: bool = None


def serialize_faculty(faculty: Faculty):
    """Convert Faculty model to dict."""
    return {
        "id": faculty.f_id,
        "name": faculty.name,
        "email": faculty.email,
        "course": faculty.course,
        "isAdmin": bool(faculty.is_admin),
        "registeredOn": faculty.registered_on.isoformat() if faculty.registered_on else None,
    }


def success_response(data):
    """Standardized success response."""
    return {"success": True, "data": data, "error": None}


def error_response(code: str, message: str, status_code: int):
    """Standardized error response."""
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message}
    )


@router.get("/faculty")
async def list_faculty_api():
    """List all faculty members (faculty-only)."""
    # TODO: Add JWT faculty verification
    faculty_list = Faculty.query.all()
    return success_response([serialize_faculty(f) for f in faculty_list])


@router.get("/faculty/{faculty_id}")
async def get_faculty_api(faculty_id: int):
    """Get single faculty member (faculty-only)."""
    # TODO: Add JWT faculty verification
    faculty = Faculty.query.filter_by(f_id=faculty_id).first()
    if not faculty:
        error_response("NOT_FOUND", "Faculty member not found", 404)
    return success_response(serialize_faculty(faculty))


@router.post("/faculty", status_code=201)
async def create_faculty_api(payload: CreateFacultyRequest):
    """Create new faculty member (admin-only)."""
    # TODO: Add JWT admin verification
    name = payload.name
    course = payload.course or ""
    email = payload.email
    password = payload.password
    is_admin = payload.isAdmin or False

    if not all([name, email, password]):
        error_response("INVALID_PAYLOAD", "name, email, and password are required", 400)

    faculty, error = AuthService.registerFaculty(
        name=name,
        course=course,
        email=email,
        password=password,
        isAdmin=bool(is_admin),
    )
    if error:
        error_response("REGISTRATION_FAILED", error, 400)
    return success_response(serialize_faculty(faculty))


@router.put("/faculty/{faculty_id}")
async def update_faculty_api(faculty_id: int, payload: UpdateFacultyRequest):
    """Update faculty member (admin-only or own profile for faculty)."""
    # TODO: Add JWT verification and extract current_faculty_id from token
    faculty = Faculty.query.filter_by(f_id=faculty_id).first()
    if not faculty:
        error_response("NOT_FOUND", "Faculty member not found", 404)

    if payload.name is not None:
        faculty.name = payload.name
    if payload.email is not None:
        faculty.email = payload.email
    if payload.course is not None:
        faculty.course = payload.course
    if payload.isAdmin is not None:
        # TODO: Only allow if current user is admin
        faculty.is_admin = bool(payload.isAdmin)

    db.session.commit()
    return success_response(serialize_faculty(faculty))


@router.delete("/faculty/{faculty_id}")
async def delete_faculty_api(faculty_id: int):
    """Delete faculty member (admin-only)."""
    # TODO: Add JWT admin verification
    faculty = Faculty.query.filter_by(f_id=faculty_id).first()
    if not faculty:
        error_response("NOT_FOUND", "Faculty member not found", 404)

    db.session.delete(faculty)
    db.session.commit()
    return success_response({"message": "Faculty member deleted"})
