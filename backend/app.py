"""
Merged application entry point for the Facial Recognition Attendance System.

Merge strategy:
- FastAPI is the primary application because the React/Vite SPA consumes /api/v1/*.
- Flask is kept only as a compatibility bridge for Flask-SQLAlchemy and legacy routes.
- Legacy template routes are isolated under /legacy so they do not conflict with the SPA root (/)
  or the modern API routes.
- Shared concerns are kept once: database initialization, CORS, logging, health check, API routers.

Run:
    uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager
from functools import wraps

import cv2
import numpy as np
import face_recognition

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.middleware.wsgi import WSGIMiddleware

from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    Response,
)

# Make backend imports work whether the file is launched from project root or backend/.
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from backend.config import Config
from backend.logging_config import init_logging, get_logger
from backend.celery_app import init_celery_config
from backend.extensions import db
from backend.api.v1.auth_routes_fastapi import router as auth_router
from backend.api.v1.student_routes_fastapi import router as student_router
from backend.api.v1.faculty_routes_fastapi import router as faculty_router
from backend.api.v1.attendance_routes_fastapi import router as attendance_router
from backend.api.v1.recognition_routes_fastapi import router as recognition_router
from backend.api.error_handler import validation_exception_handler, general_exception_handler

try:
    from backend.face_detector import load_face_detector, detect_face_locations
    from backend.video_capture import VideoCapture
    from backend.models import Student, Faculty, Attendance
except ImportError:
    # Compatibility with the original flat Flask project layout.
    from backend.face_detector import load_face_detector, detect_face_locations
    from video_capture import VideoCapture
    from models import Student, Faculty, Attendance


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
log_level = os.getenv("LOG_LEVEL", "INFO")
init_logging(log_level)
log = get_logger(__name__)


# -----------------------------------------------------------------------------
# Legacy Flask app: keeps old template routes and Flask-SQLAlchemy compatibility.
# It is mounted under /legacy in FastAPI to avoid conflicts with the SPA/API root.
# -----------------------------------------------------------------------------
def create_legacy_flask_app() -> Flask:
    legacy_app = Flask(__name__)
    legacy_app.config.from_object(Config)

    # Keep env-based overrides compatible with the old file, but avoid hard-coded local paths.
    legacy_app.config.setdefault(
        "SQLALCHEMY_DATABASE_URI",
        os.getenv("DATABASE_URL", "sqlite:///db/database.db"),
    )
    legacy_app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    legacy_app.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY", "change-me"))

    # YOLO face detector config from the original Flask file.
    yolo_face_model_path = os.environ.get("YOLO_FACE_MODEL_PATH", "face_model/best.pt")
    yolo_face_conf = float(os.environ.get("YOLO_FACE_CONF", "0.50"))
    face_detector = load_face_detector(yolo_face_model_path)

    db.init_app(legacy_app)

    with legacy_app.app_context():
        db.create_all()

    def is_student_logged_in(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if "std_logged_in" in session:
                return f(*args, **kwargs)
            flash("Unauthorized, Please login!", "danger")
            return redirect(url_for("login_student"))

        return wrap

    def is_faculty_logged_in(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if "fty_logged_in" in session:
                return f(*args, **kwargs)
            flash("Unauthorized, Please login!", "danger")
            return redirect(url_for("login_faculty"))

        return wrap

    @legacy_app.route("/")
    def legacy_index():
        return render_template("index.html")

    @legacy_app.route("/login_student", methods=["GET", "POST"])
    def login_student():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            student = Student.query.filter_by(email=email, password=password).first()

            if student is not None:
                session["std_logged_in"] = True
                session["uname"] = email.split("@")[0]
                session["roll_no"] = student.rollno
                flash("You are now logged in", "success")
                return redirect(url_for("student"))

            return render_template("login_student.html", error="Invalid login")

        return render_template("login_student.html")

    @legacy_app.route("/login_faculty", methods=["GET", "POST"])
    def login_faculty():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            faculty = Faculty.query.filter_by(email=email, password=password).first()

            if faculty is not None:
                if faculty.is_admin:
                    session["is_admin"] = True
                session["fty_logged_in"] = True
                session["uname"] = email.split("@")[0]
                session["name"] = faculty.name
                session["course"] = faculty.course
                flash("You are now logged in", "success")
                return redirect(url_for("faculty"))

            return render_template("login_faculty.html", error="Invalid login")

        return render_template("login_faculty.html")

    @legacy_app.route("/student")
    @is_student_logged_in
    def student():
        courses = (
            Attendance.query.filter_by(rollno=session["roll_no"])
            .with_entities(Attendance.course)
            .distinct()
            .order_by(Attendance.course)
            .all()
        )
        lectures_count = [
            Attendance.query.filter_by(rollno=session["roll_no"], course=course[0]).count()
            for course in courses
        ]
        legacy_app.logger.info(lectures_count)
        return render_template(
            "dashboard_student.html", courses=courses, lectures_count=lectures_count
        )

    @legacy_app.route("/my_attendance")
    @is_student_logged_in
    def view_attendance():
        unique_courses = (
            Attendance.query.filter_by(rollno=session["roll_no"])
            .with_entities(Attendance.course)
            .distinct()
            .order_by(Attendance.course)
            .all()
        )
        course = request.args.get("course")
        if course is None and unique_courses:
            course = unique_courses[0][0]

        attendance = Attendance.query.filter_by(
            rollno=session["roll_no"], course=course
        ).all()
        return render_template(
            "view_attendance.html",
            unique_courses=unique_courses,
            attendance=attendance,
        )

    @legacy_app.route("/faculty")
    @is_faculty_logged_in
    def faculty():
        lectures_count = (
            Attendance.query.filter_by(marked_by=session["name"])
            .with_entities(Attendance.lecture_no)
            .distinct()
            .count()
        )
        students_count = Student.query.with_entities(Student.rollno).count()
        faculty_count = Faculty.query.with_entities(Faculty.f_id).count()
        return render_template(
            "dashboard_faculty.html",
            lectures_count=lectures_count,
            students_count=students_count,
            faculty_count=faculty_count,
        )

    @legacy_app.route("/faculty_registration", methods=["GET", "POST"])
    @is_faculty_logged_in
    def register_faculty():
        if request.method == "POST":
            existing_faculty = Faculty.query.filter_by(email=request.form["email"]).first()
            is_admin = "isAdmin" in request.form

            if existing_faculty is None:
                faculty = Faculty(
                    name=request.form["name"],
                    course=request.form["course"],
                    email=request.form["email"],
                    password=request.form["password"],
                    is_admin=is_admin,
                    registered_on=datetime.now(),
                )
                db.session.add(faculty)
                db.session.commit()
                flash("Faculty registration successful", "success")
                return render_template("register_faculty.html")

            flash("Faculty with this email already exists!", "danger")

        return render_template("register_faculty.html")

    @legacy_app.route("/student_registration", methods=["GET", "POST"])
    @is_faculty_logged_in
    def register_student():
        if request.method == "POST":
            existing_student = Student.query.filter_by(email=request.form["email"]).first()

            if existing_student is None:
                image_path = (
                    f'static/images/users/{request.form["rollno"]}-'
                    f'{request.form["name"]}.jpg'
                )
                new_student = Student(
                    rollno=request.form["rollno"],
                    name=request.form["name"],
                    semester=request.form["semester"],
                    email=request.form["email"],
                    password=request.form["password"],
                    pic_path=image_path,
                    registered_on=datetime.now(),
                )
                db.session.add(new_student)
                db.session.commit()

                if os.path.isfile("static/images/users/temp.jpg"):
                    os.rename("static/images/users/temp.jpg", image_path)
                session.pop("img_captured", None)
                flash("Student registration successful", "success")
                return render_template("register_student.html")

            flash("Student with this email already exists!", "danger")

        temp_pic = os.path.isfile("static/images/users/temp.jpg")
        return render_template("register_student.html", temp_pic=temp_pic)

    @legacy_app.route("/capture_image")
    @is_faculty_logged_in
    def capture_image():
        session["dt"] = datetime.now()
        path = "static/images/users"
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Press c to capture image", frame)
            if cv2.waitKey(1) & 0xFF == ord("c"):
                cv2.imwrite(os.path.join(path, "temp.jpg"), frame)
                time.sleep(2)
                break

        cap.release()
        cv2.destroyAllWindows()
        session["img_captured"] = True
        return redirect(url_for("register_student"))

    @legacy_app.route("/attendance", methods=["GET", "POST"])
    @is_faculty_logged_in
    def mark_attendance_1():
        std_reg = Student.query.count() > 0
        if request.method == "POST":
            session["lecture_no"] = request.form["lecture"]
            return redirect(url_for("mark_attendance_2"))
        return render_template("mark_attendance_1.html", std_reg=std_reg)

    @legacy_app.route("/attendance/fr")
    @is_faculty_logged_in
    def mark_attendance_2():
        return render_template("mark_attendance_2.html")

    @legacy_app.route("/view_lectures_attendance/")
    @is_faculty_logged_in
    def view_lectures_attendance():
        lect_no = request.args.get("lecture") or 1
        unique_lect_no = (
            Attendance.query.filter_by(marked_by=session["name"])
            .with_entities(Attendance.lecture_no)
            .distinct()
            .order_by(Attendance.lecture_no)
            .all()
        )
        attendance = Attendance.query.filter_by(
            lecture_no=lect_no, marked_by=session["name"]
        ).all()
        return render_template(
            "view_lecture_attendance.html",
            unique_lect_no=unique_lect_no,
            attendance=attendance,
        )

    @legacy_app.route("/facultydownloadcsv", defaults={"lect_no": 1})
    @legacy_app.route("/facultydownloadcsv/<int:lect_no>")
    @is_faculty_logged_in
    def download_attendance_csv(lect_no):
        headings = "Roll_no,Course,Lecture_no,Marked_by,Marking_date,Marking_Time\n"
        attendance = Attendance.query.filter_by(
            lecture_no=lect_no, marked_by=session["name"]
        ).all()
        rows = "".join(
            f"{a.rollno},{a.course},{a.lecture_no},{a.marked_by},{a.marked_date},{a.marked_time} \n"
            for a in attendance
        )
        return Response(
            headings + rows,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=attendance.csv"},
        )

    @legacy_app.route("/studentdownloadcsv", defaults={"course": None})
    @legacy_app.route("/studentdownloadcsv/<string:course>")
    @is_student_logged_in
    def download_student_attendance_csv(course):
        headings = "Roll_no,Course,Lecture_no,Marked_by,Marking_date,Marking_Time\n"
        attendance = Attendance.query.filter_by(
            rollno=session["roll_no"], course=course
        ).all()
        rows = "".join(
            f"{a.rollno},{a.course},{a.lecture_no},{a.marked_by},{a.marked_date},{a.marked_time} \n"
            for a in attendance
        )
        return Response(
            headings + rows,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=my_attendance.csv"},
        )

    @legacy_app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("legacy_index"))

    @legacy_app.route("/fr_attendance")
    @is_faculty_logged_in
    def mark_face_attendance():
        """Legacy desktop OpenCV attendance flow.

        This is preserved for compatibility. For the SPA/camera flow, prefer the
        modern /api/v1 recognition router.
        """
        video_capture = VideoCapture(0)
        known_face_encodings = []
        known_face_names = []
        users_dir = "static/images/users"
        allowed_ext = (".jpg", ".jpeg", ".png")

        if not os.path.isdir(users_dir):
            video_capture.release()
            flash("Registered user image folder not found!", "danger")
            return redirect(url_for("mark_attendance_2"))

        for filename in os.listdir(users_dir):
            if not filename.lower().endswith(allowed_ext):
                continue

            image_path = os.path.join(users_dir, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if not encodings:
                legacy_app.logger.warning("No face found in registered image: %s", image_path)
                continue

            known_face_names.append(os.path.splitext(filename)[0])
            known_face_encodings.append(encodings[0])

        if not known_face_encodings:
            video_capture.release()
            flash("No valid registered student face images found!", "danger")
            return redirect(url_for("mark_attendance_2"))

        face_locations = []
        face_names = []
        marked_rolls_in_frame = set()
        process_this_frame = True

        while True:
            frame = video_capture.read()
            marked_rolls_in_frame.clear()

            if process_this_frame:
                face_locations = detect_face_locations(
                    frame,
                    detector=face_detector,
                    conf=yolo_face_conf,
                )
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                face_names = []

                for face_encoding in face_encodings:
                    roll_name = "Unknown"
                    face_distances = face_recognition.face_distance(
                        known_face_encodings, face_encoding
                    )

                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        matches = face_recognition.compare_faces(
                            known_face_encodings, face_encoding
                        )

                        if matches[best_match_index]:
                            roll_name = known_face_names[best_match_index]
                            roll = roll_name.split("-")[0]

                            is_marked_already = Attendance.query.filter(
                                Attendance.rollno == int(roll),
                                Attendance.course == session["course"],
                                Attendance.lecture_no == int(session["lecture_no"]),
                            ).first()

                            if is_marked_already is None:
                                attendance = Attendance(
                                    rollno=int(roll),
                                    course=session["course"],
                                    lecture_no=int(session["lecture_no"]),
                                    marked_by=session["name"],
                                    marked_date=datetime.now().date(),
                                    marked_time=datetime.now().time(),
                                )
                                db.session.add(attendance)
                                db.session.commit()
                                marked_rolls_in_frame.add(roll)
                                print("marked", roll_name)

                    face_names.append(roll_name)

            process_this_frame = not process_this_frame

            for (top, right, bottom, left), roll_name in zip(face_locations, face_names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, roll_name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

                roll = roll_name.split("-")[0]
                if roll in marked_rolls_in_frame:
                    cv2.putText(frame, "Marked", (left + 12, bottom - 24), font, 0.5, (255, 255, 255), 1)

            cv2.imshow("Marking attendance - YOLO Face Detector", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        video_capture.release()
        cv2.destroyAllWindows()
        return redirect(url_for("mark_attendance_2"))

    return legacy_app


legacy_flask_app = create_legacy_flask_app()
legacy_flask_ctx = legacy_flask_app.app_context()
legacy_flask_ctx.push()


# -----------------------------------------------------------------------------
# Modern FastAPI app for SPA/API
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("application_startup")
    with legacy_flask_app.app_context():
        db.create_all()
        log.info("database_initialized")

    init_celery_config()
    log.info("celery_initialized")
    yield

    db.session.remove()
    legacy_flask_ctx.pop()
    log.info("application_shutdown")


app = FastAPI(
    title="Facial Recognition Attendance API",
    description="Modern async API for facial recognition attendance system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://localhost:3000",
    ).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_session_middleware(request, call_next):
    try:
        response = await call_next(request)
        return response
    finally:
        db.session.remove()


@app.middleware("http")
async def logging_middleware(request, call_next):
    log.info(
        "request_received",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None,
    )
    response = await call_next(request)
    log.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    return response


app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(student_router, prefix="/api/v1", tags=["Students"])
app.include_router(faculty_router, prefix="/api/v1", tags=["Faculty"])
app.include_router(attendance_router, prefix="/api/v1", tags=["Attendance"])
app.include_router(recognition_router, prefix="/api/v1", tags=["Recognition"])


@app.get("/health")
async def health_check():
    log.info("health_check")
    return {"status": "ok", "service": "facial-recognition-api"}


@app.get("/")
async def root():
    return {
        "message": "Attendance API - Use frontend SPA or /docs for API documentation",
        "docs": "/docs",
        "health": "/health",
        "legacy": "/legacy",
    }


# Legacy template UI is still available at /legacy/*.
app.mount("/legacy", WSGIMiddleware(legacy_flask_app))


if __name__ == "__main__":
    import uvicorn

    log.info("starting_server", host="0.0.0.0", port=8000)
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )