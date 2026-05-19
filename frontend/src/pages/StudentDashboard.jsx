import React, { useEffect, useMemo, useState } from 'react'
import { DashboardLayout, Card, AttendanceTable, Alert } from '../shared/ui'
import { attendanceService } from '../shared/api/attendanceService'
import './StudentDashboard.css'

export const StudentDashboard = () => {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchAttendance = async () => {
    setLoading(true)
    setError('')

    try {
      const data = await attendanceService.getMyAttendances()
      const normalizedData = Array.isArray(data) ? data : data?.records || []
      setRecords(normalizedData)
    } catch (err) {
      setError(err.message || 'Unable to load attendance records')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAttendance()
  }, [])

  const stats = useMemo(() => {
    const totalClasses = records.length
    const attended = records.filter((item) => {
      const status = String(item.status || item.attendanceStatus || 'present').toLowerCase()
      return status === 'present'
    }).length

    const percentage = totalClasses
      ? Math.round((attended / totalClasses) * 100)
      : 0

    return {
      totalClasses,
      attended,
      percentage,
    }
  }, [records])

  return (
    <DashboardLayout>
      <div className="student-dashboard">
        <h1>My Attendance Overview</h1>

        {error && (
          <Alert variant="error">
            {error}
          </Alert>
        )}

        <div className="stats-grid">
          <Card>
            <h3>Total Classes</h3>
            <p>{stats.totalClasses}</p>
          </Card>

          <Card>
            <h3>Present</h3>
            <p>{stats.attended}</p>
          </Card>

          <Card className="gold">
            <h3>Attendance Rate</h3>
            <p>{stats.percentage}%</p>
          </Card>
        </div>

        <div className="attendance-history">
          <div className="student-dashboard__section-header">
            <h2>Attendance History</h2>
            <button
              type="button"
              className="student-dashboard__refresh"
              onClick={fetchAttendance}
              disabled={loading}
            >
              Refresh
            </button>
          </div>

          <AttendanceTable
            data={records}
            loading={loading}
            error={error}
            columns={['date', 'course', 'lecture', 'status', 'time', 'markedBy']}
            emptyMessage="No attendance records found"
          />
        </div>
      </div>
    </DashboardLayout>
  )
}