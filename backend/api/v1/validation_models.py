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
# Authentication Models
# ============================================================================

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
# Attendance Models
# ============================================================================

class CreateAttendanceRequest(BaseModel):
    """Create attendance record request."""
    rollno: int = Field(..., gt=0, description="Student roll number")
    date: str = Field(..., description="Date (YYYY-MM-DD format)")
    time_in: Optional[str] = None
    time_out: Optional[str] = None
    status: str = Field("present", description="Status: present, absent, late")

    class Config:
        json_schema_extra = {
            "example": {
                "rollno": 12001,
                "date": "2024-05-19",
                "status": "present",
                "time_in": "09:00:00",
                "time_out": "16:30:00"
            }
        }

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = {"present", "absent", "late", "excused"}
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v


class UpdateAttendanceRequest(BaseModel):
    """Update attendance record request."""
    status: Optional[str] = None
    time_in: Optional[str] = None
    time_out: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "present",
                "time_in": "09:00:00",
                "time_out": "16:30:00"
            }
        }

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = {"present", "absent", "late", "excused"}
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of {valid_statuses}')
        return v


class AttendanceResponse(BaseModel):
    """Attendance response model."""
    id: int
    rollno: int
    date: str
    time_in: Optional[str]
    time_out: Optional[str]
    status: str
    created_at: Optional[datetime] = None


class AttendanceListResponse(BaseModel):
    """List of attendance records response."""
    records: List[AttendanceResponse]
    total: int


# ============================================================================
# Recognition Models
# ============================================================================

class RecognitionJobRequest(BaseModel):
    """Start face recognition job request."""
    course: str = Field(..., min_length=1, description="Course name")
    timeout: Optional[int] = Field(30, ge=5, le=300, description="Timeout in seconds (5-300)")

    class Config:
        json_schema_extra = {
            "example": {
                "course": "Computer Science",
                "timeout": 30
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
