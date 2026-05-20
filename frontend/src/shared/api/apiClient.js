import axios from 'axios'

const API_BASE_URL = '/api/v1'

const TOKEN_KEY = 'token'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Gắn JWT token vào mọi request nếu đã đăng nhập
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY)

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)

// Xử lý khi token hết hạn hoặc không hợp lệ
(response) => response,
  (error) => {
    const status = error.response?.status
    const requestUrl = error.config?.url || ''
    const currentPath = window.location.pathname

    const isAuthMeRequest = requestUrl.endsWith('/auth/me')
    const isLoginPage = currentPath === '/login'

    const apiError =
      error.response?.data?.error ||
      error.response?.data?.detail ||
      null

    if (apiError?.message) {
      error.message = apiError.message
    }

    if (status === 401 && !isAuthMeRequest && !isLoginPage) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem('user')
      localStorage.removeItem('role')

      window.location.href = '/login'
    }

    return Promise.reject(error)
}


export default apiClient