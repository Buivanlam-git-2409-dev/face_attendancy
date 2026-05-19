# Facial Recognition Attendance System

A modern web-based facial recognition attendance system for schools, featuring real-time attendance marking via live video.

### Features
* Real-time face recognition attendance marking.
* Role-based dashboard (Admin, Faculty, Student).
* Downloadable attendance records.

### Technology Stack
* **Backend:** Python (Flask/FastAPI)
* **Frontend:** React, Vite, Axios
* **Database:** SQLite (default) or PostgreSQL

---

### Cấu hình Dự án

#### 1. Backend
1. **Tạo môi trường ảo (Virtual Environment):**
   ```bash
   cd backend
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```
2. **Cài đặt thư viện:**
   ```bash
   pip install -r ..\requirements.txt
   ```
#### 3. Cấu hình PostgreSQL (Tùy chọn - Dùng Docker)
Nếu bạn muốn sử dụng PostgreSQL thay vì SQLite, hãy làm theo các bước sau:

1. **Chạy container PostgreSQL:**
   ```bash
   docker run --name attendance_postgres -e POSTGRES_PASSWORD=mypassword -e POSTGRES_USER=postgres -e POSTGRES_DB=attendance_db -p 5432:5432 -d postgres:17
   ```
2. **Kiểm tra trạng thái:**
   ```bash
   docker ps
   ```
3. **Kết nối database:**
   ```bash
   docker exec -it attendance_postgres psql -U postgres -d attendance_db
   ```
4. **Cấu hình trong `.env`:**
   Cập nhật `DATABASE_URL` trong file `.env`:
   ```text
   DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/attendance_db
   ```

**Các lệnh quản lý:**
- Dừng: `docker stop attendance_postgres`
- Khởi động lại: `docker start attendance_postgres`
- Xem log: `docker logs attendance_postgres`


#### 2. Frontend
1. **Cài đặt dependencies:**
   ```bash
   cd frontend
   npm install
   ```
2. **Chạy môi trường phát triển:**
   ```bash
   npm run dev
   ```
   Ứng dụng sẽ chạy tại `http://localhost:5173`.

---

### REST API (v1)
- `POST /api/v1/auth/login`
- `GET /api/v1/students`
- `POST /api/v1/recognition/attendance/run` (queue background job)
