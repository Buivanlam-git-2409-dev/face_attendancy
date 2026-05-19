import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { attendanceService } from '../shared/api/attendanceService'
import { 
  Button, 
  Card, 
  Alert 
} from '../shared/ui'
import './Dashboard.css'

export const StudentDashboard = () => {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [attendances, setAttendances] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchAttendances = async () => {
      try {
        const result = await attendanceService.getMyAttendances()
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
  }, [])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const uniqueCourses = [...new Set(attendances.map(a => a.course))]
  const courseStats = uniqueCourses.map(course => {
    const courseAttendances = attendances.filter(a => a.course === course)
    return {
      course,
      count: courseAttendances.length,
    }
  })

  return (
    <div className="dashboard">
      <header className="navbar">
        <div className="navbar-brand">Attendance System</div>
        <div className="navbar-user">
          <span className="user-name">Welcome, <strong>{user?.name || user?.rollno}</strong></span>
          <Button variant="ghost" size="sm" onClick={handleLogout}>
            Logout
          </Button>
        </div>
      </header>

      <main className="dashboard-container">
        <div className="dashboard-header">
          <h1>Student Dashboard</h1>
        </div>

        {error && <Alert variant="error" title="Error">{error}</Alert>}

        {loading ? (
          <div className="loading">Loading dashboard...</div>
        ) : (
          <div className="dashboard-content">
            <h2 style={{ marginBottom: '1rem' }}>Your Attendance Overview</h2>
            <div className="stats-grid" style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', 
              gap: '1.5rem',
              marginBottom: '2.5rem'
            }}>
              {courseStats.map(stat => (
                <Card key={stat.course}>
                  <div style={{ textAlign: 'center' }}>
                    <h3 style={{ color: '#6b7280', fontSize: '0.875rem', textTransform: 'uppercase', marginBottom: '0.5rem' }}>{stat.course}</h3>
                    <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#3b82f6' }}>{stat.count}</div>
                    <p style={{ color: '#9ca3af', fontSize: '0.875rem' }}>Lectures Attended</p>
                  </div>
                </Card>
              ))}
              {courseStats.length === 0 && (
                <Card>
                  <div style={{ textAlign: 'center', color: '#9ca3af' }}>No course data available</div>
                </Card>
              )}
            </div>

            <Card title="Attendance History">
              {attendances.length === 0 ? (
                <p className="empty-message">No attendance records found.</p>
              ) : (
                <div className="table-responsive">
                  <table className="attendance-table">
                    <thead>
                      <tr>
                        <th>Course</th>
                        <th>Lecture</th>
                        <th>Marked By</th>
                        <th>Date</th>
                        <th>Time</th>
                      </tr>
                    </thead>
                    <tbody>
                      {attendances.map(att => (
                        <tr key={att.attendanceId}>
                          <td><strong>{att.course}</strong></td>
                          <td>{att.lectureNo}</td>
                          <td>{att.markedBy}</td>
                          <td>{new Date(att.markedDate).toLocaleDateString()}</td>
                          <td>{att.markedTime}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </div>
        )}
      </main>
    </div>
  )
}
