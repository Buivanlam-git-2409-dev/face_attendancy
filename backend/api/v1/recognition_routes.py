from flask import current_app, request, session

from backend.api.v1 import v1Blueprint
from backend.api.v1.responses import errorResponse, successResponse
from backend.services.recognition_job_service import RecognitionJobService


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


def queueRecognitionJob(payload):
    course = payload.get("course") or session.get("course")
    lectureNo = parseInt(payload.get("lecture_no") or session.get("lecture_no"))
    durationSeconds = parseInt(payload.get("duration_seconds")) or 30
    markedBy = session.get("name")
    if not course or lectureNo is None or not markedBy:
        return None, errorResponse("INVALID_PAYLOAD", "course and lecture_no are required", 400)
    if durationSeconds < 5 or durationSeconds > 600:
        return None, errorResponse("INVALID_PAYLOAD", "duration_seconds must be between 5 and 600", 400)

    app = current_app._get_current_object()
    job = RecognitionJobService.createAndStartJob(
        app=app,
        course=course,
        lectureNo=lectureNo,
        markedBy=markedBy,
        durationSeconds=durationSeconds,
    )
    return job, None


@v1Blueprint.route("/recognition/attendance/run", methods=["POST"])
def runRecognitionAttendanceApi():
    authError = ensureFacultySession()
    if authError is not None:
        return authError

    payload = request.get_json(silent=True) or {}
    job, error = queueRecognitionJob(payload)
    if error is not None:
        return error
    return successResponse({"message": "Recognition job queued", "job": job}, statusCode=202)


@v1Blueprint.route("/recognition/jobs", methods=["POST"])
def createRecognitionJobApi():
    authError = ensureFacultySession()
    if authError is not None:
        return authError

    payload = request.get_json(silent=True) or {}
    job, error = queueRecognitionJob(payload)
    if error is not None:
        return error
    return successResponse(job, statusCode=202)


@v1Blueprint.route("/recognition/jobs/<string:jobId>", methods=["GET"])
def getRecognitionJobApi(jobId: str):
    authError = ensureFacultySession()
    if authError is not None:
        return authError

    job = RecognitionJobService.getJob(jobId)
    if job is None:
        return errorResponse("NOT_FOUND", "Recognition job not found", 404)
    return successResponse(job)
