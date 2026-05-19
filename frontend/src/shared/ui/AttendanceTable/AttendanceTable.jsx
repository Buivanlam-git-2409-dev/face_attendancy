import React from 'react'
import './AttendanceTable.css'

const StatusBadge = ({ status }) => {
  const normalizedStatus = String(status || 'present').toLowerCase()

  const statusMap = {
    present: { label: 'Present', className: 'badge--present' },
    absent: { label: 'Absent', className: 'badge--absent' },
    late: { label: 'Late', className: 'badge--late' },
    pending: { label: 'Pending', className: 'badge--pending' },
  }

  const config = statusMap[normalizedStatus] || statusMap.present

  return <span className={`status-badge ${config.className}`}>{config.label}</span>
}

const formatDate = (value) => {
  if (!value) return '-'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return String(value)
  }

  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const formatTime = (value) => {
  if (!value) return '-'

  if (typeof value === 'string') {
    return value.substring(0, 8)
  }

  return String(value)
}

const getAttendanceId = (row) => {
  return row.attendanceId || row.attendance_id || row.id
}

export const AttendanceTable = ({
  data = [],
  loading = false,
  error = null,
  columns = ['date', 'rollno', 'course', 'lecture', 'status', 'time'],
  emptyMessage = 'No attendance records found',
  className = '',
  onEdit,
  onDelete,
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

  const showActions = columns.includes('actions') && (onEdit || onDelete)

  return (
    <div className={classes} {...props}>
      <table className="attendance-table__table">
        <thead>
          <tr>
            {columns.includes('date') && <th>Date</th>}
            {columns.includes('rollno') && <th>Roll No</th>}
            {columns.includes('student') && <th>Student</th>}
            {columns.includes('course') && <th>Course</th>}
            {columns.includes('lecture') && <th>Lecture</th>}
            {columns.includes('status') && <th>Status</th>}
            {columns.includes('time') && <th>Time</th>}
            {columns.includes('markedBy') && <th>Marked By</th>}
            {showActions && <th>Actions</th>}
          </tr>
        </thead>

        <tbody>
          {data.map((row, idx) => {
            const id = getAttendanceId(row)

            const date =
              row.markedDate ||
              row.marked_date ||
              row.date ||
              row.attendanceDate

            const time =
              row.markedTime ||
              row.marked_time ||
              row.time ||
              row.checkInTime

            const rollno =
              row.rollno ||
              row.rollNo ||
              row.roll_no ||
              row.studentRollNo ||
              '-'

            const studentName =
              row.studentName ||
              row.student_name ||
              row.name ||
              '-'

            const course =
              row.course ||
              row.courseName ||
              '-'

            const lecture =
              row.lectureNo ||
              row.lecture_no ||
              row.lecture ||
              '-'

            const markedBy =
              row.markedBy ||
              row.marked_by ||
              '-'

            const status =
              row.status ||
              row.attendanceStatus ||
              'present'

            return (
              <tr key={id || idx}>
                {columns.includes('date') && <td>{formatDate(date)}</td>}
                {columns.includes('rollno') && <td>{rollno}</td>}
                {columns.includes('student') && <td>{studentName}</td>}
                {columns.includes('course') && <td>{course}</td>}
                {columns.includes('lecture') && <td>{lecture}</td>}
                {columns.includes('status') && (
                  <td>
                    <StatusBadge status={status} />
                  </td>
                )}
                {columns.includes('time') && <td>{formatTime(time)}</td>}
                {columns.includes('markedBy') && <td>{markedBy}</td>}

                {showActions && (
                  <td>
                    <div className="attendance-table__actions">
                      {onEdit && (
                        <button
                          type="button"
                          className="attendance-table__action-btn"
                          onClick={() => onEdit(row)}
                        >
                          Edit
                        </button>
                      )}

                      {onDelete && (
                        <button
                          type="button"
                          className="attendance-table__action-btn attendance-table__action-btn--danger"
                          onClick={() => onDelete(row)}
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  </td>
                )}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}