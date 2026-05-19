# backend/services/auth_service.py

from datetime import datetime

from backend.extensions import db
from backend.models import Faculty, Student
from backend.security import hash_password, verify_password


class AuthService:
    @staticmethod
    def authenticate_student(email: str, password: str):
        student = Student.query.filter_by(email=email).first()

        if not student:
            return None

        if verify_password(password, student.password):
            return student

        return None

    @staticmethod
    def authenticate_faculty(email: str, password: str):
        faculty = Faculty.query.filter_by(email=email).first()

        if not faculty:
            return None

        if verify_password(password, faculty.password):
            return faculty

        return None

    @staticmethod
    def get_user_by_token_payload(payload: dict):
        role = payload.get("role")
        user_id = payload.get("user_id")

        if not role or user_id is None:
            return None, None

        if role == "student":
            user = Student.query.filter_by(rollno=user_id).first()
            return user, "student"

        if role == "faculty":
            user = Faculty.query.filter_by(f_id=user_id).first()
            return user, "faculty"

        return None, None

    @staticmethod
    def serialize_student(student: Student) -> dict:
        return {
            "id": student.id,
            "rollno": student.rollno,
            "name": student.name,
            "email": student.email,
            "semester": student.semester,
            "role": "student",
        }

    @staticmethod
    def serialize_faculty(faculty: Faculty) -> dict:
        return {
            "id": faculty.f_id,
            "name": faculty.name,
            "email": faculty.email,
            "course": faculty.course,
            "isAdmin": bool(faculty.is_admin),
            "role": "faculty",
        }

    @staticmethod
    def registerFaculty(name: str, course: str, email: str, password: str, isAdmin: bool):
        existingFaculty = Faculty.query.filter_by(email=email).first()

        if existingFaculty is not None:
            return None, "Faculty with this email already exists!"

        faculty = Faculty(
            name=name,
            course=course,
            email=email,
            password=hash_password(password),
            is_admin=isAdmin,
            registered_on=datetime.now(),
        )

        db.session.add(faculty)
        db.session.commit()

        return faculty, None

    @staticmethod
    def registerStudent(
        rollno: int,
        name: str,
        semester: str,
        email: str,
        password: str,
        picPath: str,
    ):
        existingStudent = Student.query.filter_by(email=email).first()

        if existingStudent is not None:
            return None, "Student with this email already exists!"

        student = Student(
            rollno=rollno,
            name=name,
            semester=semester,
            email=email,
            password=hash_password(password),
            pic_path=picPath,
            registered_on=datetime.now(),
        )

        db.session.add(student)
        db.session.commit()

        return student, None