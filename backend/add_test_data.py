#!/usr/bin/env python
"""Add test data for frontend MVP testing"""
from app import db, app
from models import Faculty, Student
from backend.security import hash_password
from datetime import datetime

with app.app_context():
    # Add test faculty
    faculty = Faculty(
        name='Dr. Smith',
        email='faculty@dev.com',
        password=hash_password('faculty123'),
        course='CS101',
        is_admin=False,
        registered_on=datetime.now(),
    )
    db.session.add(faculty)
    db.session.commit()
    print('✓ Faculty added: faculty@dev.com / faculty123')

    # Add test student
    student = Student(
        rollno=1001,
        name='John Student',
        semester='5',
        email='student@dev.com',
        password=hash_password('student123'),
        pic_path='static/images/users/1001-John_Student.jpg',
        registered_on=datetime.now(),
    )
    db.session.add(student)
    db.session.commit()
    print('✓ Student added: student@dev.com / student123 (roll: 1001)')

    print('\nTest credentials ready!')
