"""
Error handling and middleware for FastAPI application.

Provides consistent success/error responses and global exception handlers.
"""

from typing import Any, Dict, Optional

import structlog
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


log = structlog.get_logger(__name__)


class ErrorCode:
    """Standard API error codes."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    BAD_REQUEST = "BAD_REQUEST"


def error_response(
    code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Note:
    The status_code parameter is kept for backward compatibility with existing
    route code. HTTP status is still controlled by HTTPException/JSONResponse.
    """
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


def success_response(
    data: Any = None,
    status_code: int = 200,
) -> Dict[str, Any]:
    """
    Create a standardized success response.

    Note:
    The status_code parameter is kept for backward compatibility.
    HTTP status is controlled by the route decorator or JSONResponse.
    """
    return {
        "success": True,
        "data": data,
        "error": None,
    }


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """Handle Pydantic validation errors."""
    formatted_errors = []

    for error in exc.errors():
        field = ".".join(str(item) for item in error.get("loc", [])[1:])
        message = error.get("msg", "Invalid value")

        formatted_errors.append(
            {
                "field": field,
                "message": message,
                "type": error.get("type", "unknown"),
            }
        )

    log.warning(
        "validation_error",
        path=request.url.path,
        errors=formatted_errors,
    )

    response = error_response(
        ErrorCode.VALIDATION_ERROR,
        "Request validation failed",
        status_code=422,
        details={"errors": formatted_errors},
    )

    return JSONResponse(
        status_code=422,
        content=response,
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    """Handle unhandled exceptions."""
    log.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=exc,
    )

    response = error_response(
        ErrorCode.INTERNAL_ERROR,
        "Internal server error",
        status_code=500,
    )

    return JSONResponse(
        status_code=500,
        content=response,
    )