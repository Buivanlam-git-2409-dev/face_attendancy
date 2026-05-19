import time
import os
from datetime import datetime

from flask import Flask, request, render_template, redirect, url_for, flash, session, Response
from functools import wraps

import cv2
from flask_cors import CORS
from backend.api import apiBlueprint
from config import Config
from backend.extensions import db
from backend.services.auth_service import AuthService
from backend.services.face_recognition_service import FaceRecognitionService

app = Flask(__name__)

app.config.from_object(Config)

if not app.config.get('SECRET_KEY'):
    raise RuntimeError('SECRET_KEY is not configured. Set it in environment variables or .env file.')

CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://localhost:3000"])

db.init_app(app)
# Import models here as to avoid circular import issue
from models import *

with app.app_context():
    db.create_all()

app.register_blueprint(apiBlueprint)

@app.route('/')
def index():
    return {'message': 'Attendance API - Use frontend SPA'}, 200

@app.route('/health')
def health():
    return {'status': 'ok'}, 200

# Legacy routes below - DISABLED (use API instead)
# All UI is now handled by React frontend on separate port
# Keep for reference but don't use - will fail because templates folder was deleted

"""
@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    ...

@app.route('/login_faculty', methods=['GET', 'POST'])
def login_faculty():
    ...

@app.route('/student')
def student():
    ...

[all other legacy routes commented out]
"""

if __name__ == '__main__':
    app.run(debug=True)
