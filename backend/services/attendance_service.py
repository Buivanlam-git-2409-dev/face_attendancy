from backend.repositories.attendance_repository import AttendanceRepository
from backend.models import Attendance


class AttendanceService:
    @staticmethod
    def listAttendances(rollNo=None, course=None, lectureNo=None, markedBy=None):
        query = Attendance.query
        if rollNo is not None:
            query = query.filter(Attendance.rollno == rollNo)
        if course:
            query = query.filter(Attendance.course == course)
        if lectureNo is not None:
            query = query.filter(Attendance.lecture_no == lectureNo)
        if markedBy:
            query = query.filter(Attendance.marked_by == markedBy)

        rows = query.order_by(Attendance.marked_date.desc(), Attendance.marked_time.desc()).all()
        return [
            {
                "attendanceId": row.att_id,
                "rollno": row.rollno,
                "course": row.course,
                "lectureNo": row.lecture_no,
                "markedBy": row.marked_by,
                "markedDate": row.marked_date.isoformat() if row.marked_date else None,
                "markedTime": row.marked_time.isoformat() if row.marked_time else None,
            }
            for row in rows
        ]

    @staticmethod
    def markAttendance(rollNo: int, course: str, lectureNo: int, markedBy: str):
        if AttendanceRepository.isAlreadyMarkedForLecture(rollNo, course, lectureNo):
            return None, "Attendance already marked for this lecture"
        row = AttendanceRepository.createAttendance(rollNo, course, lectureNo, markedBy)
        return {
            "attendanceId": row.att_id,
            "rollno": row.rollno,
            "course": row.course,
            "lectureNo": row.lecture_no,
            "markedBy": row.marked_by,
        }, None

    @staticmethod
    def getAttendance(attId: int):
        row = AttendanceRepository.getAttendanceById(attId)
        if not row:
            return None
        return {
            "attendanceId": row.att_id,
            "rollno": row.rollno,
            "course": row.course,
            "lectureNo": row.lecture_no,
            "markedBy": row.marked_by,
            "markedDate": row.marked_date.isoformat() if row.marked_date else None,
            "markedTime": row.marked_time.isoformat() if row.marked_time else None,
        }

    @staticmethod
    def updateAttendance(attId: int, rollNo: int = None, course: str = None, lectureNo: int = None):
        row = AttendanceRepository.updateAttendance(attId, rollNo, course, lectureNo)
        if not row:
            return None, "Attendance not found"
        return {
            "attendanceId": row.att_id,
            "rollno": row.rollno,
            "course": row.course,
            "lectureNo": row.lecture_no,
            "markedBy": row.marked_by,
        }, None

    @staticmethod
    def deleteAttendance(attId: int):
        success = AttendanceRepository.deleteAttendance(attId)
        if not success:
            return False, "Attendance not found"
        return True, None
