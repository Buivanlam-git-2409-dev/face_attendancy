#!/usr/bin/env python
"""Add test data for frontend MVP testing"""
from backend.legacy.flask_app import legacy_flask_app
from backend.extensions import db
from backend.models import Faculty, Student
from datetime import datetime

with legacy_flask_app.app_context():
    # Add test faculty
    faculty = Faculty(
        name='Dr. Smith',
        email='faculty@dev.com',
        course='CS101',
        is_admin=False,
        registered_on=datetime.now(),
    )
    faculty.set_password('faculty123')
    db.session.add(faculty)
    db.session.commit()
    print('✓ Faculty added: faculty@dev.com / faculty123')

    # Add test student
    student = Student(
        rollno=1001,
        name='John Student',
        semester='5',
        email='student@dev.com',
        pic_path='static/images/users/1001-John_Student.jpg',
        registered_on=datetime.now(),
    )
    student.set_password('student123')
    db.session.add(student)
    db.session.commit()
    print('✓ Student added: student@dev.com / student123 (roll: 1001)')

    print('\nTest credentials ready!')
