# 🚀 Testing Guide - Frontend MVP

## Quick Start

### 1. Backend (Flask API Server)
```bash
cd C:\Users\fptsh\Downloads\facial-recognition-attendance-webapp-master
.\venv\Scripts\activate  # Or just: venv\Scripts\activate.ps1
python app.py
```
✅ Backend runs on: **http://localhost:5000**

### 2. Frontend (React Dev Server)
```bash
cd frontend
npm run dev
```
✅ Frontend runs on: **http://localhost:5175** (or next available port 5173+)

---

## Test Credentials

### Student Account
- Email: `student@dev.com`
- Password: `student123`
- Role: Student
- Roll No: 1001
- Name: John Student

### Faculty Account
- Email: `faculty@dev.com`
- Password: `faculty123`
- Role: Faculty
- Course: CS101
- Name: Dr. Smith

---

## Testing Workflow

### 1. Login Page
```
URL: http://localhost:5175/login
```
- ✅ Select role (Student/Faculty)
- ✅ Enter email and password
- ✅ Click "Login"
- ✅ Should redirect to dashboard

### 2. Student Dashboard
```
URL: http://localhost:5175/student/dashboard
- Shows personal attendance records
- Stats card: Courses and lecture count
- Attendance table with full details (Date, Time, Course, etc.)
- Logout button in navbar
```

### 3. Faculty Dashboard
```
URL: http://localhost:5175/faculty/dashboard
- Shows all attendance records marked by this faculty
- Filter by course dropdown
- Admin badge if applicable
- Attendance table
- Logout button in navbar
```

### 4. Session Persistence
- Login once
- Refresh page (F5 or Cmd+R)
- Dashboard should restore without re-login ✅ (uses GET /api/v1/auth/me)

### 5. Logout & Redirect
- Click "Logout" button
- Should be redirected to login page
- Manual refresh to /student/dashboard should redirect back to login ✅

---

## API Endpoints (Backend)

All endpoints respond with:
```json
{
  "success": true/false,
  "data": {...},
  "error": null / { "code": "ERROR_CODE", "message": "..." }
}
```

### Auth
- **POST /api/v1/auth/login** - Student/Faculty login
- **GET /api/v1/auth/me** - Get current session user
- **POST /api/v1/auth/logout** - Clear session

### Attendance (Student)
- **GET /api/v1/me/attendances** - Get own attendance records

### Attendance (Faculty)
- **GET /api/v1/attendances** - Get all attendance (with filters)
  - Query params: `rollno`, `lecture_no`, `course`, `marked_by`

---

## Troubleshooting

### Issue: "API Connection Failed" or Network Error

**Solution 1: Ensure both servers are running**
```bash
# Check backend
curl http://localhost:5000/api/v1/auth/me

# Check frontend
curl http://localhost:5175
```

**Solution 2: Check proxy config**
- Frontend proxy is set in `frontend/vite.config.js`
- It forwards `/api/*` to `http://localhost:5000`
- Ensure ports don't conflict

### Issue: 401 Unauthorized on first load

**Expected behavior** - Frontend checks `GET /api/v1/auth/me` on app load. If no session, returns 401.
- ✅ This is correct - should redirect to login page
- If stuck on loading screen, check browser console for network errors

### Issue: Login fails with "Invalid Credentials"

**Check test data exists:**
```bash
cd ..
python -c "from models import Student; from extensions import db; from app import app; 
with app.app_context(): 
  s = Student.query.filter_by(email='student@dev.com').first()
  print('Found:', s.email if s else 'Not found')"
```

**If not found, add test data:**
```bash
python add_test_data.py
```

### Issue: Session not persisting after page refresh

**Check cookies are enabled** in browser. Flask sessions use HTTP-only cookies.

---

## Browser Console

Open DevTools (F12) and check:

1. **Network tab** - Should see API requests to `/api/v1/...`
2. **Console tab** - Check for JS errors
3. **Application > Cookies** - Should have `session` cookie from Flask

---

## Add More Test Data

**To add attendance records:**
```python
from app import db, app
from models import Attendance
from datetime import date, time, datetime

with app.app_context():
    att = Attendance(
        rollno=1001,
        course='CS101',
        lecture_no=1,
        marked_by='Dr. Smith',
        marked_date=date.today(),
        marked_time=datetime.now().time(),
    )
    db.session.add(att)
    db.session.commit()
    print("Attendance added!")
```

---

## Next Steps

- ✅ Frontend MVP complete (Auth + Dashboard + Read-only Attendance)
- ⏳ Manual attendance marking UI (not in scope for MVP)
- ⏳ Face recognition integration (not in scope for MVP)
- ⏳ Student/Faculty registration forms (not in scope for MVP)

---

## Log Files

- Frontend errors: Check browser console (F12)
- Backend errors: Check terminal running `python app.py`
- No file-based logs configured yet (can add later if needed)
