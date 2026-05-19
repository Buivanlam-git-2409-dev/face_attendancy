from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from backend.extensions import db

class Role(db.Model):
    __tablename__ = "Role"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<Role {self.name}>"

class User(db.Model):
    __tablename__ = "User"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("Role.id"))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    role = db.relationship("Role", backref=db.backref("users", lazy=True))

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<User {self.email}>"

class Student(db.Model):
    __tablename__ = "Student"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=True)
    rollno = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(80))
    semester = db.Column(db.String(80))
    email = db.Column(db.String(100), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    pic_path = db.Column(db.Text)
    registered_on = db.Column(db.DateTime)

    user = db.relationship("User", backref=db.backref("student_profile", uselist=False))

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

class Faculty(db.Model):
    __tablename__ = "Faculty"
    __table_args__ = {"extend_existing": True}

    f_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=True)
    name = db.Column(db.String(80))
    course = db.Column(db.String(80))
    email = db.Column(db.String(100), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    registered_on = db.Column(db.DateTime)

    user = db.relationship("User", backref=db.backref("faculty_profile", uselist=False))

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

class Department(db.Model):
    __tablename__ = "Department"
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True)

class Semester(db.Model):
    __tablename__ = "Semester"
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False) # e.g., Fall 2024
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)

class Course(db.Model):
    __tablename__ = "Course"
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False) # e.g., CS101
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("Department.id"))
    credits = db.Column(db.Integer, default=3)

    department = db.relationship("Department", backref="courses")

class ClassRoom(db.Model):
    __tablename__ = "ClassRoom"
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g., A-101
    capacity = db.Column(db.Integer)

class Enrollment(db.Model):
    __tablename__ = "Enrollment"
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("Student.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("Course.id"), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey("Semester.id"), nullable=False)
    enrolled_at = db.Column(db.DateTime, server_default=func.now())

    student = db.relationship("Student", backref="enrollments")
    course = db.relationship("Course", backref="enrollments")
    semester = db.relationship("Semester", backref="enrollments")

class AttendanceSession(db.Model):
    __tablename__ = "AttendanceSession"
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("Course.id"), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("Faculty.f_id"), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey("ClassRoom.id"))
    semester_id = db.Column(db.Integer, db.ForeignKey("Semester.id"))
    
    lecture_no = db.Column(db.Integer)
    session_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    status = db.Column(db.String(20), default='scheduled') # scheduled, active, completed, cancelled

    course = db.relationship("Course", backref="sessions")
    faculty = db.relationship("Faculty", backref="sessions")
    classroom = db.relationship("ClassRoom", backref="sessions")

class AttendanceRecord(db.Model):
    __tablename__ = "AttendanceRecord"
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("AttendanceSession.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("Student.id"), nullable=False)
    
    status = db.Column(db.String(20), default='PRESENT') # PRESENT, ABSENT, LATE, EXCUSED
    marked_at = db.Column(db.DateTime, server_default=func.now())
    marking_method = db.Column(db.String(20), default='FACE') # FACE, MANUAL

    session = db.relationship("AttendanceSession", backref="records")
    student = db.relationship("Student", backref="attendance_records")

class FaceEmbedding(db.Model):
    __tablename__ = "FaceEmbedding"
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("Student.id"), nullable=False)
    embedding = db.Column(db.JSON, nullable=False) # Store as JSON array of floats
    created_at = db.Column(db.DateTime, server_default=func.now())

    student = db.relationship("Student", backref="embeddings")

class Attendance(db.Model):
    __tablename__ = "Attendance"
    __table_args__ = {"extend_existing": True}

    att_id = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.Integer, db.ForeignKey("Student.rollno"))
    course = db.Column(db.String(80))
    lecture_no = db.Column(db.Integer)
    marked_by = db.Column(db.String(80))
    marked_date = db.Column(db.Date)
    marked_time = db.Column(db.Time)


class RecognitionJob(db.Model):
    __tablename__ = "RecognitionJob"
    __table_args__ = {"extend_existing": True}

    job_id = db.Column(db.String(64), primary_key=True)
    course = db.Column(db.String(80), nullable=False)
    lecture_no = db.Column(db.Integer, nullable=False)
    marked_by = db.Column(db.String(80), nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False, default=30)
    status = db.Column(db.String(20), nullable=False, default='queued')
    marked_count = db.Column(db.Integer, nullable=False, default=0)
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime, server_default=func.now())
    finished_at = db.Column(db.DateTime)
