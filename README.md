# Facial Recognition Attendance System

A modern web-based facial recognition attendance system for schools and universities.

The project uses a **FastAPI backend** with a **React + Vite frontend**. The legacy Flask UI is still preserved only for compatibility and is mounted under `/legacy`, but it is **not the main application flow**.

---

## Current Main Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Backend Server | Uvicorn |
| Frontend | React 18 + Vite |
| API Client | Axios |
| Database | SQLite by default, PostgreSQL supported |
| Background Jobs | Celery + Redis |
| Legacy Compatibility | Flask mounted under `/legacy` only |

---

## Main Application Flow

```txt
Frontend SPA
http://localhost:5173
        |
        | /api/*
        v
FastAPI Backend
http://localhost:8000
        |
        v
Database
SQLite or PostgreSQL
```

Legacy Flask routes are available only at:

```txt
http://localhost:8000/legacy
```

Do not use Flask port `5000` as the main development flow.

---

## Features

- Role-based login for Student and Faculty.
- Student dashboard.
- Faculty dashboard.
- Attendance records.
- Versioned REST API under `/api/v1`.
- FastAPI OpenAPI documentation.
- PostgreSQL support.
- Celery + Redis support for recognition jobs.
- Legacy Flask routes preserved under `/legacy`.

---

## Project Structure

```txt
face_attendancy/
├── backend/
│   ├── api/
│   │   └── v1/
│   ├── db/
│   ├── migrations/
│   ├── repositories/
│   ├── services/
│   ├── tasks/
│   ├── app.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   ├── celery_app.py
│   ├── celery_worker.py
│   ├── docker-compose.yml
│   └── .env.example
│
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── requirements.txt
├── README.md
├── STATUS.md
└── TESTING.md
```

---

## Prerequisites

Install these before running the project:

- Python 3.10+
- Node.js 18+
- npm
- Docker Desktop, optional but recommended for PostgreSQL and Redis

---

## 1. Backend Setup

Run commands from the project root.

### Create virtual environment

```bash
python -m venv venv
```

### Activate virtual environment

Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

Windows CMD:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## 2. Backend Environment Configuration

Create a `.env` file inside the `backend/` folder:

```bash
copy backend\.env.example backend\.env
```

For local SQLite development, you can keep the default configuration.

For PostgreSQL, use:

```env
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/attendance_db
SECRET_KEY=your-super-secret-key-change-this
CELERY_ENABLED=true
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

---

## 3. Run Database

### Option A: SQLite

SQLite is the simplest local option. No separate database server is required.

The backend will create the database tables during startup.

### Option B: PostgreSQL with Docker

From the project root:

```bash
cd backend
docker compose up -d postgres
```

PostgreSQL will run on:

```txt
localhost:5432
```

Default credentials:

```txt
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=attendance_db
```

Useful commands:

```bash
docker compose ps
docker compose logs postgres
docker compose down
```

---

## 4. Run Redis for Celery

If Celery is enabled, start Redis:

```bash
docker run --name attendance_redis -p 6379:6379 -d redis:7
```

Check Redis container:

```bash
docker ps
```

Stop Redis:

```bash
docker stop attendance_redis
```

Start it again:

```bash
docker start attendance_redis
```

---

## 5. Run Backend

Run from the project root:

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

Backend URLs:

```txt
API Root:      http://localhost:8000
Health Check:  http://localhost:8000/health
Swagger Docs:  http://localhost:8000/docs
OpenAPI JSON:  http://localhost:8000/openapi.json
Legacy UI:     http://localhost:8000/legacy
```

Important:

```txt
FastAPI on port 8000 is the main backend.
Flask port 5000 is legacy and should not be used as the main flow.
```

---

## 6. Run Celery Worker

Open another terminal from the project root:

```bash
celery -A backend.celery_worker.celeryApp worker --loglevel=info --pool=solo
```

Use this when testing recognition jobs or background processing.

---

## 7. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
```

Run Vite:

```bash
npm run dev
```

Frontend runs at:

```txt
http://localhost:5173
```

The Vite dev server proxies API requests:

```txt
/api/* -> http://127.0.0.1:8000
```

---

## 8. Recommended Development Startup Order

Use 3 or 4 terminals:

### Terminal 1: Database

```bash
cd backend
docker compose up -d postgres
```

### Terminal 2: Redis

```bash
docker run --name attendance_redis -p 6379:6379 -d redis:7
```

Skip this if Redis is already running.

### Terminal 3: Backend

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 4: Frontend

```bash
cd frontend
npm run dev
```

Then open:

```txt
http://localhost:5173
```

---

## REST API

Main API prefix:

```txt
/api/v1
```

Common endpoints:

```txt
POST   /api/v1/auth/login
POST   /api/v1/auth/token
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me
POST   /api/v1/auth/logout

GET    /api/v1/students
GET    /api/v1/students/{rollno}
POST   /api/v1/students/register

GET    /api/v1/faculty
POST   /api/v1/faculty
GET    /api/v1/faculty/{id}
PUT    /api/v1/faculty/{id}
DELETE /api/v1/faculty/{id}

GET    /api/v1/attendances
POST   /api/v1/attendances
PUT    /api/v1/attendances/{id}
DELETE /api/v1/attendances/{id}

POST   /api/v1/recognition/jobs
GET    /api/v1/recognition/jobs/{job_id}
```

API documentation is available at:

```txt
http://localhost:8000/docs
```

---

## Legacy Flask Notes

This project originally used Flask templates and Flask routes.

Current status:

- FastAPI is the primary backend.
- Flask is kept only as a compatibility bridge.
- Legacy Flask routes are mounted under `/legacy`.
- Legacy template UI should not be treated as the main application.
- New frontend work should target the React/Vite SPA.
- New API work should target FastAPI routers under `/api/v1`.

Use:

```txt
http://localhost:8000/legacy
```

only when you intentionally need to check old Flask behavior.

---

## Troubleshooting

### Backend does not start

Check that your virtual environment is active:

```bash
.\venv\Scripts\Activate.ps1
```

Then reinstall dependencies:

```bash
pip install -r requirements.txt
```

### Frontend cannot call API

Confirm backend is running:

```bash
curl http://localhost:8000/health
```

Confirm frontend is running:

```bash
curl http://localhost:5173
```

Check that `frontend/vite.config.js` proxies `/api` to:

```txt
http://127.0.0.1:8000
```

### PostgreSQL connection fails

Check container:

```bash
cd backend
docker compose ps
```

Check logs:

```bash
docker compose logs postgres
```

Confirm `.env` contains:

```env
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/attendance_db
```

### Celery job does not run

Check Redis:

```bash
docker ps
```

Check Celery worker terminal.

Make sure `.env` contains:

```env
CELERY_ENABLED=true
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

---

## Development Rules

- Do not use Flask port `5000` as the main backend.
- Do not duplicate Axios setup in the frontend.
- Keep frontend API calls through the shared API client.
- Keep backend business logic out of route handlers.
- Prefer service and repository layers for backend logic.
- Keep legacy Flask behavior isolated under `/legacy`.
