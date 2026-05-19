import React from 'react';
import './DashboardLayout.css';

const Sidebar = () => (
  <aside className="dashboard-sidebar">
    <div className="sidebar-logo">UniAttendance</div>
    <nav>
      <ul>
        <li><a href="/dashboard">Dashboard</a></li>
        <li><a href="/attendance">Attendance</a></li>
        <li><a href="/profile">Profile</a></li>
      </ul>
    </nav>
  </aside>
);

const Topbar = () => (
  <header className="dashboard-topbar">
    <div className="search-placeholder">Search...</div>
    <div className="user-profile">Hello, User</div>
  </header>
);

export const DashboardLayout = ({ children }) => (
  <div className="dashboard-container">
    <Sidebar />
    <div className="main-content">
      <Topbar />
      <main className="content-inner">{children}</main>
    </div>
  </div>
);
