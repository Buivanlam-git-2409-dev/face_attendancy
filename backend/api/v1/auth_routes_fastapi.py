"""
FastAPI Auth Routes
Migration of Flask auth_routes.py to FastAPI with validation and logging.
"""
from fastapi import APIRouter, HTTPException
import structlog

from backend.api.v1.validation_models import (
    LoginRequest,
    TokenRequest,
    RefreshTokenRequest,
)
from backend.api.error_handler import error_response, success_response, ErrorCode
from backend.services.auth_service import AuthService
from backend.security import (
    generate_token,
    generate_refresh_token,
    verify_refresh_token,
)

router = APIRouter()
log = structlog.get_logger(__name__)


@router.post("/auth/login")
async def login_api(payload: LoginRequest):
    """Student/Faculty login with session support."""
    email = payload.email
    password = payload.password
    role = payload.role

    log.info("login_attempt", email=email, role=role or "auto-detect")

    if role == "student":
        student = AuthService.authenticateStudent(email=email, password=password)
        if student is None:
            log.warning("login_failed", email=email, reason="invalid_credentials", role="student")
            response = error_response(
                ErrorCode.INVALID_CREDENTIALS,
                "Invalid login credentials",
                400
            )
            raise HTTPException(status_code=400, detail=response["error"])

        log.info("login_success", email=email, rollno=student.rollno, role="student")
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
            log.info("login_success", email=email, rollno=student.rollno, role="student")
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
        log.warning("login_failed", email=email, reason="invalid_credentials", role="faculty")
        response = error_response(
            ErrorCode.INVALID_CREDENTIALS,
            "Invalid login credentials",
            401
        )
        raise HTTPException(status_code=401, detail=response["error"])

    log.info("login_success", email=email, f_id=faculty.f_id, role="faculty")
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

    log.info("token_request", email=email)

    student = AuthService.authenticateStudent(email=email, password=password)
    if student:
        access_token = generate_token(user_id=student.rollno, role="student")
        refresh_token = generate_refresh_token(user_id=student.rollno, role="student")
        log.info("token_generated", email=email, rollno=student.rollno, role="student")
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
        log.info("token_generated", email=email, f_id=faculty.f_id, role="faculty")
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

    log.warning("token_failed", email=email, reason="invalid_credentials")
    response = error_response(
        ErrorCode.INVALID_CREDENTIALS,
        "Invalid email or password",
        401
    )
    raise HTTPException(status_code=401, detail=response["error"])


@router.post("/auth/refresh")
async def refresh_token_api(payload: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    refresh_token = payload.refreshToken

    log.info("refresh_token_request")

    token_payload = verify_refresh_token(refresh_token)
    if not token_payload:
        log.warning("refresh_token_failed", reason="invalid_or_expired_token")
        response = error_response(
            ErrorCode.UNAUTHORIZED,
            "Invalid or expired refresh token",
            401
        )
        raise HTTPException(status_code=401, detail=response["error"])

    user_id = token_payload.get("user_id")
    role = token_payload.get("role")
    is_admin = token_payload.get("is_admin", False)

    access_token = generate_token(user_id=user_id, role=role, is_admin=is_admin)
    log.info("refresh_token_success", user_id=user_id, role=role)
    return success_response({
        "accessToken": access_token,
    })


@router.get("/auth/me")
async def get_me_api():
    """Get current authenticated user info."""
    log.warning("get_me_called_without_auth")
    response = error_response(
        ErrorCode.UNAUTHORIZED,
        "Not logged in - use JWT token in Authorization header",
        401
    )
    raise HTTPException(status_code=401, detail=response["error"])


@router.post("/auth/logout")
async def logout_api():
    """Logout (stateless - no-op for JWT)."""
    log.info("logout")
    return success_response({"message": "Logged out"})
