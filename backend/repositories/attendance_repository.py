from datetime import datetime
from typing import Optional

from backend.extensions import db
from backend.models import Attendance


class AttendanceRepository:
    @staticmethod
    def has_any_attendance_for_roll_no(roll_no: int) -> bool:
        return Attendance.query.filter_by(rollno=roll_no).first() is not None

    @staticmethod
    def is_already_marked_for_lecture(
        roll_no: int,
        course: str,
        lecture_no: int,
    ) -> bool:
        return (
            Attendance.query.filter(
                Attendance.rollno == roll_no,
                Attendance.course == course,
                Attendance.lecture_no == lecture_no,
            ).first()
            is not None
        )

    @staticmethod
    def create_attendance(
        roll_no: int,
        course: str,
        lecture_no: int,
        marked_by: str,
    ) -> Attendance:
        now = datetime.now()

        attendance = Attendance(
            rollno=roll_no,
            course=course,
            lecture_no=lecture_no,
            marked_by=marked_by,
            marked_date=now.date(),
            marked_time=now.time(),
        )

        db.session.add(attendance)
        db.session.commit()

        return attendance

    @staticmethod
    def get_attendance_by_id(att_id: int) -> Optional[Attendance]:
        return Attendance.query.filter_by(att_id=att_id).first()

    @staticmethod
    def update_attendance(
        att_id: int,
        roll_no: Optional[int] = None,
        course: Optional[str] = None,
        lecture_no: Optional[int] = None,
    ) -> Optional[Attendance]:
        attendance = AttendanceRepository.get_attendance_by_id(att_id)

        if not attendance:
            return None

        if roll_no is not None:
            attendance.rollno = roll_no

        if course is not None:
            attendance.course = course

        if lecture_no is not None:
            attendance.lecture_no = lecture_no

        db.session.commit()

        return attendance

    @staticmethod
    def delete_attendance(att_id: int) -> bool:
        attendance = AttendanceRepository.get_attendance_by_id(att_id)

        if not attendance:
            return False

        db.session.delete(attendance)
        db.session.commit()

        return True
    # Backward compatibility aliases
    hasAnyAttendanceForRollNo = has_any_attendance_for_roll_no
    isAlreadyMarkedForLecture = is_already_marked_for_lecture
    createAttendance = create_attendance
    getAttendanceById = get_attendance_by_id
    updateAttendance = update_attendance
    deleteAttendance = delete_attendance