# backend/services/auth_service.py

from datetime import datetime

from backend.extensions import db
from backend.models import Faculty, Student, User, Role
from backend.security import hash_password, verify_password


class AuthService:
    @staticmethod
    def get_role(role_name: str) -> Role:
        return Role.query.filter_by(name=role_name.upper()).first()

    @staticmethod
    def authenticate(email: str, password: str):
        """Universal authentication using the User model"""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def authenticate_student(email: str, password: str):
        # Keep for backward compatibility
        user = AuthService.authenticate(email, password)
        if user and user.role and user.role.name == 'STUDENT':
            return user.student_profile

        # Fallback to old table if user not linked yet
        student = Student.query.filter_by(email=email).first()
        if student and student.check_password(password):
            return student
        return None

    @staticmethod
    def authenticate_faculty(email: str, password: str):
        # Keep for backward compatibility
        user = AuthService.authenticate(email, password)
        if user and user.role and user.role.name in ['FACULTY', 'ADMIN']:
            return user.faculty_profile

        # Fallback to old table if user not linked yet
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
        existingUser = User.query.filter_by(email=email).first()
        if existingUser:
            return None, "User with this email already exists!"

        # 1. Create User
        role_name = 'ADMIN' if isAdmin else 'FACULTY'
        role = AuthService.get_role(role_name)

        user = User(
            email=email,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush() # Get user.id

        # 2. Create Faculty Profile
        faculty = Faculty(
            user_id=user.id,
            name=name,
            course=course,
            email=email,
            is_admin=isAdmin,
            registered_on=datetime.now(),
        )
        faculty.set_password(password)

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
        existingUser = User.query.filter_by(email=email).first()
        if existingUser:
            return None, "User with this email already exists!"

        # 1. Create User
        role = AuthService.get_role('STUDENT')
        
        user = User(
            email=email,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # 2. Create Student Profile
        student = Student(
            user_id=user.id,
            rollno=rollno,
            name=name,
            semester=semester,
            email=email,
            pic_path=picPath,
            registered_on=datetime.now(),
        )
        student.set_password(password)

        db.session.add(student)
        db.session.commit()

        return student, None