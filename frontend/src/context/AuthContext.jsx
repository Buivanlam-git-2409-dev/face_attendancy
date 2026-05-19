import React, { createContext, useState, useCallback, useEffect, useRef } from 'react'
import { authService } from '../shared/api/authService'

export const AuthContext = createContext()

const TOKEN_KEY = 'token'

const clearAuthStorage = () => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem('user')
  localStorage.removeItem('role')
}

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [role, setRole] = useState(null)
  const [loading, setLoading] = useState(true)
  const sessionCheckDone = useRef(false)

  useEffect(() => {
    if (sessionCheckDone.current) return

    const restoreSession = async () => {
      const token = localStorage.getItem(TOKEN_KEY)

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
          clearAuthStorage()
          setUser(null)
          setRole(null)
        }
      } catch (error) {
        clearAuthStorage()
        setUser(null)
        setRole(null)
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

      if (!result.success) {
        return {
          success: false,
          error: result.error?.message || 'Login failed',
        }
      }

      const { accessToken, user: userData, role: userRole } = result.data

      if (!accessToken) {
        return {
          success: false,
          error: 'Login succeeded but access token was not returned',
        }
      }

      localStorage.setItem(TOKEN_KEY, accessToken)
      setUser(userData)
      setRole(userRole)

      return {
        success: true,
        role: userRole,
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.error?.message ||
        error.response?.data?.message ||
        'Login failed'

      return {
        success: false,
        error: errorMessage,
      }
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      clearAuthStorage()
      setUser(null)
      setRole(null)
    }
  }, [])

  const value = {
    user,
    role,
    loading,
    isAuthenticated: Boolean(user),
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