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

export const studentService = {
  async listStudents(filters = {}) {
    const params = new URLSearchParams()

    if (filters.search) params.append('search', filters.search)
    if (filters.semester) params.append('semester', filters.semester)

    const queryString = params.toString()
    const url = queryString ? `/students?${queryString}` : '/students'

    const response = await apiClient.get(url)
    return unwrap(response)
  },

  async getStudent(rollNo) {
    const response = await apiClient.get(`/students/${rollNo}`)
    return unwrap(response)
  },

  async registerStudent(payload) {
    const response = await apiClient.post('/students/register', {
      rollno: Number(payload.rollno),
      name: payload.name,
      email: payload.email,
      password: payload.password,
      semester: payload.semester,
      pic_path: payload.pic_path || '',
    })

    return unwrap(response)
  },
  async uploadStudentFace(rollNo, file) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post(
      `/students/${rollNo}/face`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return unwrap(response)
  },
}