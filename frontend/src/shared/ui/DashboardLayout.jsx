import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Button } from './Button/Button'
import './DashboardLayout.css'

const Sidebar = ({ role }) => {
  const dashboardPath =
    role === 'faculty' ? '/dashboard/faculty' : '/dashboard/student'

  return (
    <aside className="dashboard-sidebar">
      <div className="sidebar-logo">UniAttendance</div>

      <nav>
        <ul>
          <li>
            <NavLink to={dashboardPath}>
              Dashboard
            </NavLink>
          </li>

          {role === 'faculty' && (
            <>
              <li>
                <NavLink to="/dashboard/faculty">
                  Attendance
                </NavLink>
              </li>
              <li>
                <NavLink to="/dashboard/faculty">
                  Students
                </NavLink>
              </li>
            </>
          )}

          {role === 'student' && (
            <li>
              <NavLink to="/dashboard/student">
                My Attendance
              </NavLink>
            </li>
          )}
        </ul>
      </nav>
    </aside>
  )
}

const Topbar = () => {
  const navigate = useNavigate()
  const { user, role, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <header className="dashboard-topbar">
      <div>
        <div className="dashboard-topbar__title">
          {role === 'faculty' ? 'Faculty Portal' : 'Student Portal'}
        </div>
        <div className="dashboard-topbar__subtitle">
          Attendance Management System
        </div>
      </div>

      <div className="dashboard-topbar__user">
        <div className="dashboard-topbar__user-info">
          <span className="dashboard-topbar__name">
            {user?.name || user?.email || 'User'}
          </span>
          <span className="dashboard-topbar__role">
            {role || 'guest'}
          </span>
        </div>

        <Button variant="outline" size="sm" onClick={handleLogout}>
          Logout
        </Button>
      </div>
    </header>
  )
}

export const DashboardLayout = ({ children }) => {
  const { role } = useAuth()

  return (
    <div className="dashboard-container">
      <Sidebar role={role} />

      <div className="main-content">
        <Topbar />
        <main className="content-inner">{children}</main>
      </div>
    </div>
  )
}