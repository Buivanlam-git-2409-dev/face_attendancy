from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import structlog

from backend.security import verify_token
from backend.services.auth_service import AuthService
from backend.api.error_handler import error_response, ErrorCode

log = structlog.get_logger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)

def unauthorized(message: str = "Unauthorized"):
    response = error_response(ErrorCode.UNAUTHORIZED, message, 401)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=response["error"],
    )

async def get_current_user_payload(
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

async def get_current_user(
    payload: dict = Depends(get_current_user_payload)
):
    user, role = AuthService.get_user_by_token_payload(payload)
    if not user:
        unauthorized("User not found")
    return user, role

async def require_student(
    user_data: tuple = Depends(get_current_user)
):
    user, role = user_data
    if role != "student":
        unauthorized("Student role required")
    return user

async def require_faculty(
    user_data: tuple = Depends(get_current_user)
):
    user, role = user_data
    if role != "faculty":
        unauthorized("Faculty role required")
    return user

async def require_admin(
    user_data: tuple = Depends(get_current_user)
):
    user, role = user_data
    if role != "faculty" or not getattr(user, "is_admin", False):
        unauthorized("Admin privileges required")
    return user
