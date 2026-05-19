import React from 'react';
import { DashboardLayout } from '../shared/ui/DashboardLayout';
import CameraStream from '../features/attendance/CameraStream';
import './FacultyDashboard.css';

const FacultyDashboard = () => {
  return (
    <DashboardLayout>
      <div className="faculty-dashboard">
        <div className="header-actions">
          <h1>Faculty Dashboard</h1>
          <button className="btn-primary">+ Start New Session</button>
        </div>
        
        <div className="stats-grid">
          <div className="stat-card"><h3>Total Students</h3><p>240</p></div>
          <div className="stat-card"><h3>Total Sessions</h3><p>48</p></div>
          <div className="stat-card gold"><h3>Today's Attendance</h3><p>94%</p></div>
        </div>

        <div className="dashboard-grid">
          <div className="camera-section">
            <h2>Live Recognition</h2>
            <CameraStream />
          </div>

          <div className="attendance-table-section">
            <h2>Recent Attendance</h2>
            <table>
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Course</th>
                  <th>Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Nguyen Van A</td>
                  <td>Data Science</td>
                  <td>09:15 AM</td>
                  <td><span className="badge present">Present</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default FacultyDashboard;
