# backend/api/v1/auth_routes_fastapi.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import structlog

from backend.api.v1.validation_models import LoginRequest
from backend.api.error_handler import error_response, success_response, ErrorCode
from backend.security import generate_token, verify_token
from backend.services.auth_service import AuthService


router = APIRouter()
log = structlog.get_logger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


def unauthorized(message: str = "Unauthorized"):
    response = error_response(ErrorCode.UNAUTHORIZED, message, 401)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=response["error"],
    )


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


async def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        unauthorized("Missing Authorization Bearer token")

    if credentials.scheme.lower() != "bearer":
        unauthorized("Invalid authorization scheme")

    payload = verify_token(credentials.credentials)

    if not payload:
        unauthorized("Invalid or expired token")

    return payload


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

        access_token = generate_token(
            user_id=student.rollno,
            role="student",
            is_admin=False,
        )

        return success_response(
            {
                "accessToken": access_token,
                "user": AuthService.serialize_student(student),
                "role": "student",
            }
        )

    if role == "faculty":
        faculty = AuthService.authenticate_faculty(email=email, password=password)

        if not faculty:
            log.warning("login_failed", email=email, role="faculty")
            invalid_credentials()

        access_token = generate_token(
            user_id=faculty.f_id,
            role="faculty",
            is_admin=bool(faculty.is_admin),
        )

        return success_response(
            {
                "accessToken": access_token,
                "user": AuthService.serialize_faculty(faculty),
                "role": "faculty",
            }
        )

    if role is not None:
        response = error_response(
            ErrorCode.BAD_REQUEST,
            "Role must be 'student', 'faculty', or null",
            400,
        )
        raise HTTPException(status_code=400, detail=response["error"])

    # Auto-detect: ưu tiên student trước, sau đó faculty
    student = AuthService.authenticate_student(email=email, password=password)

    if student:
        access_token = generate_token(
            user_id=student.rollno,
            role="student",
            is_admin=False,
        )

        return success_response(
            {
                "accessToken": access_token,
                "user": AuthService.serialize_student(student),
                "role": "student",
            }
        )

    faculty = AuthService.authenticate_faculty(email=email, password=password)

    if faculty:
        access_token = generate_token(
            user_id=faculty.f_id,
            role="faculty",
            is_admin=bool(faculty.is_admin),
        )

        return success_response(
            {
                "accessToken": access_token,
                "user": AuthService.serialize_faculty(faculty),
                "role": "faculty",
            }
        )

    log.warning("login_failed", email=email, role="auto-detect")
    invalid_credentials()


from backend.api.v1.dependencies import get_current_user


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

    unauthorized("Invalid token role")


@router.post("/auth/logout")
async def logout_api():
    # JWT stateless: backend không giữ session nên không cần clear gì ở server.
    return success_response(
        {
            "message": "Logged out successfully",
        }
    )