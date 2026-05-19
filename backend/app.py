"""
Main application entry point - FastAPI with async/await support.
Replaces Flask with modern async framework while reusing existing models, services, repositories.
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure backend is properly imported
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import Config
from backend.celery_app import init_celery_config
from backend.extensions import db
from backend.api.v1.auth_routes_fastapi import router as auth_router
from backend.api.v1.student_routes_fastapi import router as student_router
from backend.api.v1.faculty_routes_fastapi import router as faculty_router
from backend.api.v1.attendance_routes_fastapi import router as attendance_router
from backend.api.v1.recognition_routes_fastapi import router as recognition_router


# Initialize database (using Flask app context for SQLAlchemy)
def create_flask_bridge():
    """Create a Flask app to bridge Flask-SQLAlchemy with FastAPI."""
    try:
        from flask import Flask as FlaskApp
        flask_app = FlaskApp(__name__)
        flask_app.config.from_object(Config)
        db.init_app(flask_app)
        # Push a persistent app context so that db.session and Model.query work
        ctx = flask_app.app_context()
        ctx.push()
        return flask_app, ctx
    except Exception as e:
        print(f"[WARN] Flask bridge initialization: {e}")
        return None, None


# Create the bridge and ensure db is initialized
flask_app, flask_ctx = create_flask_bridge()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    if flask_app:
        with flask_app.app_context():
            db.create_all()
            print("[DB] Database initialized")
    
    init_celery_config()
    print("[START] FastAPI initialized with Celery enabled")
    yield
    # Shutdown
    if flask_ctx:
        flask_ctx.pop()
    print("[STOP] FastAPI shutdown")


# Create FastAPI app
app = FastAPI(
    title="Facial Recognition Attendance API",
    description="Modern async API for facial recognition attendance system",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_session_middleware(request, call_next):
    """Ensure database session is removed after each request."""
    try:
        response = await call_next(request)
        return response
    finally:
        db.session.remove()


# Register routers
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(student_router, prefix="/api/v1", tags=["Students"])
app.include_router(faculty_router, prefix="/api/v1", tags=["Faculty"])
app.include_router(attendance_router, prefix="/api/v1", tags=["Attendance"])
app.include_router(recognition_router, prefix="/api/v1", tags=["Recognition"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "facial-recognition-api"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "Attendance API - Use frontend SPA or /docs for API documentation",
        "docs": "/docs",
        "health": "/health"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "error": {"message": exc.detail, "code": exc.status_code}
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

