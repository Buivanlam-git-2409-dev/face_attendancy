import apiClient from './apiClient'

export const authService = {
  async login(email, password, role = null) {
    const response = await apiClient.post('/auth/login', {
      email,
      password,
      role,
    })
    return response.data
  },

  async getMe() {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  async logout() {
    const response = await apiClient.post('/auth/logout')
    return response.data
  },
}
