import axios from 'axios'

const API_BASE_URL = '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.response.use(
  response => response,
  error => {
    const isAuthMeRequest = error.config?.url?.endsWith('/auth/me')
    const isLoginPage = window.location.pathname === '/login'

    if (error.response?.status === 401 && !isAuthMeRequest && !isLoginPage) {
      // Session expired - redirect to login
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
