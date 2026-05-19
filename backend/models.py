from sqlalchemy.sql import func

from backend.extensions import db

class Student(db.Model):
    __tablename__ = 'Student'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(80))
    semester = db.Column(db.String(80))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(80))
    pic_path = db.Column(db.Text)
    registered_on = db.Column(db.DateTime)

class Faculty(db.Model):

    __tablename__ = 'Faculty'
    __table_args__ = {'extend_existing': True}

    f_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    course = db.Column(db.String(80))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(80))
    is_admin = db.Column(db.Boolean, default=False)
    registered_on = db.Column(db.DateTime)

class Attendance(db.Model):
    __tablename__ = 'Attendance'
    __table_args__ = {'extend_existing': True}

    att_id = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.Integer, db.ForeignKey('Student.rollno'))
    course = db.Column(db.String(80))
    lecture_no = db.Column(db.Integer)
    marked_by = db.Column(db.String(80))
    marked_date = db.Column(db.Date)
    marked_time = db.Column(db.Time)


class RecognitionJob(db.Model):
    __tablename__ = 'RecognitionJob'
    __table_args__ = {'extend_existing': True}

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
