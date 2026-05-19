import os
import time
import cv2
import numpy as np
import face_recognition
from datetime import datetime
from functools import wraps
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

from backend.config import Config
from backend.extensions import db
from backend.services.auth_service import AuthService
from backend.face_detector import load_face_detector, detect_face_locations
from backend.video_capture import VideoCapture
from backend.models import Student, Faculty, Attendance

def create_legacy_flask_app() -> Flask:
    legacy_app = Flask(__name__, 
                       template_folder="../templates", 
                       static_folder="../static")
    legacy_app.config.from_object(Config)

    # Keep env-based overrides compatible with the old file
    legacy_app.config.setdefault(
        "SQLALCHEMY_DATABASE_URI",
        os.getenv("DATABASE_URL", "sqlite:///db/database.db"),
    )
    legacy_app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    legacy_app.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY", "change-me"))

    # YOLO face detector config from the original Flask file.
    yolo_face_model_path = Config.YOLO_FACE_MODEL_PATH
    yolo_face_conf = Config.YOLO_FACE_CONF
    face_detector = load_face_detector(yolo_face_model_path)

    db.init_app(legacy_app)

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
            student = AuthService.authenticate_student(email=email, password=password)

            if student is not None:
                session["uname"] = email.split("@")[0]
                session["roll_no"] = student.rollno
                session["std_logged_in"] = True
                flash("You are now logged in", "success")
                return redirect(url_for("student"))

            return render_template("login_student.html", error="Invalid login")

        return render_template("login_student.html")

    @legacy_app.route("/login_faculty", methods=["GET", "POST"])
    def login_faculty():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            faculty = AuthService.authenticate_faculty(email=email, password=password)

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
            name = request.form["name"]
            course = request.form["course"]
            email = request.form["email"]
            password = request.form["password"]
            is_admin = "isAdmin" in request.form

            faculty, error = AuthService.registerFaculty(
                name=name,
                course=course,
                email=email,
                password=password,
                isAdmin=is_admin
            )

            if faculty:
                flash("Faculty registration successful", "success")
                return render_template("register_faculty.html")

            flash(error or "Registration failed", "danger")

        return render_template("register_faculty.html")

    @legacy_app.route("/student_registration", methods=["GET", "POST"])
    @is_faculty_logged_in
    def register_student():
        if request.method == "POST":
            rollno = request.form["rollno"]
            name = request.form["name"]
            semester = request.form["semester"]
            email = request.form["email"]
            password = request.form["password"]

            image_path = f"static/images/users/{rollno}-{name}.jpg"

            student, error = AuthService.registerStudent(
                rollno=int(rollno),
                name=name,
                semester=semester,
                email=email,
                password=password,
                picPath=image_path
            )

            if student:
                if os.path.isfile("static/images/users/temp.jpg"):
                    os.rename("static/images/users/temp.jpg", image_path)
                session.pop("img_captured", None)
                flash("Student registration successful", "success")
                return render_template("register_student.html")

            flash(error or "Registration failed", "danger")

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
        """Legacy desktop OpenCV attendance flow."""
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

                    face_names.append(roll_name)

            process_this_frame = not process_this_frame

            for (top, right, bottom, left), roll_name in zip(face_locations, face_names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, roll_name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

            cv2.imshow("Marking attendance - YOLO Face Detector", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        video_capture.release()
        cv2.destroyAllWindows()
        return redirect(url_for("mark_attendance_2"))

    return legacy_app

legacy_flask_app = create_legacy_flask_app()
