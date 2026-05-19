# Frontend (React + Vite) - Getting Started

## Setup

```bash
cd frontend
npm install  # Already done
npm run dev
```

The app will start on **http://localhost:5173** and proxy API calls to backend at **http://localhost:5000/api/v1**.

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── context/           # Auth state management (AuthContext)
│   ├── features/
│   │   ├── auth/         # Auth-related features
│   │   └── attendance/   # Attendance features
│   ├── pages/            # Page components (Login, Dashboards)
│   ├── shared/
│   │   ├── api/          # API client and services (authService, attendanceService)
│   │   └── ui/           # Shared UI components (ProtectedRoute)
│   ├── App.jsx           # Main app with routing
│   ├── main.jsx          # React entry point
│   └── App.css           # Global styles
├── package.json
├── vite.config.js        # Vite config with API proxy
└── index.html            # HTML template
```

## Features (MVP)

### ✅ Login Page
- Form with email, password, and role selector (Student/Faculty)
- Calls `POST /api/v1/auth/login`
- Role-based redirect to dashboard
- Error handling

### ✅ Student Dashboard
- View personal attendance records
- Stats card showing lectures per course
- Attendance table with date/time
- Logout button

### ✅ Faculty Dashboard
- View all attendance records (filtered by logged-in faculty)
- Course filter dropdown
- Attendance table with roll numbers
- Logout button

### ✅ Auth Context
- Persists login state across page refreshes via `GET /api/v1/auth/me`
- Session expiry handling (auto redirect to login on 401)
- Protected routes

## Development

### Start both backend and frontend:

**Terminal 1 - Backend:**
```bash
cd ..
python app.py
# Runs on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
# Auto-proxies /api calls to backend
```

### Build for production:

```bash
npm run build
# Creates optimized build in `dist/`
```

## Next Steps (Not in MVP)

- Manual attendance marking with face recognition UI
- Student registration form
- Faculty registration form (admin only)
- Faculty management pages
- More advanced filtering/reporting
- Export to CSV
- Real-time recognition job status
