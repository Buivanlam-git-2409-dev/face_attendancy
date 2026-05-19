import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { isAuthenticated, role, loading } = useAuth()

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />
  }

  if (requiredRole && role !== requiredRole) {
    return <Navigate to="/" />
  }

  return children
}
