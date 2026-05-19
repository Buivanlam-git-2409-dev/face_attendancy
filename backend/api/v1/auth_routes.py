from flask import request, session

from backend.api.v1 import v1Blueprint
from backend.api.v1.responses import errorResponse, successResponse
from backend.services.auth_service import AuthService
from backend.security import (
    generate_token,
    generate_refresh_token,
    verify_refresh_token,
)


@v1Blueprint.route("/auth/login", methods=["POST"])
def loginApi():
    payload = request.get_json(silent=True) or {}
    email = payload.get("email")
    password = payload.get("password")
    role = payload.get("role")

    if not email or not password:
        return errorResponse("INVALID_PAYLOAD", "email and password are required", 400)

    if role == "student":
        student = AuthService.authenticateStudent(email=email, password=password)
        if student is None:
            return errorResponse("INVALID_CREDENTIALS", "Invalid login", 401)
        session["std_logged_in"] = True
        session["roll_no"] = student.rollno
        return successResponse({
            "role": "student",
            "user": {
                "rollno": student.rollno,
                "name": student.name,
                "email": student.email,
            },
        })

    if role is None:
        student = AuthService.authenticateStudent(email=email, password=password)
        if student is not None:
            session["std_logged_in"] = True
            session["roll_no"] = student.rollno
            return successResponse({
                "role": "student",
                "user": {
                    "rollno": student.rollno,
                    "name": student.name,
                    "email": student.email,
                },
            })

    faculty = AuthService.authenticateFaculty(email=email, password=password)
    if faculty is None:
        return errorResponse("INVALID_CREDENTIALS", "Invalid login", 401)

    session["fty_logged_in"] = True
    session["fty_id"] = faculty.f_id
    session["name"] = faculty.name
    session["course"] = faculty.course
    session["is_admin"] = bool(faculty.is_admin)
    return successResponse({
        "role": "faculty",
        "user": {
            "id": faculty.f_id,
            "name": faculty.name,
            "email": faculty.email,
            "course": faculty.course,
            "isAdmin": bool(faculty.is_admin),
        },
    })


@v1Blueprint.route("/auth/token", methods=["POST"])
def getTokenApi():
    """Generate JWT tokens for API client authentication"""
    payload = request.get_json(silent=True) or {}
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        return errorResponse("INVALID_PAYLOAD", "email and password are required", 400)

    student = AuthService.authenticateStudent(email=email, password=password)
    if student:
        access_token = generate_token(user_id=student.rollno, role="student")
        refresh_token = generate_refresh_token(user_id=student.rollno, role="student")
        return successResponse({
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": {
                "rollno": student.rollno,
                "name": student.name,
                "email": student.email,
                "role": "student",
            },
        })

    faculty = AuthService.authenticateFaculty(email=email, password=password)
    if faculty:
        access_token = generate_token(
            user_id=faculty.f_id,
            role="faculty",
            is_admin=bool(faculty.is_admin)
        )
        refresh_token = generate_refresh_token(user_id=faculty.f_id, role="faculty")
        return successResponse({
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": {
                "id": faculty.f_id,
                "name": faculty.name,
                "email": faculty.email,
                "course": faculty.course,
                "isAdmin": bool(faculty.is_admin),
                "role": "faculty",
            },
        })

    return errorResponse("INVALID_CREDENTIALS", "Invalid email or password", 401)


@v1Blueprint.route("/auth/refresh", methods=["POST"])
def refreshTokenApi():
    """Refresh access token using refresh token"""
    payload = request.get_json(silent=True) or {}
    refresh_token = payload.get("refreshToken")

    if not refresh_token:
        return errorResponse("INVALID_PAYLOAD", "refreshToken is required", 400)

    token_payload = verify_refresh_token(refresh_token)
    if not token_payload:
        return errorResponse("INVALID_TOKEN", "Invalid or expired refresh token", 401)

    user_id = token_payload.get("user_id")
    role = token_payload.get("role")
    is_admin = token_payload.get("is_admin", False)

    access_token = generate_token(user_id=user_id, role=role, is_admin=is_admin)
    return successResponse({
        "accessToken": access_token,
    })


@v1Blueprint.route("/auth/me", methods=["GET"])
def getMeApi():
    if "std_logged_in" in session:
        return successResponse({
            "role": "student",
            "user": {
                "rollno": session.get("roll_no"),
            },
        })

    if "fty_logged_in" in session:
        return successResponse({
            "role": "faculty",
            "user": {
                "name": session.get("name"),
                "course": session.get("course"),
                "isAdmin": session.get("is_admin", False),
            },
        })

    return errorResponse("UNAUTHORIZED", "Not logged in", 401)


@v1Blueprint.route("/auth/logout", methods=["POST"])
def logoutApi():
    session.clear()
    return successResponse({"message": "Logged out"})
