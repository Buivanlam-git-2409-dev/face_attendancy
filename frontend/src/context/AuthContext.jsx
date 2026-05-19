import React, { createContext, useState, useCallback, useEffect, useRef } from 'react'
import { authService } from '../shared/api/authService'

export const AuthContext = createContext()

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [role, setRole] = useState(null)
  const [loading, setLoading] = useState(true)
  const sessionCheckDone = useRef(false)

  useEffect(() => {
    if (sessionCheckDone.current) return

    const restoreSession = async () => {
      const token = localStorage.getItem('token')
      if (!token) {
        setLoading(false)
        sessionCheckDone.current = true
        return
      }

      try {
        const result = await authService.getMe()
        if (result.success) {
          setUser(result.data.user)
          setRole(result.data.role)
        } else {
          localStorage.removeItem('token')
        }
      } catch (error) {
        // Not logged in or invalid token
        localStorage.removeItem('token')
      } finally {
        setLoading(false)
        sessionCheckDone.current = true
      }
    }

    restoreSession()
  }, [])

  const login = useCallback(async (email, password, roleParam = null) => {
    try {
      const result = await authService.login(email, password, roleParam)
      if (result.success) {
        const { accessToken, user: userData, role: userRole } = result.data
        localStorage.setItem('token', accessToken)
        setUser(userData)
        setRole(userRole)
        return { success: true, role: userRole }
      } else {
        return { success: false, error: result.error.message }
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error?.message || 'Login failed'
      return { success: false, error: errorMessage }
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      localStorage.removeItem('token')
      setUser(null)
      setRole(null)
    }
  }, [])

  const value = {
    user,
    role,
    loading,
    isAuthenticated: !!user,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export { AuthProvider }

export const useAuth = () => {
  const context = React.useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
