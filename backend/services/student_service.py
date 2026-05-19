from typing import Optional

from backend.models import Student


class StudentService:
    @staticmethod
    def serialize_student(student: Student, include_detail: bool = False) -> dict:
        data = {
            "id": getattr(student, "id", None),
            "rollno": student.rollno,
            "name": student.name,
            "semester": student.semester,
            "email": student.email,
        }

        if include_detail:
            data.update(
                {
                    "picPath": student.pic_path,
                    "registeredOn": (
                        student.registered_on.isoformat()
                        if student.registered_on
                        else None
                    ),
                }
            )

        return data

    @staticmethod
    def list_students():
        students = Student.query.order_by(Student.rollno).all()

        return [
            StudentService.serialize_student(student)
            for student in students
        ]

    @staticmethod
    def get_student_by_roll_no(roll_no: int) -> Optional[dict]:
        student = Student.query.filter_by(rollno=roll_no).first()

        if student is None:
            return None

        return StudentService.serialize_student(
            student,
            include_detail=True,
        )

    # Backward compatibility aliases
    listStudents = list_students
    getStudentByRollNo = get_student_by_roll_no