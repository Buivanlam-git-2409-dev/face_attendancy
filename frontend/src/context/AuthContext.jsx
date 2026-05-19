import React, { createContext, useState, useCallback, useEffect, useRef } from 'react'
import { authService } from '../shared/api/authService'

export const AuthContext = createContext()

const AuthProviderComponent = ({ children }) => {
  const [user, setUser] = useState(null)
  const [role, setRole] = useState(null)
  const [loading, setLoading] = useState(true)
  const sessionCheckDone = useRef(false)

  useEffect(() => {
    if (sessionCheckDone.current) return

    const restoreSession = async () => {
      try {
        const result = await authService.getMe()
        if (result.success) {
          setUser(result.data.user)
          setRole(result.data.role)
        }
      } catch (error) {
        // Not logged in, ignore
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
        setUser(result.data.user)
        setRole(result.data.role)
        return { success: true, role: result.data.role }
      } else {
        return { success: false, error: result.error.message }
      }
    } catch (error) {
      return { success: false, error: 'Login failed' }
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await authService.logout()
      setUser(null)
      setRole(null)
    } catch (error) {
      console.error('Logout failed:', error)
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

export const AuthProvider = AuthProviderComponent

export const useAuth = () => {
  const context = React.useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
