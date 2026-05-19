import apiClient from './apiClient'

export const attendanceService = {
  async getMyAttendances() {
    const response = await apiClient.get('/me/attendances')
    return response.data
  },

  async getStudentAttendances(rollNo) {
    const response = await apiClient.get(`/students/${rollNo}/attendances`)
    return response.data
  },

  async listAttendances(filters = {}) {
    const params = new URLSearchParams()
    if (filters.rollno) params.append('rollno', filters.rollno)
    if (filters.lecture_no) params.append('lecture_no', filters.lecture_no)
    if (filters.course) params.append('course', filters.course)
    if (filters.marked_by) params.append('marked_by', filters.marked_by)
    
    const response = await apiClient.get(`/attendances?${params}`)
    return response.data
  },
}
