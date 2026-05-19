import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { GradientButton } from '../shared/ui/GradientButton/GradientButton'
import { GlassPanel } from '../shared/ui/GlassPanel/GlassPanel'
import { Input, Select, Alert } from '../shared/ui'
import './LoginPage.css'

export const LoginPage = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()

  const queryParams = new URLSearchParams(location.search)
  const initialRole = queryParams.get('role') || 'student'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState(initialRole)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const newRole = queryParams.get('role')
    if (newRole && (newRole === 'student' || newRole === 'faculty')) {
      setRole(newRole)
    }
  }, [location.search])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await login(email, password, role)
    if (result.success) {
      if (result.role === 'student') {
        navigate('/dashboard/student')
      } else {
        navigate('/dashboard/faculty')
      }
    } else {
      setError(result.error || 'Login failed')
    }
    setLoading(false)
  }

  const roleOptions = [
    { value: 'student', label: 'Student' },
    { value: 'faculty', label: 'Faculty' },
  ]

  return (
    <div className="login-container">
      <div className="login-background" />

      <div className="login-wrapper">
        <Link to="/" className="login-back">
          ← Back
        </Link>

        <GlassPanel className="login-card" elevated animated>
          <div className="login-brand">
            <span className="login-logo">📚</span>
            <h1>AttendanceAI</h1>
            <p>Secure. Fast. Reliable.</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            <h2 className="login-title">Welcome Back</h2>

            {error && (
              <Alert variant="error" className="login-error">
                {error}
              </Alert>
            )}

            <div className="form-group">
              <label htmlFor="role" className="form-label">
                I am a
              </label>
              <Select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                options={roleOptions}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email Address
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@university.edu"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                disabled={loading}
              />
            </div>

            <GradientButton
              type="submit"
              variant="navy-gold"
              size="lg"
              loading={loading}
              className="login-button"
            >
              Sign In
            </GradientButton>
          </form>

          <p className="login-footer">
            Don't have an account?{' '}
            <a href="#signup" className="login-link">
              Contact your institution
            </a>
          </p>
        </GlassPanel>

        <p className="login-copyright">
          © {new Date().getFullYear()} AttendanceAI. All rights reserved.
        </p>
      </div>
    </div>
  )
}

