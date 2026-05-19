"""
Main application entry point for the Facial Recognition Attendance System.

FastAPI is the primary application, providing modern async API routes for the React SPA.
The legacy Flask application is mounted under /legacy for compatibility.

Run:
    uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.middleware.wsgi import WSGIMiddleware

# Ensure backend is in the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.logging_config import init_logging, get_logger
from backend.celery_app import init_celery_config
from backend.extensions import db
from backend.legacy.flask_app import legacy_flask_app
from backend.api.v1.auth_routes_fastapi import router as auth_router
from backend.api.v1.student_routes_fastapi import router as student_router
from backend.api.v1.faculty_routes_fastapi import router as faculty_router
from backend.api.v1.attendance_routes_fastapi import router as attendance_router
from backend.api.v1.recognition_routes_fastapi import router as recognition_router
from backend.api.error_handler import validation_exception_handler, general_exception_handler

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
log_level = os.getenv("LOG_LEVEL", "INFO")
init_logging(log_level)
log = get_logger(__name__)


# -----------------------------------------------------------------------------
# FastAPI App Lifecycle
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("application_startup")
    
    # Initialize database within the Flask context (for Flask-SQLAlchemy)
    with legacy_flask_app.app_context():
        db.create_all()
        log.info("database_initialized")

    init_celery_config()
    log.info("celery_initialized")
    
    yield

    db.session.remove()
    log.info("application_shutdown")


# -----------------------------------------------------------------------------
# FastAPI Application Initialization
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Facial Recognition Attendance API",
    description="Modern async API for facial recognition attendance system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://localhost:3000",
    ).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_session_middleware(request, call_next):
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


# Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# API Routes
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(student_router, prefix="/api/v1", tags=["Students"])
app.include_router(faculty_router, prefix="/api/v1", tags=["Faculty"])
app.include_router(attendance_router, prefix="/api/v1", tags=["Attendance"])
app.include_router(recognition_router, prefix="/api/v1", tags=["Recognition"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "facial-recognition-api"}


@app.get("/")
async def root():
    return {
        "message": "Attendance API - Use frontend SPA or /docs for API documentation",
        "docs": "/docs",
        "health": "/health",
        "legacy": "/legacy",
    }


# Mount Legacy Flask Application
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
