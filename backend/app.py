"""
Main application entry point for the Facial Recognition Attendance System.

FastAPI is the primary application, providing API routes for the React SPA.
The legacy Flask application is mounted under /legacy for compatibility.

Run:
    uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from backend.models import Role
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.wsgi import WSGIMiddleware

# Ensure project root is in Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.api.error_handler import (  # noqa: E402
    general_exception_handler,
    validation_exception_handler,
)
from backend.api.v1.attendance_routes_fastapi import router as attendance_router  # noqa: E402
from backend.api.v1.auth_routes_fastapi import router as auth_router  # noqa: E402
from backend.api.v1.faculty_routes_fastapi import router as faculty_router  # noqa: E402
from backend.api.v1.recognition_routes_fastapi import router as recognition_router  # noqa: E402
from backend.api.v1.student_routes_fastapi import router as student_router  # noqa: E402
from backend.celery_app import init_celery_config  # noqa: E402
from backend.extensions import db  # noqa: E402
from backend.legacy.flask_app import legacy_flask_app  # noqa: E402
from backend.logging_config import get_logger, init_logging  # noqa: E402


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
log_level = os.getenv("LOG_LEVEL", "INFO")
init_logging(log_level)
log = get_logger(__name__)

def seed_default_roles():
    default_roles = [
        ("STUDENT", "Student user"),
        ("FACULTY", "Faculty user"),
        ("ADMIN", "Administrator user"),
    ]

    for name, description in default_roles:
        existing_role = Role.query.filter_by(name=name).first()

        if not existing_role:
            role = Role(
                name=name,
                description=description,
            )
            db.session.add(role)

    db.session.commit()
# -----------------------------------------------------------------------------
# FastAPI App Lifecycle
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("application_startup")

    # Flask-SQLAlchemy still needs a Flask application context.
    # For production, prefer migrations instead of db.create_all().
    with legacy_flask_app.app_context():
        db.create_all()
        seed_default_roles()
        log.info("database_initialized")

    init_celery_config()
    log.info("celery_initialized")

    yield

    with legacy_flask_app.app_context():
        db.session.remove()

    log.info("application_shutdown")


# -----------------------------------------------------------------------------
# FastAPI Application Initialization
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Facial Recognition Attendance API",
    description="API for the facial recognition attendance system",
    version="1.0.0",
    lifespan=lifespan,
)


# -----------------------------------------------------------------------------
# CORS
# -----------------------------------------------------------------------------
cors_origins = os.getenv(
    "CORS_ALLOW_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------
@app.middleware("http")
async def db_session_middleware(request, call_next):
    """
    Provide Flask app context for Flask-SQLAlchemy while FastAPI is the main app.

    This is a transitional solution. Long-term, move to SQLAlchemy session
    management independent from Flask.
    """
    with legacy_flask_app.app_context():
        try:
            response = await call_next(request)
            return response
        finally:
            db.session.remove()


@app.middleware("http")
async def logging_middleware(request, call_next):
    log.info(
        "request_received",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None,
    )

    response = await call_next(request)

    log.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )

    return response


# -----------------------------------------------------------------------------
# Exception Handlers
# -----------------------------------------------------------------------------
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# -----------------------------------------------------------------------------
# API Routes
# -----------------------------------------------------------------------------
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(student_router, prefix="/api/v1", tags=["Students"])
app.include_router(faculty_router, prefix="/api/v1", tags=["Faculty"])
app.include_router(attendance_router, prefix="/api/v1", tags=["Attendance"])
app.include_router(recognition_router, prefix="/api/v1", tags=["Recognition"])


# -----------------------------------------------------------------------------
# Basic Routes
# -----------------------------------------------------------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "facial-recognition-api",
    }


@app.get("/")
async def root():
    return {
        "message": "Attendance API - Use frontend SPA or /docs for API documentation",
        "docs": "/docs",
        "health": "/health",
        "legacy": "/legacy",
    }


# -----------------------------------------------------------------------------
# Legacy Flask Application
# -----------------------------------------------------------------------------
app.mount("/legacy", WSGIMiddleware(legacy_flask_app))


if __name__ == "__main__":
    import uvicorn

    log.info("starting_server", host="0.0.0.0", port=8000)

    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )