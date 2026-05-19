"""
Pydantic validation models for all API endpoints.
Provides input validation, error messages, and API response schemas.
"""
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime


# Generic response model
T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool
    data: Optional[T] = None
    error: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {},
                "error": None
            }
        }


class ErrorDetail(BaseModel):
    """Error detail structure."""
    code: str
    message: str


# ============================================================================
# Attendance Models
# ============================================================================

class CreateAttendanceRequest(BaseModel):
    """Create attendance record request."""

    rollno: int = Field(..., gt=0, description="Student roll number")
    course: str = Field(..., min_length=1, max_length=100, description="Course name")
    lecture_no: int = Field(..., ge=0, description="Lecture number")

    class Config:
        json_schema_extra = {
            "example": {
                "rollno": 12001,
                "course": "Computer Science",
                "lecture_no": 1,
            }
        }

    @validator("course")
    def validate_course(cls, value):
        if not value or not value.strip():
            raise ValueError("Course cannot be empty")
        return value.strip()


class UpdateAttendanceRequest(BaseModel):
    """Update attendance record request."""

    rollno: Optional[int] = Field(None, gt=0, description="Student roll number")
    course: Optional[str] = Field(None, min_length=1, max_length=100, description="Course name")
    lecture_no: Optional[int] = Field(None, ge=0, description="Lecture number")

    class Config:
        json_schema_extra = {
            "example": {
                "rollno": 12001,
                "course": "Computer Science",
                "lecture_no": 1,
            }
        }

    @validator("course")
    def validate_course(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Course cannot be empty")
        return value.strip() if value is not None else value


class AttendanceResponse(BaseModel):
    """Attendance response model."""

    attendanceId: int
    rollno: int
    course: Optional[str] = None
    lectureNo: Optional[int] = None
    markedBy: Optional[str] = None
    markedDate: Optional[str] = None
    markedTime: Optional[str] = None


class AttendanceListResponse(BaseModel):
    """List of attendance records response."""

    records: List[AttendanceResponse]
    total: int
class LoginRequest(BaseModel):
    """Student/Faculty login request."""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")
    role: Optional[str] = Field(None, description="Role: 'student' or 'faculty'")
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "password123",
                "role": "student"
            }
        }

    @validator("role")
    def validate_role(cls, v):
        if v is None:
            return v

        normalized = v.lower().strip()

        if normalized not in {"student", "faculty"}:
            raise ValueError("Role must be 'student', 'faculty', or null")

        return normalized



class TokenRequest(BaseModel):
    """JWT token generation request."""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "password123"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refreshToken: str = Field(..., description="Valid refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
            }
        }

    @validator('refreshToken')
    def validate_token(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Invalid refresh token format')
        return v


# ============================================================================
# Student Models
# ============================================================================

class RegisterStudentRequest(BaseModel):
    """Student registration request."""
    rollno: int = Field(..., gt=0, description="Roll number (positive integer)")
    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")
    semester: Optional[str] = Field("", max_length=50, description="Semester")
    pic_path: Optional[str] = Field("", description="Picture path")

    class Config:
        json_schema_extra = {
            "example": {
                "rollno": 12001,
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123",
                "semester": "5",
                "pic_path": "/path/to/pic.jpg"
            }
        }

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class StudentResponse(BaseModel):
    """Student response model."""
    rollno: int
    name: str
    email: str
    semester: Optional[str] = None


class StudentListResponse(BaseModel):
    """List of students response."""
    students: List[StudentResponse]
    total: int


# ============================================================================
# Faculty Models
# ============================================================================

class CreateFacultyRequest(BaseModel):
    """Create faculty request."""
    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password")
    course: str = Field(..., min_length=1, max_length=100, description="Course name")
    is_admin: Optional[bool] = Field(False, description="Admin privileges")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Dr. Smith",
                "email": "smith@example.com",
                "password": "password123",
                "course": "Computer Science",
                "is_admin": False
            }
        }

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class UpdateFacultyRequest(BaseModel):
    """Update faculty request."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    course: Optional[str] = Field(None, min_length=1, max_length=100)
    is_admin: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Dr. Smith",
                "course": "Computer Science",
                "is_admin": False
            }
        }


class FacultyResponse(BaseModel):
    """Faculty response model."""
    f_id: int
    name: str
    email: str
    course: str
    is_admin: bool



# ============================================================================
# Recognition Models
# ============================================================================

class CreateRecognitionJobRequest(BaseModel):
    """Start face recognition job request."""
    course: str = Field(..., min_length=1, description="Course name")
    lecture_no: int = Field(..., description="Lecture number")
    duration_seconds: Optional[int] = Field(30, ge=5, le=600, description="Duration in seconds (5-600)")

    class Config:
        json_schema_extra = {
            "example": {
                "course": "Computer Science",
                "lecture_no": 1,
                "duration_seconds": 30
            }
        }


class RecognitionJobResponse(BaseModel):
    """Recognition job response."""
    job_id: str
    status: str
    created_at: datetime
    progress: Optional[dict] = None


class RecognitionJobStatusResponse(BaseModel):
    """Recognition job status response."""
    job_id: str
    status: str
    progress: Optional[dict] = None
    result: Optional[dict] = None
    error: Optional[str] = None
