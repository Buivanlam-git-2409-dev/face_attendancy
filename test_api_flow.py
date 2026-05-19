"""
API Smoke Test for Face Attendance Project

File này dùng để test nhanh các phần đã refactor:
- FastAPI health check
- Student register/login
- JWT /auth/me
- Student permission
- Faculty login nếu có tài khoản faculty
- Faculty list students
- Faculty create/get/update/delete attendance
- Recognition verify invalid image handling

Cách dùng:

1. Chạy backend trước:
   uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

2. Cài requests nếu chưa có:
   pip install requests

3. Chạy test cơ bản:
   python test_api_flow.py

4. Nếu muốn test thêm faculty/attendance, set biến môi trường:

   Windows PowerShell:
   $env:FACULTY_EMAIL="faculty@example.com"
   $env:FACULTY_PASSWORD="password123"
   python test_api_flow.py

   macOS/Linux:
   FACULTY_EMAIL="faculty@example.com" FACULTY_PASSWORD="password123" python test_api_flow.py

Ghi chú:
- File này cố tình không dùng pytest để bạn chạy dễ hơn.
- Nếu chưa có faculty account thì phần faculty sẽ được skip.
- Student test sẽ tự tạo email/rollno mới theo timestamp để tránh trùng.
"""

import os
import sys
import time
from typing import Any, Dict, Optional

import requests


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
API_URL = f"{BASE_URL}/api/v1"

FACULTY_EMAIL = os.getenv("FACULTY_EMAIL")
FACULTY_PASSWORD = os.getenv("FACULTY_PASSWORD")


class TestFailure(Exception):
    pass


def print_step(message: str) -> None:
    print(f"\n[TEST] {message}")


def print_ok(message: str) -> None:
    print(f"[OK] {message}")


def print_skip(message: str) -> None:
    print(f"[SKIP] {message}")


def fail(message: str) -> None:
    raise TestFailure(message)


def request_json(
    method: str,
    url: str,
    *,
    token: Optional[str] = None,
    expected_status: Optional[int] = None,
    allowed_statuses: Optional[set[int]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    headers = kwargs.pop("headers", {})

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(method, url, headers=headers, timeout=20, **kwargs)

    if expected_status is not None and response.status_code != expected_status:
        raise TestFailure(
            f"{method} {url} expected status {expected_status}, "
            f"got {response.status_code}. Body: {response.text}"
        )

    if allowed_statuses is not None and response.status_code not in allowed_statuses:
        raise TestFailure(
            f"{method} {url} expected status in {allowed_statuses}, "
            f"got {response.status_code}. Body: {response.text}"
        )

    try:
        data = response.json()
    except ValueError:
        raise TestFailure(
            f"{method} {url} did not return JSON. "
            f"Status: {response.status_code}. Body: {response.text}"
        )

    return {
        "status_code": response.status_code,
        "json": data,
    }


def assert_success(payload: Dict[str, Any], context: str) -> Dict[str, Any]:
    body = payload["json"]

    if not isinstance(body, dict):
        fail(f"{context}: response body is not object: {body}")

    if body.get("success") is not True:
        fail(f"{context}: expected success=true, got: {body}")

    return body.get("data")


def assert_error(payload: Dict[str, Any], context: str) -> Dict[str, Any]:
    body = payload["json"]

    if not isinstance(body, dict):
        fail(f"{context}: response body is not object: {body}")

    if body.get("success") is not False:
        fail(f"{context}: expected success=false, got: {body}")

    return body.get("error") or {}


def health_check() -> None:
    print_step("Health check")

    response = requests.get(f"{BASE_URL}/health", timeout=10)

    if response.status_code != 200:
        fail(f"Health check failed. Status={response.status_code}, body={response.text}")

    data = response.json()

    if data.get("status") != "ok":
        fail(f"Health response unexpected: {data}")

    print_ok("Backend /health is OK")


def register_student() -> Dict[str, Any]:
    print_step("Register demo student")

    suffix = int(time.time())
    student = {
        "rollno": suffix % 100000000,
        "name": f"Demo Student {suffix}",
        "email": f"student_{suffix}@example.com",
        "password": "password123",
        "semester": "5",
        "pic_path": "",
    }

    payload = request_json(
        "POST",
        f"{API_URL}/students/register",
        json=student,
        expected_status=201,
    )

    data = assert_success(payload, "register student")

    if not data or "user" not in data:
        fail(f"Register student response missing user: {payload['json']}")

    print_ok(f"Student registered: {student['email']} / rollno={student['rollno']}")

    return student


def login(email: str, password: str, role: Optional[str] = None) -> Dict[str, Any]:
    print_step(f"Login as {role or 'auto'}: {email}")

    body = {
        "email": email,
        "password": password,
    }

    if role:
        body["role"] = role

    payload = request_json(
        "POST",
        f"{API_URL}/auth/login",
        json=body,
        expected_status=200,
    )

    data = assert_success(payload, "login")

    if not data.get("accessToken"):
        fail(f"Login response missing accessToken: {payload['json']}")

    if not data.get("user"):
        fail(f"Login response missing user: {payload['json']}")

    if not data.get("role"):
        fail(f"Login response missing role: {payload['json']}")

    print_ok(f"Login OK. Role={data.get('role')}")

    return data


def auth_me(token: str, expected_role: str) -> Dict[str, Any]:
    print_step("/auth/me with JWT token")

    payload = request_json(
        "GET",
        f"{API_URL}/auth/me",
        token=token,
        expected_status=200,
    )

    data = assert_success(payload, "auth me")

    if data.get("role") != expected_role:
        fail(f"/auth/me expected role={expected_role}, got={data}")

    print_ok(f"/auth/me OK. Role={expected_role}")

    return data


def student_permission_tests(student_token: str, rollno: int) -> None:
    print_step("Student permission tests")

    own_attendances = request_json(
        "GET",
        f"{API_URL}/me/attendances",
        token=student_token,
        expected_status=200,
    )
    assert_success(own_attendances, "student /me/attendances")
    print_ok("Student can access /me/attendances")

    own_profile = request_json(
        "GET",
        f"{API_URL}/students/{rollno}",
        token=student_token,
        expected_status=200,
    )
    assert_success(own_profile, "student own profile")
    print_ok("Student can access own profile")

    forbidden_students = request_json(
        "GET",
        f"{API_URL}/students",
        token=student_token,
        allowed_statuses={401, 403},
    )
    assert_error(forbidden_students, "student forbidden /students")
    print_ok("Student cannot list all students")

    other_rollno = rollno + 999999
    forbidden_other = request_json(
        "GET",
        f"{API_URL}/students/{other_rollno}",
        token=student_token,
        allowed_statuses={401, 403, 404},
    )

    if forbidden_other["status_code"] in {401, 403}:
        assert_error(forbidden_other, "student cannot access other student")
        print_ok("Student cannot access other student's profile")

    if forbidden_other["status_code"] == 404:
        print_ok("Other student not found. Permission route still returned safely")


def faculty_tests(student: Dict[str, Any]) -> None:
    if not FACULTY_EMAIL or not FACULTY_PASSWORD:
        print_skip("FACULTY_EMAIL/FACULTY_PASSWORD not set. Skipping faculty and attendance tests.")
        return

    faculty_login = login(FACULTY_EMAIL, FACULTY_PASSWORD, "faculty")
    faculty_token = faculty_login["accessToken"]

    auth_me(faculty_token, "faculty")

    print_step("Faculty list students")
    students_response = request_json(
        "GET",
        f"{API_URL}/students",
        token=faculty_token,
        expected_status=200,
    )
    assert_success(students_response, "faculty list students")
    print_ok("Faculty can list students")

    print_step("Faculty create attendance")
    attendance_payload = {
        "rollno": student["rollno"],
        "course": "Computer Science",
        "lecture_no": 1,
    }

    create_response = request_json(
        "POST",
        f"{API_URL}/attendances",
        token=faculty_token,
        json=attendance_payload,
        expected_status=201,
    )

    attendance_data = assert_success(create_response, "faculty create attendance")
    attendance_id = attendance_data.get("attendanceId")

    if not attendance_id:
        fail(f"Create attendance response missing attendanceId: {create_response['json']}")

    print_ok(f"Attendance created. attendanceId={attendance_id}")

    print_step("Duplicate attendance should return 409")
    duplicate_response = request_json(
        "POST",
        f"{API_URL}/attendances",
        token=faculty_token,
        json=attendance_payload,
        expected_status=409,
    )
    assert_error(duplicate_response, "duplicate attendance")
    print_ok("Duplicate attendance returns 409")

    print_step("Faculty get attendance detail")
    get_response = request_json(
        "GET",
        f"{API_URL}/attendances/{attendance_id}",
        token=faculty_token,
        expected_status=200,
    )
    assert_success(get_response, "get attendance detail")
    print_ok("Faculty can get attendance detail")

    print_step("Faculty update attendance")
    update_response = request_json(
        "PUT",
        f"{API_URL}/attendances/{attendance_id}",
        token=faculty_token,
        json={
            "course": "Computer Science",
            "lecture_no": 2,
        },
        expected_status=200,
    )
    assert_success(update_response, "update attendance")
    print_ok("Faculty can update attendance")

    print_step("Recognition invalid image should return 400")
    invalid_file_response = requests.post(
        f"{API_URL}/recognition/verify",
        headers={"Authorization": f"Bearer {faculty_token}"},
        files={"file": ("not-image.txt", b"this is not an image", "text/plain")},
        data={
            "course": "Computer Science",
            "lecture_no": "1",
        },
        timeout=30,
    )

    if invalid_file_response.status_code != 400:
        raise TestFailure(
            "Recognition invalid image expected status 400, "
            f"got {invalid_file_response.status_code}. Body: {invalid_file_response.text}"
        )

    print_ok("Recognition invalid image returns 400")

    print_step("Faculty delete attendance")
    delete_response = request_json(
        "DELETE",
        f"{API_URL}/attendances/{attendance_id}",
        token=faculty_token,
        expected_status=200,
    )
    assert_success(delete_response, "delete attendance")
    print_ok("Faculty can delete attendance")


def main() -> int:
    print("=" * 80)
    print("Face Attendance API Smoke Test")
    print(f"BASE_URL = {BASE_URL}")
    print("=" * 80)

    try:
        health_check()

        student = register_student()

        student_login = login(
            student["email"],
            student["password"],
            "student",
        )
        student_token = student_login["accessToken"]

        auth_me(student_token, "student")

        student_permission_tests(student_token, student["rollno"])

        faculty_tests(student)

        print("\n" + "=" * 80)
        print("ALL AVAILABLE TESTS PASSED")
        print("=" * 80)
        return 0

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to backend.")
        print("Hãy chắc chắn backend đang chạy:")
        print("uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload")
        return 1

    except TestFailure as exc:
        print(f"\n[FAILED] {exc}")
        return 1

    except Exception as exc:
        print(f"\n[UNEXPECTED ERROR] {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
