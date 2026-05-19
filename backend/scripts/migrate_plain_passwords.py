from flask import Flask

from backend.config import Config
from backend.extensions import db
from backend.models import Student, Faculty
from backend.security import hash_password


def is_bcrypt_hash(value: str) -> bool:
    return isinstance(value, str) and value.startswith("$2")


def create_migration_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


app = create_migration_app()

with app.app_context():
    updated = 0

    for student in Student.query.all():
        if student.password and not is_bcrypt_hash(student.password):
            student.password = hash_password(student.password)
            updated += 1

    for faculty in Faculty.query.all():
        if faculty.password and not is_bcrypt_hash(faculty.password):
            faculty.password = hash_password(faculty.password)
            updated += 1

    db.session.commit()

    print(f"Migrated {updated} passwords to bcrypt.")