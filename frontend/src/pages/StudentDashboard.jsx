import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { attendanceService } from '../shared/api/attendanceService'
import { GradientButton } from '../shared/ui/GradientButton/GradientButton'
import { GlassPanel } from '../shared/ui/GlassPanel/GlassPanel'
import { StatCard } from '../shared/ui/StatCard/StatCard'
import { AttendanceTable } from '../shared/ui/AttendanceTable/AttendanceTable'
import { Alert } from '../shared/ui'
import './Dashboard.css'

export const StudentDashboard = () => {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [attendances, setAttendances] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  useEffect(() => {
    const fetchAttendances = async () => {
      try {
        const result = await attendanceService.getMyAttendances()
        if (result.success) {
          setAttendances(result.data || [])
        } else {
          setError(result.error?.message || 'Failed to load attendances')
        }
      } catch (err) {
        setError('Network error')
      } finally {
        setLoading(false)
      }
    }

    fetchAttendances()
  }, [])

  const calculateStats = () => {
    if (!attendances || attendances.length === 0) {
      return {
        totalAttendance: 0,
        coursesEnrolled: 0,
        daysPresent: 0,
      }
    }

    const courses = [...new Set(attendances.map(a => a.course || a.courseName))]
    const uniqueDates = [...new Set(attendances.map(a => a.markedDate || a.attendanceDate))]

    return {
      totalAttendance: attendances.length > 0 ? Math.round((attendances.length / (courses.length * 15)) * 100) : 0,
      coursesEnrolled: courses.length,
      daysPresent: uniqueDates.length,
    }
  }

  const stats = calculateStats()

  const tableData = attendances.map(att => ({
    date: att.markedDate || att.attendanceDate,
    course: att.course || att.courseName,
    status: 'present',
    time: att.markedTime || att.checkInTime,
  }))

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="dashboard-header-content">
          <div className="header-brand">
            <span className="brand-icon">📚</span>
            <h1 className="brand-name">AttendanceAI</h1>
          </div>

          <div className="header-actions">
            <span className="header-user">
              👤 {user?.name || user?.rollno || 'User'}
            </span>
            <GradientButton
              variant="secondary"
              size="sm"
              onClick={handleLogout}
              className="logout-btn"
            >
              Logout
            </GradientButton>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="dashboard-main">
        <div className="dashboard-container">
          {/* Welcome Section */}
          <section className="welcome-section fade-up-in">
            <h2 className="welcome-title">
              Welcome back, <span className="user-highlight">{user?.name || user?.rollno}</span>
            </h2>
            <p className="welcome-subtitle">Here's your attendance overview</p>
          </section>

          {/* Error Alert */}
          {error && (
            <Alert variant="error" className="dashboard-error">
              {error}
            </Alert>
          )}

          {/* Loading State */}
          {loading ? (
            <div className="loading-state">
              <div className="loader-spinner" />
              <p>Loading your attendance records...</p>
            </div>
          ) : (
            <>
              {/* Stats Cards */}
              <section className="stats-section">
                <div className="stats-grid">
                  <StatCard
                    icon={() => <span style={{ fontSize: '24px' }}>📊</span>}
                    label="Attendance Rate"
                    value={stats.totalAttendance}
                    suffix="%"
                    description="Overall attendance percentage"
                    animated
                    delay={0}
                  />
                  <StatCard
                    icon={() => <span style={{ fontSize: '24px' }}>📚</span>}
                    label="Courses Enrolled"
                    value={stats.coursesEnrolled}
                    description="Active courses this semester"
                    animated
                    delay={100}
                  />
                  <StatCard
                    icon={() => <span style={{ fontSize: '24px' }}>✓</span>}
                    label="Days Present"
                    value={stats.daysPresent}
                    description="Total attendance days recorded"
                    animated
                    delay={200}
                  />
                </div>
              </section>

              {/* Recent Attendance Table */}
              <section className="attendance-section">
                <GlassPanel animated>
                  <div className="section-header">
                    <h3 className="section-title">Recent Attendance</h3>
                    <p className="section-subtitle">Your latest check-in records</p>
                  </div>

                  <AttendanceTable
                    data={tableData}
                    loading={loading}
                    error={error}
                    columns={['date', 'course', 'status', 'time']}
                    emptyMessage="No attendance records found yet"
                  />
                </GlassPanel>
              </section>
            </>
          )}
        </div>
      </main>
    </div>
  )
}

