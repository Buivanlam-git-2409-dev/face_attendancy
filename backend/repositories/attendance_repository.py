from datetime import datetime

from backend.extensions import db
from backend.models import Attendance


class AttendanceRepository:
    @staticmethod
    def hasAnyAttendanceForRollNo(rollNo: int) -> bool:
        return Attendance.query.filter_by(rollno=rollNo).first() is not None

    @staticmethod
    def isAlreadyMarkedForLecture(rollNo: int, course: str, lectureNo: int) -> bool:
        row = Attendance.query.filter(
            Attendance.rollno == rollNo,
            Attendance.course == course,
            Attendance.lecture_no == lectureNo,
        ).first()
        return row is not None

    @staticmethod
    def createAttendance(rollNo: int, course: str, lectureNo: int, markedBy: str):
        attendance = Attendance(
            rollno=rollNo,
            course=course,
            lecture_no=lectureNo,
            marked_by=markedBy,
            marked_date=datetime.date(datetime.now()),
            marked_time=datetime.time(datetime.now()),
        )
        db.session.add(attendance)
        db.session.commit()
        return attendance

    @staticmethod
    def getAttendanceById(attId: int):
        return Attendance.query.filter_by(att_id=attId).first()

    @staticmethod
    def updateAttendance(attId: int, rollNo: int = None, course: str = None, lectureNo: int = None):
        attendance = Attendance.query.filter_by(att_id=attId).first()
        if not attendance:
            return None
        
        if rollNo is not None:
            attendance.rollno = rollNo
        if course is not None:
            attendance.course = course
        if lectureNo is not None:
            attendance.lecture_no = lectureNo
        
        db.session.commit()
        return attendance

    @staticmethod
    def deleteAttendance(attId: int) -> bool:
        attendance = Attendance.query.filter_by(att_id=attId).first()
        if not attendance:
            return False
        
        db.session.delete(attendance)
        db.session.commit()
        return True
