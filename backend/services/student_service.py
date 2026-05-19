from backend.models import Student


class StudentService:
    @staticmethod
    def listStudents():
        students = Student.query.order_by(Student.rollno).all()
        return [
            {
                "rollno": student.rollno,
                "name": student.name,
                "semester": student.semester,
                "email": student.email,
            }
            for student in students
        ]

    @staticmethod
    def getStudentByRollNo(rollNo: int):
        student = Student.query.filter_by(rollno=rollNo).first()
        if student is None:
            return None
        return {
            "rollno": student.rollno,
            "name": student.name,
            "semester": student.semester,
            "email": student.email,
            "picPath": student.pic_path,
            "registeredOn": student.registered_on.isoformat() if student.registered_on else None,
        }
