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

### ✅ 3. Khởi tạo frontend React/Vite theo kiến trúc hiện tại (DONE)
   - ✅ Tạo app mới với cấu trúc thực tế hiện tại:
     - `frontend/src/context/AuthContext.jsx`
     - `frontend/src/features/auth/`
     - `frontend/src/features/attendance/`
     - `frontend/src/pages/`
     - `frontend/src/shared/api/`
     - `frontend/src/shared/ui/`
     - `frontend/src/App.jsx`, `frontend/src/App.css`, `frontend/src/main.jsx`
   - ✅ Thiết lập router bằng React Router v6 trong `App.jsx` / các route liên quan.
   - ✅ HTTP client dùng chung bằng Axios tại `frontend/src/shared/api/apiClient.js`.
   - ✅ Service API đã tách theo domain:
     - `frontend/src/shared/api/authService.js`
     - `frontend/src/shared/api/attendanceService.js`
   - ✅ Base layout, route guard và auth state:
     - `frontend/src/context/AuthContext.jsx`
     - `frontend/src/shared/ui/ProtectedRoute.jsx`
   - **Output**: `frontend/` folder

   > Ghi chú đồng bộ: Plan ban đầu có nhắc thư mục `src/app`, nhưng cấu trúc thực tế trong dự án hiện đang dùng trực tiếp `App.jsx`, `App.css`, `main.jsx` ở `src/`. Vì vậy file plan được cập nhật theo cấu trúc thực tế trong ảnh thay vì bắt buộc tạo thêm `src/app`.

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

#### Prompt sử dụng skill để redesign giao diện

```txt
ACTIVATE frontend-design skill.

I need to redesign my Facial Recognition Attendance Dashboard frontend based on the current project structure and roadmap.

IMPORTANT: Sync with the existing structure shown below. Do not create a new unrelated architecture unless necessary.

CURRENT FRONTEND STRUCTURE:
frontend/
  src/
    context/
      AuthContext.jsx
    features/
      attendance/
      auth/
    pages/
    shared/
      api/
        apiClient.js
        attendanceService.js
        authService.js
      ui/
        Alert/
        Badge/
        Button/
        Card/
        Input/
        Select/
        index.js
        Modal.css
        Modal.jsx
        ProtectedRoute.jsx
        theme.css
    App.css
    App.jsx
    main.jsx

PROJECT TECH:
- React 18 + Vite
- Tailwind CSS already configured
- React Router v6
- Axios for API calls
- Existing apiClient must be imported from: frontend/src/shared/api/apiClient.js
- Existing services: authService.js, attendanceService.js

MAIN GOAL:
Create a professional, modern, trustworthy education-tech UI for a school/university Facial Recognition Attendance System.
The app flow must be Landing-first, then Login, then Dashboard.

ROUTES / PAGES NEEDED:

1. Landing Page (/)
   - Public entry point before login
   - Hero section introducing Facial Recognition Attendance for schools/universities
   - Strong headline, short supporting text, modern CTA area
   - CTA buttons: Login, View Demo, Learn More
   - Feature cards:
     + Face Recognition Attendance
     + Real-time Faculty Monitoring
     + Student Attendance History
     + Secure Role-based Access
   - Trust section for schools/universities
   - Smooth scroll / fade-up animations
   - Use premium education-tech visual style

2. Login Page (/login)
   - Role selector: Student / Faculty
   - Email + password fields
   - Clean centered card
   - Subtle animation when the card appears
   - Redirect after login based on role:
     + student -> /dashboard/student
     + faculty -> /dashboard/faculty

3. Student Dashboard (/dashboard/student)
   - Welcome header with avatar
   - Stats cards:
     + Total Attendance %
     + Courses Enrolled
     + Days Present
   - Recent Attendance Table: date, course, status, time
   - Minimal and scannable
   - Loading, empty and error states

4. Faculty Dashboard (/dashboard/faculty)
   - Course selector dropdown
   - Today's attendance summary
   - Student attendance table with search/filter
   - Start Recognition button for real-time camera flow
   - Loading, empty and error states

STYLE DIRECTION:
- Clean, professional, trusted feel
- Hospitality warmth adapted for education
- Navy blue + gold accents similar to an elegant hotel/academy brand
- More modern tech elements:
  + subtle gradients
  + glassmorphism cards
  + soft shadows
  + smooth animations
  + premium hover states

STYLE CONSTRAINTS:
- Do NOT use Inter or Roboto
- Use one of these fonts:
  + Plus Jakarta Sans
  + DM Sans
  + Space Grotesk
- Primary Navy: #1A365D
- Secondary Gold: #C5A059
- Accent Teal: #319795
- Background Off-white: #F7F6F2
- Use backdrop-blur for modals / sidebars / glass panels
- Add subtle border gradients on hover
- Add staggered fade-up animations for cards
- Keep layout responsive for desktop, tablet and mobile

COMPONENTS TO CREATE OR UPGRADE INSIDE shared/ui:
1. GradientButton
   - loading state
   - disabled state
   - icon support if needed
   - navy/gold gradient variant

2. StatCard
   - animated counter
   - label, value, helper text
   - optional icon
   - fade-up animation

3. AttendanceTable
   - reusable table for student/faculty attendance data
   - status badges: Present, Absent, Late, Pending
   - responsive behavior
   - loading/empty/error states

4. GlassPanel
   - reusable glassmorphism wrapper
   - backdrop-blur
   - subtle border
   - suitable for modals, sidebars and cards

API INTEGRATION RULES:
- Use existing apiClient from frontend/src/shared/api/apiClient.js
- Do not duplicate Axios setup
- Do not break AuthContext
- Keep login connected to authService.js
- Keep attendance data connected to attendanceService.js
- Handle loading and error states properly
- Show toast notifications for success/error if toast system exists; otherwise create a simple reusable alert/toast component

IMPLEMENTATION ORDER:
1. First update theme.css / global styling tokens if needed
2. Create/upgrade shared UI components
3. Create LandingPage.jsx
4. Update App.jsx routes so / renders LandingPage
5. Then redesign Login Page
6. Then redesign Student Dashboard
7. Then redesign Faculty Dashboard

START by generating the Landing Page component first, because the desired flow is Landing Page -> Login -> Dashboard.
```
