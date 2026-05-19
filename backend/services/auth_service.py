from datetime import datetime

from backend.extensions import db
from backend.models import Faculty, Student
from backend.security import hash_password, verify_password


class AuthService:
    @staticmethod
    def isBcryptHash(value: str) -> bool:
        return isinstance(value, str) and value.startswith("$2")

    @staticmethod
    def verifyAndUpgradePassword(user, password: str) -> bool:
        storedPassword = user.password
        if not storedPassword:
            return False

        if AuthService.isBcryptHash(storedPassword):
            return verify_password(password, storedPassword)

        if storedPassword == password:
            user.password = hash_password(password)
            db.session.commit()
            return True

        return False

    @staticmethod
    def authenticateStudent(email: str, password: str):
        student = Student.query.filter_by(email=email).first()
        if student and AuthService.verifyAndUpgradePassword(student, password):
            return student
        return None

    @staticmethod
    def authenticateFaculty(email: str, password: str):
        faculty = Faculty.query.filter_by(email=email).first()
        if faculty and AuthService.verifyAndUpgradePassword(faculty, password):
            return faculty
        return None

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
