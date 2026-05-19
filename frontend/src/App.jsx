import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute } from './shared/ui/ProtectedRoute'
import { LoginPage } from './pages/LoginPage'
import { StudentDashboard } from './pages/StudentDashboard'
import { FacultyDashboard } from './pages/FacultyDashboard'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route
            path="/student/dashboard"
            element={
              <ProtectedRoute requiredRole="student">
                <StudentDashboard />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/faculty/dashboard"
            element={
              <ProtectedRoute requiredRole="faculty">
                <FacultyDashboard />
              </ProtectedRoute>
            }
          />

          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
