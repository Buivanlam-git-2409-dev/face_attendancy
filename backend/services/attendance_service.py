from typing import Optional
from backend.models import Attendance
from backend.repositories.attendance_repository import AttendanceRepository


class AttendanceService:
    @staticmethod
    def serialize_attendance(row: Attendance) -> dict:
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
    def list_attendances(
        roll_no: Optional[int] = None,
        course: Optional[str] = None,
        lecture_no: Optional[int] = None,
        marked_by: Optional[str] = None,
    ):
        query = Attendance.query

        if roll_no is not None:
            query = query.filter(Attendance.rollno == roll_no)

        if course:
            query = query.filter(Attendance.course == course)

        if lecture_no is not None:
            query = query.filter(Attendance.lecture_no == lecture_no)

        if marked_by:
            query = query.filter(Attendance.marked_by == marked_by)

        rows = query.order_by(
            Attendance.marked_date.desc(),
            Attendance.marked_time.desc(),
        ).all()

        return [AttendanceService.serialize_attendance(row) for row in rows]

    @staticmethod
    def mark_attendance(
        roll_no: int,
        course: str,
        lecture_no: int,
        marked_by: str,
    ):
        if not roll_no:
            return None, "rollNo is required"

        if not course:
            return None, "course is required"

        if lecture_no is None:
            return None, "lectureNo is required"

        already_marked = AttendanceRepository.is_already_marked_for_lecture(
            roll_no,
            course,
            lecture_no,
        )

        if already_marked:
            return None, "Attendance already marked for this lecture"

        row = AttendanceRepository.create_attendance(
            roll_no,
            course,
            lecture_no,
            marked_by,
        )

        return AttendanceService.serialize_attendance(row), None

    @staticmethod
    def get_attendance(att_id: int):
        row = AttendanceRepository.get_attendance_by_id(att_id)

        if not row:
            return None

        return AttendanceService.serialize_attendance(row)

    @staticmethod
    def update_attendance(
        att_id: int,
        roll_no: Optional[int] = None,
        course: Optional[str] = None,
        lecture_no: Optional[int] = None,
    ):
        row = AttendanceRepository.update_attendance(
            att_id,
            roll_no,
            course,
            lecture_no,
        )

        if not row:
            return None, "Attendance not found"

        return AttendanceService.serialize_attendance(row), None

    @staticmethod
    def delete_attendance(att_id: int):
        success = AttendanceRepository.delete_attendance(att_id)

        if not success:
            return False, "Attendance not found"

        return True, None

    # Backward compatibility aliases
    listAttendances = staticmethod(
        lambda rollNo=None, course=None, lectureNo=None, markedBy=None:
        AttendanceService.list_attendances(
            roll_no=rollNo,
            course=course,
            lecture_no=lectureNo,
            marked_by=markedBy,
        )
    )

    markAttendance = staticmethod(
        lambda rollNo, course, lectureNo, markedBy:
        AttendanceService.mark_attendance(
            roll_no=rollNo,
            course=course,
            lecture_no=lectureNo,
            marked_by=markedBy,
        )
    )

    getAttendance = staticmethod(
        lambda attId:
        AttendanceService.get_attendance(att_id=attId)
    )

    updateAttendance = staticmethod(
        lambda attId, rollNo=None, course=None, lectureNo=None:
        AttendanceService.update_attendance(
            att_id=attId,
            roll_no=rollNo,
            course=course,
            lecture_no=lectureNo,
        )
    )

    deleteAttendance = staticmethod(
        lambda attId:
        AttendanceService.delete_attendance(att_id=attId)
    )