import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { 
  Button, 
  Input, 
  Select, 
  Alert, 
  Card 
} from '../shared/ui'
import './LoginPage.css'

export const LoginPage = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('student')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await login(email, password, role)
    if (result.success) {
      if (result.role === 'student') {
        navigate('/student/dashboard')
      } else {
        navigate('/faculty/dashboard')
      }
    } else {
      setError(result.error || 'Login failed')
    }
    setLoading(false)
  }

  const roleOptions = [
    { value: 'student', label: 'Student' },
    { value: 'faculty', label: 'Faculty' }
  ]

  return (
    <div className="login-container">
      <div className="login-wrapper">
        <div className="login-brand">
          <h1>Attendance System</h1>
          <p>Automated school attendance with AI-driven facial recognition.</p>
        </div>
        
        <Card className="login-card">
          <form onSubmit={handleSubmit}>
            <h2 className="login-title">Sign In</h2>
            
            {error && <Alert variant="error" className="mb-4">{error}</Alert>}

            <Select 
              label="Select Role"
              id="role"
              value={role} 
              onChange={(e) => setRole(e.target.value)}
              options={roleOptions}
              disabled={loading}
            />

            <Input
              label="Email Address"
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@university.edu"
              required
              disabled={loading}
            />

            <Input
              label="Password"
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              disabled={loading}
            />

            <Button 
              type="submit" 
              className="w-full mt-4" 
              disabled={loading}
              size="lg"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>
        </Card>
        
        <footer className="login-footer">
          &copy; {new Date().getFullYear()} Attendance Management System
        </footer>
      </div>
    </div>
  )
}
