# Kế hoạch triển khai giao diện mới (SPA) cho hệ thống điểm danh

## Bài toán & hiện trạng
- Toàn bộ giao diện cũ (`templates`, `static`) đã được xóa.
- Backend hiện có:
  - Flask monolith (`app.py`) vẫn giữ các route giao diện cũ (đang lỗi do thiếu template).
  - API versioned đã có ở `/api/v1/*` với response envelope chuẩn:
    - `{ "success": true, "data": ..., "error": null }`
  - Service layer và repository layer đã được tách một phần (auth, attendance, student, recognition jobs).
- Mục tiêu: dựng lại frontend từ đầu theo hướng **SPA React/Vite** và kết nối với backend hiện có.

## Phạm vi đã chốt (MVP)
- Frontend: **React + Vite** tách riêng, gửi API `/api/v1`.
- Ưu tiên chức năng: **Auth + dashboard + danh sách điểm danh (read-only)**.
- Chưa làm trong MVP:
  - Luồng tạo/sửa dữ liệu phức tạp (mark attendance thủ công, registration form đầy đủ, nhận diện realtime UI nâng cao).    
  - Refactor lớn kiến trúc backend sang FastAPI.

## Cách tiếp cận
1. Chuẩn hóa "hợp đồng API" cho SPA trước (session/cookie + quyền truy cập).
2. Dựng khung SPA, routing, state quản lý auth, API client dùng chung.
3. Làm màn hình theo chiều dọc (vertical slice): Login -> Dashboard -> Attendance list.
4. Ổn định trải nghiệm lỗi/loading/unauthorized theo envelope API hiện có.

## Danh sách công việc (execution plan)

### ✅ 1. Khảo sát API và chốt contract cho frontend (DONE)
   - Lập bảng endpoint sử dụng cho MVP: login, lấy dữ liệu dashboard, lấy danh sách attendance.
   - Chuẩn hóa mapping giữa `error.code` backend và thông báo UI.
   - Xác định rõ endpoint nào thiếu cho SPA (ví dụ: `auth/me`, `auth/logout`, attendance của student theo phiên đăng nhập).
   - **Output**: `.claude/api-contract-spa.md`

### ✅ 2. Bổ sung backend tối thiểu để phục vụ SPA (DONE)
   - ✅ Thêm endpoint API cho trạng thái phiên (`GET /api/v1/auth/me`)
   - ✅ Thêm logout JSON endpoint (`POST /api/v1/auth/logout`)
   - ✅ Bổ sung endpoint attendance phù hợp vai trò student (self-attendance)
   - ✅ Cấu hình CORS cho Flask app
   - ✅ Cài Flask-CORS package
   - **Changes**: `app.py`, `api/v1/auth_routes.py`, `api/v1/student_routes.py`, `requirements.txt`

### ✅ 3. Khởi tạo frontend React/Vite theo kiến trúc rõ ràng (DONE)
   - ✅ Tạo app mới với cấu trúc thư mục rõ ràng: `app`, `pages`, `features/auth`, `features/attendance`, `shared/api`, `shared/ui`.     
   - ✅ Thiết lập router (React Router v6)
   - ✅ HTTP client (Axios) với proxy dev
   - ✅ Env config (Vite)
   - ✅ Base layout và route guard
   - **Output**: `frontend/` folder

### ✅ 4. Triển khai Auth flow cho SPA (DONE)
   - ✅ Trang login với form (email, password, role selector)
   - ✅ Gửi `POST /api/v1/auth/login` và lưu session
   - ✅ AuthContext để manage state phía client
   - ✅ Xử lý redirect theo role (student/faculty)
   - ✅ Session restore trên page refresh (`GET /api/v1/auth/me`)
   - ✅ Logout button

### ✅ 5. Triển khai Dashboard + Attendance list (read-only) (DONE)
   - ✅ Dashboard Student: hiển thị stats card (courses + attendance count), attendance table
   - ✅ Dashboard Faculty: danh sách attendance của faculty đó, filter by course
   - ✅ Loading/empty/error states
   - ✅ Chuẩn hóa định dạng thời gian/ngày

### ✅ 6. Hoàn thiện chất lượng UI và sửa lỗi (DONE)
   - ✅ Thống nhất component primitives (Button, Input, Table, Alert, Badge, Card)
   - ✅ Responsive design cho desktop + tablet + mobile
   - ✅ Sửa lỗi vòng lặp request (Infinite loop 401) trong `apiClient.js`
   - ✅ Refactor toàn bộ Dashboard và Login trang sang hệ UI mới

### 🔄 7. Ổn định Backend và chuẩn bị tích hợp AI (IN PROGRESS)
   - ✅ Sửa lỗi Circular Import và ModuleNotFound khi chạy backend độc lập
   - ✅ Cài đặt đầy đủ dependencies (dlib, face-recognition, v.v.)
   - 🔄 Tích hợp luồng Camera Stream (Nhận diện thực tế) vào Faculty Dashboard
   - 🔄 Hoàn thiện Celery worker cho các tác vụ nặng

## Lưu ý quan trọng
- Backend hiện đã ổn định và có thể chạy bằng lệnh: `$env:PYTHONPATH = "."; python backend/app.py` từ thư mục gốc.
- Các UI components mới nằm trong `frontend/src/shared/ui` rất dễ mở rộng.
- Cần chú ý file `.env` cho cả Backend (SECRET_KEY) và Frontend nếu có thay đổi port.

## Tài liệu tham khảo
- **API Contract**: `.claude/api-contract-spa.md`
- **Frontend README**: `frontend/README.md`
- **Kiến trúc FE**: `frontend/src/` (shared/ui, context, pages)
