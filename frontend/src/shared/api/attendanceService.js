import apiClient from './apiClient'

const unwrap = (response) => {
  const body = response.data

  if (body && typeof body === 'object' && 'success' in body) {
    if (!body.success) {
      const message =
        body.error?.message ||
        body.detail?.message ||
        body.message ||
        'Request failed'

      throw new Error(message)
    }

    return body.data
  }

  return body
}

export const attendanceService = {
  async getMyAttendances() {
    const response = await apiClient.get('/me/attendances')
    return unwrap(response)
  },

  async getStudentAttendances(rollNo) {
    const response = await apiClient.get(`/students/${rollNo}/attendances`)
    return unwrap(response)
  },

  async listAttendances(filters = {}) {
    const params = new URLSearchParams()

    if (filters.rollno) params.append('rollno', filters.rollno)
    if (filters.lecture_no) params.append('lecture_no', filters.lecture_no)
    if (filters.course) params.append('course', filters.course)
    if (filters.marked_by) params.append('marked_by', filters.marked_by)

    const queryString = params.toString()
    const url = queryString ? `/attendances?${queryString}` : '/attendances'

    const response = await apiClient.get(url)
    return unwrap(response)
  },

  async createAttendance(payload) {
    const response = await apiClient.post('/attendances', {
      rollno: Number(payload.rollno),
      course: payload.course,
      lecture_no: Number(payload.lecture_no),
    })

    return unwrap(response)
  },

  async updateAttendance(attendanceId, payload) {
    const body = {}

    if (payload.rollno !== undefined && payload.rollno !== '') {
      body.rollno = Number(payload.rollno)
    }

    if (payload.course !== undefined) {
      body.course = payload.course
    }

    if (payload.lecture_no !== undefined && payload.lecture_no !== '') {
      body.lecture_no = Number(payload.lecture_no)
    }

    const response = await apiClient.put(`/attendances/${attendanceId}`, body)
    return unwrap(response)
  },

  async deleteAttendance(attendanceId) {
    const response = await apiClient.delete(`/attendances/${attendanceId}`)
    return unwrap(response)
  },
}