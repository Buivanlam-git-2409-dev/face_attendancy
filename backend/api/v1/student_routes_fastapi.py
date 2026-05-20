"""
FastAPI Student Routes.

Routes:
- POST /students/register: register new student account.
- GET /students: faculty only.
- GET /students/{rollno}: faculty or the student owner.
- GET /students/{rollno}/attendances: faculty or the student owner.
- GET /me/attendances: current student only.
"""

from fastapi import APIRouter, Depends, HTTPException
import structlog
from pathlib import Path

import face_recognition
from fastapi import File, UploadFile
from backend.extensions import db
from backend.models import FaceEmbedding

from backend.api.error_handler import ErrorCode, error_response, success_response
from backend.api.v1.dependencies import get_current_user, require_faculty, require_student
from backend.api.v1.validation_models import RegisterStudentRequest
from backend.models import Faculty, Student
from backend.services.attendance_service import AttendanceService
from backend.services.auth_service import AuthService
from backend.services.student_service import StudentService


router = APIRouter()
log = structlog.get_logger(__name__)


def forbidden(message: str):
    response = error_response(ErrorCode.FORBIDDEN, message, 403)
    raise HTTPException(status_code=403, detail=response["error"])


def not_found(message: str):
    response = error_response(ErrorCode.NOT_FOUND, message, 404)
    raise HTTPException(status_code=404, detail=response["error"])


def internal_error(message: str):
    response = error_response(ErrorCode.INTERNAL_ERROR, message, 500)
    raise HTTPException(status_code=500, detail=response["error"])


@router.post("/students/register", status_code=201)
async def register_student_api(payload: RegisterStudentRequest):
    """
    Register a new student account.

    Current mode: public endpoint for demo/MVP.
    Production recommendation: restrict this endpoint to faculty/admin.
    """
    rollno = payload.rollno
    name = payload.name
    email = payload.email
    password = payload.password
    semester = payload.semester or ""
    pic_path = payload.pic_path or ""

    log.info("student_registration_attempt", rollno=rollno, email=email)

    try:
        student, error = AuthService.register_student(
            rollno=int(rollno),
            name=name,
            semester=semester,
            email=email,
            password=password,
            pic_path=pic_path,
        )

        if error:
            log.warning(
                "student_registration_failed",
                rollno=rollno,
                email=email,
                reason=error,
            )

            response = error_response(
                ErrorCode.CONFLICT,
                error,
                409,
            )
            raise HTTPException(status_code=409, detail=response["error"])

        log.info("student_registration_success", rollno=rollno, email=email)

        return success_response(
            {
                "message": "Student registered successfully",
                "user": {
                    "rollno": student.rollno,
                    "name": student.name,
                    "email": student.email,
                },
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(
            "student_registration_error",
            rollno=rollno,
            error=str(e),
            exc_info=e,
        )
        response = error_response(
            ErrorCode.INTERNAL_ERROR,
            "Registration failed",
            500,
        )
        raise HTTPException(status_code=500, detail=response["error"])


@router.get("/students")
async def list_students_api(current_faculty: Faculty = Depends(require_faculty)):
    """List all students. Faculty only."""
    log.info("list_students_request", faculty=current_faculty.name)

    try:
        students = StudentService.listStudents()
        return success_response(students)

    except Exception as e:
        log.error("list_students_error", error=str(e), exc_info=e)
        internal_error("Failed to retrieve students")


@router.get("/students/{rollno}")
async def get_student_api(
    rollno: int,
    current_user_data: tuple = Depends(get_current_user),
):
    """Get student by roll number. Faculty or student owner only."""
    log.info("get_student_request", rollno=rollno)

    current_user, role = current_user_data

    if role == "student" and current_user.rollno != rollno:
        log.warning(
            "get_student_forbidden",
            requested_rollno=rollno,
            current_rollno=current_user.rollno,
        )
        forbidden("Cannot access other student data")

    try:
        student = StudentService.getStudentByRollNo(rollno)

        if student is None:
            log.warning("get_student_not_found", rollno=rollno)
            not_found("Student not found")

        log.info("get_student_success", rollno=rollno)
        return success_response(student)

    except HTTPException:
        raise
    except Exception as e:
        log.error("get_student_error", rollno=rollno, error=str(e), exc_info=e)
        internal_error("Failed to retrieve student")


@router.get("/students/{rollno}/attendances")
async def get_student_attendance_api(
    rollno: int,
    current_user_data: tuple = Depends(get_current_user),
):
    """Get student's attendance records. Faculty or student owner only."""
    log.info("get_student_attendance_request", rollno=rollno)

    current_user, role = current_user_data

    if role == "student" and current_user.rollno != rollno:
        log.warning(
            "get_student_attendance_forbidden",
            requested_rollno=rollno,
            current_rollno=current_user.rollno,
        )
        forbidden("Cannot access other student data")

    try:
        student = StudentService.getStudentByRollNo(rollno)

        if student is None:
            log.warning("get_student_attendance_not_found", rollno=rollno)
            not_found("Student not found")

        data = AttendanceService.listAttendances(rollNo=rollno)

        log.info(
            "get_student_attendance_success",
            rollno=rollno,
            count=len(data),
        )

        return success_response(data)
    except HTTPException:
        raise
    except Exception as e:
        log.error(
            "get_student_attendance_error",
            rollno=rollno,
            error=str(e),
            exc_info=e,
        )
        internal_error("Failed to retrieve attendance")


@router.get("/me/attendances")
async def get_my_attendances_api(current_student: Student = Depends(require_student)):
    """Get current student's attendance records."""
    log.info("get_my_attendances", rollno=current_student.rollno)

    try:
        data = AttendanceService.listAttendances(rollNo=current_student.rollno)
        return success_response(data)
    except Exception as e:
        log.error(
            "get_my_attendances_error",
            rollno=current_student.rollno,
            error=str(e),
            exc_info=e,
        )
        internal_error("Failed to retrieve attendance")
        
@router.post("/students/{rollno}/face")
async def upload_student_face_api(
    rollno: int,
    file: UploadFile = File(...),
    current_faculty: Faculty = Depends(require_faculty),
):
    """
    Upload student face image and create FaceEmbedding.
    Faculty only.
    """
    log.info(
        "upload_student_face_request",
        rollno=rollno,
        faculty=current_faculty.name,
        filename=file.filename,
    )

    try:
        student = Student.query.filter_by(rollno=rollno).first()

        if not student:
            not_found("Student not found")

        if not file.content_type or not file.content_type.startswith("image/"):
            response = error_response(
                ErrorCode.BAD_REQUEST,
                "Uploaded file must be an image",
                400,
            )
            raise HTTPException(status_code=400, detail=response["error"])

        upload_dir = Path("backend/static/images/users")
        upload_dir.mkdir(parents=True, exist_ok=True)

        extension = Path(file.filename or "").suffix.lower()
        if extension not in [".jpg", ".jpeg", ".png"]:
            extension = ".jpg"

        image_path = upload_dir / f"{rollno}{extension}"

        contents = await file.read()
        if not contents:
            response = error_response(
                ErrorCode.BAD_REQUEST,
                "Uploaded file is empty",
                400,
            )
            raise HTTPException(status_code=400, detail=response["error"])

        image_path.write_bytes(contents)

        image = face_recognition.load_image_file(str(image_path))
        face_locations = face_recognition.face_locations(image)

        if len(face_locations) == 0:
            response = error_response(
                ErrorCode.BAD_REQUEST,
                "No face found in image",
                400,
            )
            raise HTTPException(status_code=400, detail=response["error"])

        if len(face_locations) > 1:
            response = error_response(
                ErrorCode.BAD_REQUEST,
                "More than one face found. Please upload an image with exactly one face.",
                400,
            )
            raise HTTPException(status_code=400, detail=response["error"])

        encodings = face_recognition.face_encodings(image, face_locations)

        if not encodings:
            response = error_response(
                ErrorCode.BAD_REQUEST,
                "Could not generate face embedding",
                400,
            )
            raise HTTPException(status_code=400, detail=response["error"])

        old_embeddings = FaceEmbedding.query.filter_by(
            student_id=student.id,
            is_active=True,
        ).all()

        for embedding in old_embeddings:
            embedding.is_active = False

        new_embedding = FaceEmbedding(
            student_id=student.id,
            embedding=encodings[0].tolist(),
            source_image_path=str(image_path),
            quality_score=1.0,
            is_active=True,
        )

        db.session.add(new_embedding)
        db.session.commit()

        log.info(
            "upload_student_face_success",
            rollno=rollno,
            student_id=student.id,
            embedding_id=new_embedding.id,
        )

        return success_response(
            {
                "message": "Face image uploaded and embedding created successfully",
                "rollno": student.rollno,
                "studentName": student.name,
                "embeddingId": new_embedding.id,
                "imagePath": str(image_path),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        db.session.rollback()
        log.error(
            "upload_student_face_error",
            rollno=rollno,
            error=str(e),
            exc_info=e,
        )
        internal_error("Failed to upload student face")