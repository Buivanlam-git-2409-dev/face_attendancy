"""
Error handling and middleware for FastAPI application.
Provides consistent error responses and logging.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog


log = structlog.get_logger(__name__)


class ErrorCode:
    """Standard error codes."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"


def error_response(
    code: str,
    message: str,
    status_code: int = 400,
    details: dict = None
):
    """Create a standardized error response."""
    error = {
        "code": code,
        "message": message,
    }
    if details:
        error["details"] = details

    return {
        "success": False,
        "data": None,
        "error": error,
    }


def success_response(data=None, status_code: int = 200):
    """Create a standardized success response."""
    return {
        "success": True,
        "data": data,
        "error": None,
    }


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = exc.errors()
    formatted_errors = []

    for error in errors:
        field = ".".join(str(x) for x in error.get("loc", [])[1:])
        msg = error.get("msg", "Invalid value")
        formatted_errors.append({
            "field": field,
            "message": msg,
            "type": error.get("type", "unknown")
        })

    log.warning(
        "validation_error",
        path=request.url.path,
        errors=formatted_errors
    )

    response = error_response(
        ErrorCode.VALIDATION_ERROR,
        "Request validation failed",
        status_code=422,
        details={"errors": formatted_errors}
    )

    return JSONResponse(
        status_code=422,
        content=response
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    log.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=exc
    )

    response = error_response(
        ErrorCode.INTERNAL_ERROR,
        "Internal server error",
        status_code=500
    )

    return JSONResponse(
        status_code=500,
        content=response
    )

