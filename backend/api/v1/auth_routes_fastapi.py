"""
FastAPI Auth Routes
Migration of Flask auth_routes.py to FastAPI.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.auth_service import AuthService
from backend.security import (
    generate_token,
    generate_refresh_token,
    verify_refresh_token,
)

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str
    role: str = None


class TokenRequest(BaseModel):
    email: str
    password: str


class RefreshTokenRequest(BaseModel):
    refreshToken: str


def success_response(data):
    """Standardized success response."""
    return {"success": True, "data": data, "error": None}


def error_response(code: str, message: str, status_code: int):
    """Standardized error response."""
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message}
    )


@router.post("/auth/login")
async def login_api(payload: LoginRequest):
    """Student/Faculty login with session support."""
    email = payload.email
    password = payload.password
    role = payload.role

    if not email or not password:
        error_response("INVALID_PAYLOAD", "email and password are required", 400)

    if role == "student":
        student = AuthService.authenticateStudent(email=email, password=password)
        if student is None:
            error_response("INVALID_CREDENTIALS", "Invalid login", 401)
        return success_response({
            "role": "student",
            "user": {
                "rollno": student.rollno,
                "name": student.name,
                "email": student.email,
            },
        })

    if role is None:
        student = AuthService.authenticateStudent(email=email, password=password)
        if student is not None:
            return success_response({
                "role": "student",
                "user": {
                    "rollno": student.rollno,
                    "name": student.name,
                    "email": student.email,
                },
            })

    faculty = AuthService.authenticateFaculty(email=email, password=password)
    if faculty is None:
        error_response("INVALID_CREDENTIALS", "Invalid login", 401)

    return success_response({
        "role": "faculty",
        "user": {
            "id": faculty.f_id,
            "name": faculty.name,
            "email": faculty.email,
            "course": faculty.course,
            "isAdmin": bool(faculty.is_admin),
        },
    })


@router.post("/auth/token")
async def get_token_api(payload: TokenRequest):
    """Generate JWT tokens for API authentication."""
    email = payload.email
    password = payload.password

    if not email or not password:
        error_response("INVALID_PAYLOAD", "email and password are required", 400)

    student = AuthService.authenticateStudent(email=email, password=password)
    if student:
        access_token = generate_token(user_id=student.rollno, role="student")
        refresh_token = generate_refresh_token(user_id=student.rollno, role="student")
        return success_response({
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": {
                "rollno": student.rollno,
                "name": student.name,
                "email": student.email,
                "role": "student",
            },
        })

    faculty = AuthService.authenticateFaculty(email=email, password=password)
    if faculty:
        access_token = generate_token(
            user_id=faculty.f_id,
            role="faculty",
            is_admin=bool(faculty.is_admin)
        )
        refresh_token = generate_refresh_token(user_id=faculty.f_id, role="faculty")
        return success_response({
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": {
                "id": faculty.f_id,
                "name": faculty.name,
                "email": faculty.email,
                "course": faculty.course,
                "isAdmin": bool(faculty.is_admin),
                "role": "faculty",
            },
        })

    error_response("INVALID_CREDENTIALS", "Invalid email or password", 401)


@router.post("/auth/refresh")
async def refresh_token_api(payload: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    refresh_token = payload.refreshToken

    if not refresh_token:
        error_response("INVALID_PAYLOAD", "refreshToken is required", 400)

    token_payload = verify_refresh_token(refresh_token)
    if not token_payload:
        error_response("INVALID_TOKEN", "Invalid or expired refresh token", 401)

    user_id = token_payload.get("user_id")
    role = token_payload.get("role")
    is_admin = token_payload.get("is_admin", False)

    access_token = generate_token(user_id=user_id, role=role, is_admin=is_admin)
    return success_response({
        "accessToken": access_token,
    })


@router.get("/auth/me")
async def get_me_api():
    """Get current authenticated user info."""
    error_response("UNAUTHORIZED", "Not logged in - use JWT token in Authorization header", 401)


@router.post("/auth/logout")
async def logout_api():
    """Logout (stateless - no-op for JWT)."""
    return success_response({"message": "Logged out"})
