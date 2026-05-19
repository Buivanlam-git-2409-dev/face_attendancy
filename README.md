# Facial Recognition Attendance System using Flask Web framework
A simple web-based facial recognition attendance system to be used for schools. This application is powered by a pre-trained deep learning facial recognition
model which was used to mark the attendance of students based on live real-time video.

### Features:
* Real-time face recognition attendance marking
* Seperate Panels for each role to manage the attendance
* Downloadable Records

### Technology Stack:
* Python 3.6+
* Face-Recognition
* Bootstrap 4
* Javascript

### Environment configuration
1. Copy `.env.example` to `.env`
2. Set `SECRET_KEY` to a strong random value
3. Optionally override `DATABASE_URL` (default: `sqlite:///db/database.db`)
4. To use distributed recognition jobs, set `CELERY_ENABLED=true` and run Redis + Celery worker

### REST API (v1)
- `POST /api/v1/auth/login`
- `GET /api/v1/students`
- `GET /api/v1/students/{rollNo}`
- `GET /api/v1/students/{rollNo}/attendances`
- `GET /api/v1/attendances`
- `POST /api/v1/attendances`
- `POST /api/v1/recognition/attendance/run` (queue background recognition job)
- `POST /api/v1/recognition/jobs`
- `GET /api/v1/recognition/jobs/{jobId}`
