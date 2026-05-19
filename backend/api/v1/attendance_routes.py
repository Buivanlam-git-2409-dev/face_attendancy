from flask import request, session

from backend.api.v1 import v1Blueprint
from backend.api.v1.responses import errorResponse, successResponse
from backend.services.attendance_service import AttendanceService


def parseInt(value):
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def ensureFacultySession():
    if "fty_logged_in" not in session:
        return errorResponse("UNAUTHORIZED", "Faculty authentication required", 401)
    return None


@v1Blueprint.route("/attendances", methods=["GET"])
def listAttendancesApi():
    authError = ensureFacultySession()
    if authError is not None:
        return authError

    rollNo = parseInt(request.args.get("rollno"))
    lectureNo = parseInt(request.args.get("lecture_no"))
    course = request.args.get("course")
    markedBy = request.args.get("marked_by")
    data = AttendanceService.listAttendances(
        rollNo=rollNo,
        course=course,
        lectureNo=lectureNo,
        markedBy=markedBy,
    )
    return successResponse(data)


@v1Blueprint.route("/attendances", methods=["POST"])
def markAttendanceApi():
    authError = ensureFacultySession()
    if authError is not None:
        return authError

    payload = request.get_json(silent=True) or {}
    rollNo = parseInt(payload.get("rollno"))
    lectureNo = parseInt(payload.get("lecture_no"))
    course = payload.get("course")

    if rollNo is None or lectureNo is None or not course:
        return errorResponse("INVALID_PAYLOAD", "rollno, course, lecture_no are required", 400)

    markedBy = session.get("name")
    data, error = AttendanceService.markAttendance(
        rollNo=rollNo,
        course=course,
        lectureNo=lectureNo,
        markedBy=markedBy,
    )
    if error is not None:
        return errorResponse("ALREADY_MARKED", error, 409)
    return successResponse(data, statusCode=201)


@v1Blueprint.route("/attendances/<int:attId>", methods=["PUT"])
def updateAttendanceApi(attId: int):
    authError = ensureFacultySession()
    if authError is not None:
        return authError

    payload = request.get_json(silent=True) or {}
    rollNo = parseInt(payload.get("rollno"))
    lectureNo = parseInt(payload.get("lecture_no"))
    course = payload.get("course")

    data, error = AttendanceService.updateAttendance(
        attId=attId,
        rollNo=rollNo,
        course=course,
        lectureNo=lectureNo,
    )
    if error is not None:
        return errorResponse("NOT_FOUND", error, 404)
    return successResponse(data)


@v1Blueprint.route("/attendances/<int:attId>", methods=["DELETE"])
def deleteAttendanceApi(attId: int):
    authError = ensureFacultySession()
    if authError is not None:
        return authError

    success, error = AttendanceService.deleteAttendance(attId)
    if error is not None:
        return errorResponse("NOT_FOUND", error, 404)
    return successResponse({"message": "Attendance record deleted"})
