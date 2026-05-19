# backend/services/auth_service.py

from datetime import datetime
from typing import Optional, Tuple
from backend.extensions import db
from backend.models import Faculty, Role, Student, User


class AuthService:
    @staticmethod
    def get_role(role_name: str) -> Optional[Role]:
        if not role_name:
            return None

        return Role.query.filter_by(name=role_name.upper()).first()

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[User]:
        """
        Universal authentication using the User model.
        """
        if not email or not password:
            return None

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def authenticate_student(email: str, password: str) -> Optional[Student]:
        """
        Authenticate student.

        Priority:
        1. New User model + linked student_profile
        2. Legacy Student table fallback
        """
        user = AuthService.authenticate(email, password)

        if user and user.role and user.role.name == "STUDENT":
            if user.student_profile:
                return user.student_profile

        student = Student.query.filter_by(email=email).first()
        if student and student.check_password(password):
            return student
        return None

    @staticmethod
    def authenticate_faculty(email: str, password: str) -> Optional[Faculty]:
        """
        Authenticate faculty/admin.

        Priority:
        1. New User model + linked faculty_profile
        2. Legacy Faculty table fallback
        """
        user = AuthService.authenticate(email, password)

        if user and user.role and user.role.name in {"FACULTY", "ADMIN"}:
            if user.faculty_profile:
                return user.faculty_profile

        faculty = Faculty.query.filter_by(email=email).first()
        if faculty and faculty.check_password(password):
            return faculty
        return None

    @staticmethod
    def get_user_by_token_payload(payload: dict):
        role = payload.get("role")
        user_id = payload.get("user_id")

        if not role or user_id is None:
            return None, None

        if role == "student":
            student = Student.query.filter_by(rollno=user_id).first()
            return student, "student"

        if role == "faculty":
            faculty = Faculty.query.filter_by(f_id=user_id).first()
            return faculty, "faculty"

        return None, None

    @staticmethod
    def serialize_student(student: Student) -> dict:
        return {
            "id": getattr(student, "id", student.rollno),
            "rollno": student.rollno,
            "name": student.name,
            "email": student.email,
            "semester": student.semester,
            "role": "student",
        }

    @staticmethod
    def serialize_faculty(faculty: Faculty) -> dict:
        return {
            "id": getattr(faculty, "f_id", getattr(faculty, "id", None)),
            "name": faculty.name,
            "email": faculty.email,
            "course": faculty.course,
            "isAdmin": bool(faculty.is_admin),
            "role": "faculty",
        }

    @staticmethod
    def register_faculty(
        name: str,
        course: str,
        email: str,
        password: str,
        is_admin: bool = False,
    ) -> Tuple[Optional[Faculty], Optional[str]]:
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return None, "User with this email already exists!"

        role_name = "ADMIN" if is_admin else "FACULTY"
        role = AuthService.get_role(role_name)

        if not role:
            return None, f"Role {role_name} does not exist!"
        user = User(
            email=email,
            role=role,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        faculty = Faculty(
            user_id=user.id,
            name=name,
            course=course,
            email=email,
            is_admin=is_admin,
            registered_on=datetime.now(),
        )
        faculty.set_password(password)

        db.session.add(faculty)
        db.session.commit()

        return faculty, None

    @staticmethod
    def register_student(
        rollno: int,
        name: str,
        semester: str,
        email: str,
        password: str,
        pic_path: str,
    ) -> Tuple[Optional[Student], Optional[str]]:
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return None, "User with this email already exists!"

        role = AuthService.get_role("STUDENT")

        if not role:
            return None, "Role STUDENT does not exist!"

        user = User(
            email=email,
            role=role,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            rollno=rollno,
            name=name,
            semester=semester,
            email=email,
            pic_path=pic_path,
            registered_on=datetime.now(),
        )
        student.set_password(password)

        db.session.add(student)
        db.session.commit()

        return student, None
    # Backward compatibility aliases for old code
    registerFaculty = register_faculty
    registerStudent = register_student