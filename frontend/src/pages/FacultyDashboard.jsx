import React, { useEffect, useMemo, useState } from 'react'
import {
  DashboardLayout,
  Card,
  AttendanceTable,
  Alert,
  Button,
  Input,
} from '../shared/ui'
import CameraStream from '../features/attendance/CameraStream'
import { attendanceService } from '../shared/api/attendanceService'
import { studentService } from '../shared/api/studentService'
import './FacultyDashboard.css'

const emptyForm = {
  rollno: '',
  course: '',
  lecture_no: '',
}

export const FacultyDashboard = () => {
  const [students, setStudents] = useState([])
  const [attendances, setAttendances] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [editingRecord, setEditingRecord] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const loadDashboardData = async () => {
    setLoading(true)
    setError('')

    try {
      const [studentData, attendanceData] = await Promise.all([
        studentService.listStudents(),
        attendanceService.listAttendances(),
      ])

      setStudents(Array.isArray(studentData) ? studentData : studentData?.records || [])
      setAttendances(
        Array.isArray(attendanceData)
          ? attendanceData
          : attendanceData?.records || []
      )
    } catch (err) {
      setError(err.message || 'Unable to load faculty dashboard data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboardData()
  }, [])

  const stats = useMemo(() => {
    const totalStudents = students.length
    const totalAttendances = attendances.length

    const today = new Date().toISOString().slice(0, 10)
    const todayAttendance = attendances.filter((item) => {
      const date = item.markedDate || item.marked_date || item.date
      return String(date || '').startsWith(today)
    }).length

    return {
      totalStudents,
      totalAttendances,
      todayAttendance,
    }
  }, [students, attendances])

  const handleChange = (event) => {
    const { name, value } = event.target

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const resetForm = () => {
    setForm(emptyForm)
    setEditingRecord(null)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      if (!form.rollno || !form.course || form.lecture_no === '') {
        throw new Error('Please fill roll number, course and lecture number')
      }

      if (editingRecord) {
        const attendanceId =
          editingRecord.attendanceId ||
          editingRecord.attendance_id ||
          editingRecord.id

        await attendanceService.updateAttendance(attendanceId, form)
        setSuccess('Attendance updated successfully')
      } else {
        await attendanceService.createAttendance(form)
        setSuccess('Attendance created successfully')
      }

      resetForm()
      await loadDashboardData()
    } catch (err) {
      setError(err.message || 'Unable to save attendance')
    } finally {
      setSaving(false)
    }
  }

  const handleEdit = (record) => {
    setEditingRecord(record)
    setForm({
      rollno: record.rollno || record.rollNo || record.roll_no || '',
      course: record.course || record.courseName || '',
      lecture_no: record.lectureNo || record.lecture_no || '',
    })
    setSuccess('')
    setError('')
  }

  const handleDelete = async (record) => {
    const attendanceId =
      record.attendanceId ||
      record.attendance_id ||
      record.id

    if (!attendanceId) {
      setError('Attendance ID was not found')
      return
    }

    const confirmed = window.confirm('Delete this attendance record?')
    if (!confirmed) return

    setError('')
    setSuccess('')

    try {
      await attendanceService.deleteAttendance(attendanceId)
      setSuccess('Attendance deleted successfully')
      await loadDashboardData()
    } catch (err) {
      setError(err.message || 'Unable to delete attendance')
    }
  }

  return (
    <DashboardLayout>
      <div className="faculty-dashboard">
        <div className="header-actions">
          <div>
            <h1>Faculty Dashboard</h1>
            <p className="faculty-dashboard__subtitle">
              Manage students and attendance records
            </p>
          </div>

          <Button
            variant="outline"
            onClick={loadDashboardData}
            disabled={loading}
          >
            Refresh
          </Button>
        </div>

        {error && (
          <Alert variant="error">
            {error}
          </Alert>
        )}

        {success && (
          <Alert variant="success">
            {success}
          </Alert>
        )}

        <div className="stats-grid">
          <Card>
            <h3>Total Students</h3>
            <p>{stats.totalStudents}</p>
          </Card>

          <Card>
            <h3>Total Attendance</h3>
            <p>{stats.totalAttendances}</p>
          </Card>

          <Card className="gold">
            <h3>Today's Attendance</h3>
            <p>{stats.todayAttendance}</p>
          </Card>
        </div>

        <div className="dashboard-grid">
          <div className="camera-section">
            <h2>Live Recognition</h2>
            <CameraStream
              course={form.course}
              lectureNo={form.lecture_no}
              disabled={!form.course || form.lecture_no === ''}
              onRecognitionSuccess={loadDashboardData}
            />
          </div>

          <div className="attendance-table-section">
            <h2>{editingRecord ? 'Edit Attendance' : 'Create Attendance'}</h2>

            <form className="attendance-form" onSubmit={handleSubmit}>
              <Input
                label="Roll Number"
                name="rollno"
                type="number"
                value={form.rollno}
                onChange={handleChange}
                placeholder="12001"
                required
              />

              <Input
                label="Course"
                name="course"
                value={form.course}
                onChange={handleChange}
                placeholder="Computer Science"
                required
              />

              <Input
                label="Lecture Number"
                name="lecture_no"
                type="number"
                value={form.lecture_no}
                onChange={handleChange}
                placeholder="1"
                required
              />

              <div className="attendance-form__actions">
                <Button type="submit" loading={saving}>
                  {editingRecord ? 'Update Attendance' : 'Create Attendance'}
                </Button>

                {editingRecord && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={resetForm}
                    disabled={saving}
                  >
                    Cancel
                  </Button>
                )}
              </div>
            </form>
          </div>
        </div>

        <div className="attendance-table-section faculty-dashboard__table">
          <h2>Attendance Records</h2>

          <AttendanceTable
            data={attendances}
            loading={loading}
            columns={[
              'date',
              'rollno',
              'course',
              'lecture',
              'status',
              'time',
              'markedBy',
              'actions',
            ]}
            emptyMessage="No attendance records found"
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </div>
      </div>
    </DashboardLayout>
  )
}