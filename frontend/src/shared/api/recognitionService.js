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

export const recognitionService = {
  async verifyFrame({ file, course, lecture_no }) {
    const formData = new FormData()

    formData.append('file', file)

    if (course) {
      formData.append('course', course)
    }

    if (lecture_no !== undefined && lecture_no !== null && lecture_no !== '') {
      formData.append('lecture_no', String(lecture_no))
    }

    const response = await apiClient.post('/recognition/verify', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return unwrap(response)
  },
  async studentCheckIn({ file, course, lecture_no }) {
    const formData = new FormData()

    formData.append('file', file)
    formData.append('course', course)
    formData.append('lecture_no', String(lecture_no))

    const response = await apiClient.post('/me/recognition/check-in', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return unwrap(response)
  },

  async runAttendanceJob(payload = {}) {
    const response = await apiClient.post('/recognition/attendance/run', payload)
    return unwrap(response)
  },
}