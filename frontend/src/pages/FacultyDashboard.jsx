import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { attendanceService } from '../shared/api/attendanceService'
import { GradientButton } from '../shared/ui/GradientButton/GradientButton'
import { GlassPanel } from '../shared/ui/GlassPanel/GlassPanel'
import { StatCard } from '../shared/ui/StatCard/StatCard'
import { AttendanceTable } from '../shared/ui/AttendanceTable/AttendanceTable'
import { Badge, Select, Alert } from '../shared/ui'
import { CameraStream } from '../features/attendance/CameraStream'
import './Dashboard.css'

export const FacultyDashboard = () => {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [attendances, setAttendances] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filterCourse, setFilterCourse] = useState('')
  const [showCamera, setShowCamera] = useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  useEffect(() => {
    const fetchAttendances = async () => {
      try {
        const filters = {}
        if (filterCourse) filters.course = filterCourse
        if (user?.name) filters.marked_by = user.name

        const result = await attendanceService.listAttendances(filters)
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
  }, [filterCourse, user])

  const uniqueCourses = [...new Set(attendances.map(a => a.course))]
  const courseOptions = [
    { value: '', label: 'All Courses' },
    ...uniqueCourses.map(course => ({ value: course, label: course })),
  ]

  const todayAttendances = attendances.filter(a => {
    const attendanceDate = new Date(a.markedDate)
    const today = new Date()
    return (
      attendanceDate.toDateString() === today.toDateString()
    )
  })

  const tableData = attendances.map(att => ({
    date: att.markedDate || att.attendanceDate,
    course: att.course,
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
              👤 {user?.name || 'Faculty'}
            </span>
            {user?.isAdmin && <Badge variant="info">Admin</Badge>}
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
              Welcome back, <span className="user-highlight">{user?.name}</span>
            </h2>
            <p className="welcome-subtitle">Manage your class attendance and monitor student check-ins</p>
          </section>

          {/* Error Alert */}
          {error && (
            <Alert variant="error" className="dashboard-error">
              {error}
            </Alert>
          )}

          {/* Today's Summary */}
          {!loading && (
            <section className="stats-section">
              <div className="stats-grid">
                <StatCard
                  icon={() => <span style={{ fontSize: '24px' }}>👥</span>}
                  label="Today's Check-ins"
                  value={todayAttendances.length}
                  description="Students checked in today"
                  animated
                  delay={0}
                />
                <StatCard
                  icon={() => <span style={{ fontSize: '24px' }}>📚</span>}
                  label="Active Courses"
                  value={uniqueCourses.length}
                  description="Courses with records"
                  animated
                  delay={100}
                />
                <StatCard
                  icon={() => <span style={{ fontSize: '24px' }}>📊</span>}
                  label="Total Records"
                  value={attendances.length}
                  description="All attendance records"
                  animated
                  delay={200}
                />
              </div>
            </section>
          )}

          {/* Camera and Filters Section */}
          <div className="faculty-grid">
            {/* Filters Sidebar */}
            <aside className="faculty-sidebar">
              <GlassPanel animated delay={300}>
                <h3 className="sidebar-title">Filters</h3>

                <div className="form-group">
                  <label htmlFor="course-filter" className="form-label">
                    Course
                  </label>
                  <Select
                    id="course-filter"
                    value={filterCourse}
                    onChange={e => setFilterCourse(e.target.value)}
                    options={courseOptions}
                  />
                </div>

                <GradientButton
                  variant="navy-teal"
                  className="w-full"
                  onClick={() => setShowCamera(!showCamera)}
                >
                  {showCamera ? '✓ Camera Active' : 'Start Camera'}
                </GradientButton>
              </GlassPanel>
            </aside>

            {/* Main Content Area */}
            <section className="faculty-content">
              {/* Camera Stream Section */}
              {showCamera && (
                <GlassPanel className="camera-panel" animated delay={300}>
                  <div className="camera-header">
                    <h3 className="camera-title">Live Attendance Recognition</h3>
                    <button
                      className="camera-close"
                      onClick={() => setShowCamera(false)}
                      aria-label="Close camera"
                    >
                      ✕
                    </button>
                  </div>
                  <CameraStream />
                </GlassPanel>
              )}

              {/* Attendance Records Table */}
              <GlassPanel animated delay={!showCamera ? 300 : 0}>
                <div className="section-header">
                  <h3 className="section-title">Attendance Records</h3>
                  <p className="section-subtitle">
                    {filterCourse ? `Course: ${filterCourse}` : 'All courses'}
                  </p>
                </div>

                <AttendanceTable
                  data={tableData}
                  loading={loading}
                  error={error}
                  columns={['date', 'course', 'status', 'time']}
                  emptyMessage="No attendance records found"
                />
              </GlassPanel>
            </section>
          </div>
        </div>
      </main>
    </div>
  )
}

