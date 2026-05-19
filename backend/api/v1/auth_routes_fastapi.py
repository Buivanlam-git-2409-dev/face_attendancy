from fastapi import APIRouter, Depends, HTTPException, status
import structlog

from backend.api.error_handler import ErrorCode, error_response, success_response
from backend.api.v1.dependencies import get_current_user
from backend.api.v1.validation_models import LoginRequest
from backend.security import generate_token
from backend.services.auth_service import AuthService


router = APIRouter()
log = structlog.get_logger(__name__)


def invalid_credentials():
    response = error_response(
        ErrorCode.INVALID_CREDENTIALS,
        "Invalid email or password",
        401,
    )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=response["error"],
    )


def bad_request(message: str):
    response = error_response(
        ErrorCode.BAD_REQUEST,
        message,
        400,
    )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=response["error"],
    )


def build_login_response(user, role: str):
    if role == "student":
        access_token = generate_token(
            user_id=user.rollno,
            role="student",
            is_admin=False,
        )

        return success_response(
            {
                "accessToken": access_token,
                "user": AuthService.serialize_student(user),
                "role": "student",
            }
        )

    if role == "faculty":
        access_token = generate_token(
            user_id=user.f_id,
            role="faculty",
            is_admin=bool(user.is_admin),
        )

        return success_response(
            {
                "accessToken": access_token,
                "user": AuthService.serialize_faculty(user),
                "role": "faculty",
            }
        )

    bad_request("Invalid role")


@router.post("/auth/login")
async def login_api(payload: LoginRequest):
    email = payload.email
    password = payload.password
    role = payload.role

    log.info("login_attempt", email=email, role=role or "auto-detect")

    if role == "student":
        student = AuthService.authenticate_student(email=email, password=password)

        if not student:
            log.warning("login_failed", email=email, role="student")
            invalid_credentials()

        return build_login_response(student, "student")

    if role == "faculty":
        faculty = AuthService.authenticate_faculty(email=email, password=password)

        if not faculty:
            log.warning("login_failed", email=email, role="faculty")
            invalid_credentials()

        return build_login_response(faculty, "faculty")

    if role is not None:
        bad_request("Role must be 'student', 'faculty', or null")

    # Auto-detect: ưu tiên student trước, sau đó faculty
    student = AuthService.authenticate_student(email=email, password=password)

    if student:
        return build_login_response(student, "student")

    faculty = AuthService.authenticate_faculty(email=email, password=password)

    if faculty:
        return build_login_response(faculty, "faculty")

    log.warning("login_failed", email=email, role="auto-detect")
    invalid_credentials()


@router.get("/auth/me")
async def get_me_api(current_user_data: tuple = Depends(get_current_user)):
    user, role = current_user_data

    if role == "student":
        return success_response(
            {
                "user": AuthService.serialize_student(user),
                "role": "student",
            }
        )

    if role == "faculty":
        return success_response(
            {
                "user": AuthService.serialize_faculty(user),
                "role": "faculty",
            }
        )

    bad_request("Invalid token role")


@router.post("/auth/logout")
async def logout_api():
    # JWT stateless: backend không giữ session nên không cần clear gì ở server.
    return success_response(
        {
            "message": "Logged out successfully",
        }
    )