import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { attendanceService } from '../shared/api/attendanceService'
import { 
  Button, 
  Badge, 
  Card, 
  Select, 
  Alert 
} from '../shared/ui'
import './Dashboard.css'

export const FacultyDashboard = () => {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [attendances, setAttendances] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filterCourse, setFilterCourse] = useState('')

  useEffect(() => {
    const fetchAttendances = async () => {
      try {
        const filters = {}
        if (filterCourse) filters.course = filterCourse
        if (user?.name) filters.marked_by = user.name
        
        const result = await attendanceService.listAttendances(filters)
        if (result.success) {
          setAttendances(result.data)
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

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const uniqueCourses = [...new Set(attendances.map(a => a.course))]
  const courseOptions = [
    { value: '', label: 'All Courses' },
    ...uniqueCourses.map(course => ({ value: course, label: course }))
  ]

  return (
    <div className="dashboard">
      <header className="navbar">
        <div className="navbar-brand">Attendance System</div>
        <div className="navbar-user">
          <span className="user-name">Welcome, <strong>{user?.name}</strong></span>
          {user?.isAdmin && <Badge variant="info">Admin</Badge>}
          <Button variant="ghost" size="sm" onClick={handleLogout}>
            Logout
          </Button>
        </div>
      </header>

      <main className="dashboard-container">
        <div className="dashboard-header">
          <h1>Faculty Dashboard</h1>
          <Button variant="primary">
            Start Recognition
          </Button>
        </div>

        {error && <Alert variant="error" title="Error">{error}</Alert>}

        <div className="dashboard-grid">
          <aside className="filters-sidebar">
            <Card title="Filters">
              <Select
                label="Course"
                value={filterCourse}
                onChange={e => setFilterCourse(e.target.value)}
                options={courseOptions}
              />
            </Card>
          </aside>

          <section className="content-area">
            <Card title="Attendance Records">
              {loading ? (
                <div className="loading">Loading attendances...</div>
              ) : attendances.length === 0 ? (
                <p className="empty-message">No attendance records found.</p>
              ) : (
                <div className="table-responsive">
                  <table className="attendance-table">
                    <thead>
                      <tr>
                        <th>Roll No.</th>
                        <th>Course</th>
                        <th>Lecture</th>
                        <th>Date</th>
                        <th>Time</th>
                      </tr>
                    </thead>
                    <tbody>
                      {attendances.map(att => (
                        <tr key={att.attendanceId}>
                          <td><strong>{att.rollno}</strong></td>
                          <td>{att.course}</td>
                          <td>{att.lectureNo}</td>
                          <td>{new Date(att.markedDate).toLocaleDateString()}</td>
                          <td>{att.markedTime}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </section>
        </div>
      </main>
    </div>
  )
}
