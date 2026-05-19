from flask import Flask
from backend.config import Config
from backend.extensions import db
from backend.models import Faculty
from backend.security import hash_password

# Initialize a temporary Flask app to provide database context
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def add_admin():
    with app.app_context():
        # Check if admin already exists to prevent duplicate entries
        existing = Faculty.query.filter_by(email='admin@dev.com').first()
        if existing:
            print("Admin already exists!")
            return

        admin = Faculty(
            name='Admin',
            email='admin@dev.com',
            password=hash_password('admin123'),
            is_admin=True,
            course='Management'
        )

        try:
            db.session.add(admin)
            db.session.commit()
            print('Admin added successfully!')
            print('Email: admin@dev.com')
            print('Password: admin123')
        except Exception as e:
            db.session.rollback()
            print(f"Error adding admin: {e}")

if __name__ == '__main__':
    add_admin()
