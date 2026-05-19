from flask import Blueprint

v1Blueprint = Blueprint("v1", __name__, url_prefix="/v1")

from backend.api.v1 import (  # noqa: E402
    attendance_routes,
    auth_routes,
    faculty_routes,
    recognition_routes,
    student_routes,
)
