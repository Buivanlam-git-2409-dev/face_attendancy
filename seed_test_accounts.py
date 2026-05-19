"""
Seed/Test Accounts for Face Attendance Project

Mục đích:
- Kiểm tra app hiện đang kết nối DB nào.
- Tạo role mặc định: STUDENT, FACULTY, ADMIN.
- Tạo tài khoản faculty test.
- Tạo tài khoản student test.
- Test login trực tiếp qua API sau khi tạo.

Cách dùng:

1. Đặt file này ở root project, cùng cấp với thư mục backend/

2. Chạy backend ở terminal 1:
   uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

3. Chạy script ở terminal 2:
   python seed_test_accounts.py

Sau khi chạy xong, bạn có thể dùng:

Faculty:
  email: faculty@example.com
  password: password123

Student:
  email: student@example.com
  password: password123

Nếu muốn đổi thông tin:
  Windows PowerShell:
    $env:TEST_FACULTY_EMAIL="teacher@test.com"
    $env:TEST_FACULTY_PASSWORD="123456"
    python seed_test_accounts.py

  macOS/Linux:
    TEST_FACULTY_EMAIL="teacher@test.com" TEST_FACULTY_PASSWORD="123456" python seed_test_accounts.py
"""

import os
import sys
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
API_URL = f"{BASE_URL}/api/v1"

TEST_FACULTY_EMAIL = os.getenv("TEST_FACULTY_EMAIL", "faculty@example.com")
TEST_FACULTY_PASSWORD = os.getenv("TEST_FACULTY_PASSWORD", "password123")

TEST_STUDENT_EMAIL = os.getenv("TEST_STUDENT_EMAIL", "student@example.com")
TEST_STUDENT_PASSWORD = os.getenv("TEST_STUDENT_PASSWORD", "password123")
TEST_STUDENT_ROLLNO = int(os.getenv("TEST_STUDENT_ROLLNO", "12001"))


def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_ok(message: str) -> None:
    print(f"[OK] {message}")


def print_info(message: str) -> None:
    print(f"[INFO] {message}")


def print_warn(message: str) -> None:
    print(f"[WARN] {message}")


def seed_database_directly() -> None:
    """
    Seed roles/users directly through Flask-SQLAlchemy models.

    This works even before API login works, as long as backend imports are valid.
    """
    print_section("1. Import backend app and inspect database")

    from backend.app import legacy_flask_app
    from backend.extensions import db
    from backend.models import Faculty, Role, Student, User

    with legacy_flask_app.app_context():
        db_uri = legacy_flask_app.config.get("SQLALCHEMY_DATABASE_URI")
        print_info(f"SQLALCHEMY_DATABASE_URI = {db_uri}")

        db.create_all()
        print_ok("db.create_all() completed")

        print_section("2. Seed roles")

        default_roles = [
            ("STUDENT", "Student user"),
            ("FACULTY", "Faculty user"),
            ("ADMIN", "Administrator user"),
        ]

        for name, description in default_roles:
            role = Role.query.filter_by(name=name).first()
            if role:
                print_ok(f"Role already exists: {name}")
                continue

            role = Role(name=name, description=description)
            db.session.add(role)
            print_ok(f"Created role: {name}")

        db.session.commit()

        print_section("3. Seed faculty account")

        faculty_role = Role.query.filter_by(name="FACULTY").first()
        if not faculty_role:
            raise RuntimeError("FACULTY role was not created")

        user = User.query.filter_by(email=TEST_FACULTY_EMAIL).first()
        faculty = Faculty.query.filter_by(email=TEST_FACULTY_EMAIL).first()

        if not user:
            user = User(
                email=TEST_FACULTY_EMAIL,
                role=faculty_role,
                is_active=True,
            )
            user.set_password(TEST_FACULTY_PASSWORD)
            db.session.add(user)
            db.session.flush()
            print_ok(f"Created User for faculty: {TEST_FACULTY_EMAIL}")
        else:
            user.role = faculty_role
            user.set_password(TEST_FACULTY_PASSWORD)
            print_ok(f"Updated existing User password/role: {TEST_FACULTY_EMAIL}")

        if not faculty:
            faculty = Faculty(
                user_id=user.id,
                name="Test Faculty",
                course="Computer Science",
                email=TEST_FACULTY_EMAIL,
                is_admin=False,
            )
            faculty.set_password(TEST_FACULTY_PASSWORD)
            db.session.add(faculty)
            print_ok(f"Created Faculty profile: {TEST_FACULTY_EMAIL}")
        else:
            faculty.user_id = user.id
            faculty.name = faculty.name or "Test Faculty"
            faculty.course = faculty.course or "Computer Science"
            faculty.is_admin = False
            faculty.set_password(TEST_FACULTY_PASSWORD)
            print_ok(f"Updated existing Faculty profile: {TEST_FACULTY_EMAIL}")

        db.session.commit()

        print_section("4. Seed student account")

        student_role = Role.query.filter_by(name="STUDENT").first()
        if not student_role:
            raise RuntimeError("STUDENT role was not created")

        user = User.query.filter_by(email=TEST_STUDENT_EMAIL).first()
        student = Student.query.filter_by(email=TEST_STUDENT_EMAIL).first()
        roll_owner = Student.query.filter_by(rollno=TEST_STUDENT_ROLLNO).first()

        if roll_owner and roll_owner.email != TEST_STUDENT_EMAIL:
            raise RuntimeError(
                f"rollno {TEST_STUDENT_ROLLNO} is already used by {roll_owner.email}. "
                "Set TEST_STUDENT_ROLLNO to another number."
            )

        if not user:
            user = User(
                email=TEST_STUDENT_EMAIL,
                role=student_role,
                is_active=True,
            )
            user.set_password(TEST_STUDENT_PASSWORD)
            db.session.add(user)
            db.session.flush()
            print_ok(f"Created User for student: {TEST_STUDENT_EMAIL}")
        else:
            user.role = student_role
            user.set_password(TEST_STUDENT_PASSWORD)
            print_ok(f"Updated existing User password/role: {TEST_STUDENT_EMAIL}")

        if not student:
            student = Student(
                user_id=user.id,
                rollno=TEST_STUDENT_ROLLNO,
                name="Test Student",
                semester="5",
                email=TEST_STUDENT_EMAIL,
                pic_path="",
            )
            student.set_password(TEST_STUDENT_PASSWORD)
            db.session.add(student)
            print_ok(f"Created Student profile: {TEST_STUDENT_EMAIL}")
        else:
            student.user_id = user.id
            student.rollno = TEST_STUDENT_ROLLNO
            student.name = student.name or "Test Student"
            student.semester = student.semester or "5"
            student.set_password(TEST_STUDENT_PASSWORD)
            print_ok(f"Updated existing Student profile: {TEST_STUDENT_EMAIL}")

        db.session.commit()

        print_section("5. Seed summary")
        print_ok(f"Faculty: {TEST_FACULTY_EMAIL} / {TEST_FACULTY_PASSWORD}")
        print_ok(f"Student: {TEST_STUDENT_EMAIL} / {TEST_STUDENT_PASSWORD}")
        print_ok(f"Student rollno: {TEST_STUDENT_ROLLNO}")


def login_via_api(email: str, password: str, role: str):
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "email": email,
            "password": password,
            "role": role,
        },
        timeout=20,
    )

    print_info(f"POST /auth/login role={role} status={response.status_code}")

    try:
        body = response.json()
    except ValueError:
        print_warn(response.text)
        return None

    if response.status_code != 200 or body.get("success") is not True:
        print_warn(f"Login failed: {body}")
        return None

    token = body["data"]["accessToken"]
    print_ok(f"Login OK: {email} as {role}")
    return token


def test_api_login_if_backend_running() -> None:
    print_section("6. Test login API if backend is running")

    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        print_warn("Backend is not running. Skip API login test.")
        print_warn("Run: uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload")
        return

    if health.status_code != 200:
        print_warn(f"Backend /health returned {health.status_code}. Skip API login test.")
        return

    print_ok("Backend /health OK")

    faculty_token = login_via_api(
        TEST_FACULTY_EMAIL,
        TEST_FACULTY_PASSWORD,
        "faculty",
    )

    student_token = login_via_api(
        TEST_STUDENT_EMAIL,
        TEST_STUDENT_PASSWORD,
        "student",
    )

    if faculty_token:
        me = requests.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {faculty_token}"},
            timeout=20,
        )
        print_info(f"Faculty GET /auth/me status={me.status_code}")
        print(me.text)

    if student_token:
        me = requests.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {student_token}"},
            timeout=20,
        )
        print_info(f"Student GET /auth/me status={me.status_code}")
        print(me.text)


def main() -> int:
    try:
        seed_database_directly()
        test_api_login_if_backend_running()

        print_section("DONE")
        print_ok("Seed/test accounts completed")
        return 0

    except Exception as exc:
        print_section("ERROR")
        print(f"{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
