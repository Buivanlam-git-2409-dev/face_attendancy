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
   - ... (đã xong)

### ✅ 2. Bổ sung backend tối thiểu để phục vụ SPA (DONE)
   - ... (đã xong)

### ✅ 3. Khởi tạo frontend React/Vite theo kiến trúc hiện tại (DONE)
   - ... (đã xong)

### ✅ 4. Triển khai Auth flow cho SPA (DONE)
   - ... (đã xong)

### ✅ 5. Triển khai Dashboard + Attendance list (read-only) (DONE)
   - ... (đã xong)

### ✅ 6. Hoàn thiện chất lượng UI và sửa lỗi (DONE)
   - ... (đã xong)

### 🔄 7. Ổn định Backend và chuẩn bị tích hợp AI (IN PROGRESS)
   - ✅ Sửa lỗi Circular Import và ModuleNotFound khi chạy backend độc lập
   - ✅ Cài đặt đầy đủ dependencies (dlib, face-recognition, v.v.)
   - 🔄 Tích hợp luồng Camera Stream (Nhận diện thực tế) vào Faculty Dashboard
   - 🔄 Hoàn thiện Celery worker cho các tác vụ nặng


## Lưu ý quan trọng
- Backend hiện đã ổn định và có thể chạy bằng lệnh: `$env:PYTHONPATH = "."; python backend/app.py` từ thư mục gốc.
- Các UI components mới nằm trong `frontend/src/shared/ui` rất dễ mở rộng.
- Cần chú ý file `.env` cho cả Backend (SECRET_KEY) và Frontend nếu có thay đổi port.


### 🔄 8. Redesign UI chuyên nghiệp theo hướng Landing-first + Education Tech (NEXT)
   - 🔄 Bổ sung flow mới: Landing Page trước, Login sau.
     - `/` → Landing Page giới thiệu hệ thống điểm danh bằng nhận diện khuôn mặt.
     - `/login` → Login Page với role selector Student / Faculty.
     - `/dashboard/student` → Student Dashboard.
     - `/dashboard/faculty` → Faculty Dashboard.
   - 🔄 Thiết kế lại giao diện theo phong cách:
     - Sạch, chuyên nghiệp, tạo cảm giác tin cậy.
     - Lấy cảm hứng hospitality ấm áp nhưng chuyển hóa sang education-tech.
     - Navy `#1A365D` làm màu chính.
     - Gold `#C5A059` làm điểm nhấn cao cấp.
     - Teal `#319795` cho trạng thái thành công / present.
     - Background off-white `#F7F6F2`.
     - Card glassmorphism, subtle gradients, hover border-gradient, backdrop-blur cho modal/sidebar.
   - 🔄 Không dùng Inter hoặc Roboto. Ưu tiên font:
     - `Plus Jakarta Sans`
     - `DM Sans`
     - `Space Grotesk`
   - 🔄 Bổ sung / nâng cấp component UI:
     - `GradientButton` có loading state.
     - `StatCard` có animated counter.
     - `AttendanceTable` có status badges.
     - `GlassPanel` dùng cho modal/sidebar/panel.
   - 🔄 Cần giữ API integration hiện tại:
     - Dùng `frontend/src/shared/api/apiClient.js`.
     - Không phá `authService.js`, `attendanceService.js`.
     - Vẫn xử lý loading/error/empty state.
     - Toast success/error nếu đã có thư viện toast, nếu chưa có thì thêm sau hoặc tạo component tạm.