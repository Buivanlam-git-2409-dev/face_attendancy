import React from 'react'
import './AttendanceTable.css'

const StatusBadge = ({ status }) => {
  const statusMap = {
    present: { label: 'Present', className: 'badge--present' },
    absent: { label: 'Absent', className: 'badge--absent' },
    late: { label: 'Late', className: 'badge--late' },
    pending: { label: 'Pending', className: 'badge--pending' },
  }

  const config = statusMap[status?.toLowerCase()] || statusMap.present
  return <span className={`status-badge ${config.className}`}>{config.label}</span>
}

export const AttendanceTable = ({
  data = [],
  loading = false,
  error = null,
  columns = ['date', 'course', 'status', 'time'],
  emptyMessage = 'No attendance records found',
  className = '',
  ...props
}) => {
  const classes = ['attendance-table', className].filter(Boolean).join(' ')

  if (loading) {
    return (
      <div className={`${classes} attendance-table--loading`}>
        <div className="table-loader">
          <div className="loader-spinner" />
          <p>Loading attendance records...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`${classes} attendance-table--error`}>
        <div className="table-error">
          <p className="error-title">Unable to load records</p>
          <p className="error-message">{error}</p>
        </div>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className={`${classes} attendance-table--empty`}>
        <div className="table-empty">
          <p>{emptyMessage}</p>
        </div>
      </div>
    )
  }

  const formatDate = (date) => {
    if (!date) return '-'
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const formatTime = (time) => {
    if (!time) return '-'
    if (typeof time === 'string' && time.includes(':')) {
      return time.substring(0, 5)
    }
    return '-'
  }

  return (
    <div className={classes} {...props}>
      <table className="attendance-table__table">
        <thead>
          <tr>
            {columns.includes('date') && <th>Date</th>}
            {columns.includes('course') && <th>Course</th>}
            {columns.includes('status') && <th>Status</th>}
            {columns.includes('time') && <th>Time</th>}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              {columns.includes('date') && (
                <td>{formatDate(row.date || row.attendanceDate)}</td>
              )}
              {columns.includes('course') && (
                <td>{row.course || row.courseName || '-'}</td>
              )}
              {columns.includes('status') && (
                <td>
                  <StatusBadge status={row.status || row.attendanceStatus} />
                </td>
              )}
              {columns.includes('time') && (
                <td>{formatTime(row.time || row.checkInTime)}</td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
