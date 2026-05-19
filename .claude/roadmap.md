# Facial Recognition Attendance Webapp - Modernization Roadmap

A project focused on automating school attendance using real-time facial recognition, currently transitioning from a legacy Flask architecture to a modern, scalable backend.

##  Project Overview
- **Purpose:** Automate attendance marking through AI-driven face recognition.
- **Current Stack:** Python 3.6+, Flask, SQLite (SQLAlchemy), `face_recognition` (dlib), OpenCV.
- **Architecture:** Monolithic, Synchronous, Session-based authentication.

---

## Backend Upgrade Plan (Modernization)

This plan outlines the steps to transform the current "outdated" codebase into a production-ready, asynchronous web application.

### Phase 1: Foundation & Infrastructure (High Priority)
- [x] **Switch to FastAPI:** Replace Flask with FastAPI for better performance and `async/await` support.
- [x] **Modern Configuration:** Use `python-dotenv` and `Pydantic Settings` to manage environment variables (DB URLs, Secret Keys).
- [x] **Security Hardening:** 
    - [x] Implement password hashing (e.g., `bcrypt` or `argon2`).
    - [x] Transition from Session Cookies to **JWT (JSON Web Tokens)** for stateless authentication.
- [x] **Database Migration:** 
    - [x] Prepare for PostgreSQL.
    - [x] Integrate **Alembic** for database schema migrations.

### Phase 1.5: RESTful API Design & Transition (Immediate)
- [x] **Define versioned API contract (`/api/v1`)** with consistent response envelope:
    - `{ "success": true, "data": {}, "error": null }`
- [x] **Introduce layered API modules** (`controller -> service -> repository -> model`) for new endpoints.
- [x] **Implement core REST resources first:**
    - [x] `POST /api/v1/auth/login`
    - [x] `GET /api/v1/students`
    - [x] `GET /api/v1/students/{rollno}`
    - [x] `POST /api/v1/students/register`
    - [x] `GET /api/v1/attendances`
    - [x] `POST /api/v1/attendances`
    - [x] `PUT /api/v1/attendances/{id}`
    - [x] `DELETE /api/v1/attendances/{id}`
    - [x] `GET /api/v1/faculty`
    - [x] `POST /api/v1/faculty`
    - [x] `GET /api/v1/faculty/{id}`
    - [x] `PUT /api/v1/faculty/{id}`
    - [x] `DELETE /api/v1/faculty/{id}`
- [x] **Keep legacy UI routes alive** while migrating business logic into services.
- [x] **Prepare FastAPI parity map** so each Flask API endpoint can be moved 1:1 to FastAPI routers.

### Phase 2: AI Processing & Scalability
- [x] **Background Workers:** Use **Celery + Redis** to handle CPU-intensive tasks like generating face encodings during registration.
    - [x] Celery integration path added for recognition jobs (`/api/v1/recognition/jobs`)
    - [x] Enabled by default in deployed environments and removed thread fallback
- [ ] **Vector Database:** Replace file-based loop search with a Vector DB (e.g., **Milvus**, **Pinecone**, or **ChromaDB**) for O(1) face matching.
- [ ] **WebSockets Implementation:** Move face recognition logic to a WebSocket stream to allow real-time processing without blocking the server.
- [ ] **AI Library Update:** Evaluate **MediaPipe** or **InsightFace** for faster, more accurate detection compared to dlib.

### Phase 3: Deployment & DevOps
- [ ] **Dockerization:** Create a `Dockerfile` and `docker-compose.yml` to bundle the app, database, and Redis.
- [x] **API Documentation:** Leverage FastAPI's automatic Swagger/OpenAPI docs for better frontend-backend integration.
- [ ] **Logging & Monitoring:** Implement structured logging (e.g., `structlog`) to track AI matching accuracy and system errors.

---

## 🛠 Current (Legacy) Architecture Reference

- `app.py`: Main Flask entry point (Synchronous routes).
- `models.py`: SQLAlchemy models (Student, Faculty, Attendance).
- `video_capture.py`: Threaded bufferless frame reader.
- `static/images/users/`: Local storage for face images (Current source of truth for AI).

##  Development Notes
- **Face matching logic:** Recognition loop is isolated in `services/face_recognition_service.py` and can be queued via `/api/v1/recognition/jobs` (Celery + Redis worker execution).
- **Database:** SQLite is used locally and now configurable via `DATABASE_URL` environment variable.
