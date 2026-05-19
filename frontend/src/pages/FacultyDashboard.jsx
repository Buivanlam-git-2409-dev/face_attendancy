import React from 'react';
import { DashboardLayout, Card, AttendanceTable } from '../shared/ui';
import CameraStream from '../features/attendance/CameraStream';
import './FacultyDashboard.css';

export const FacultyDashboard = () => {
  // Mock data for now, would typically come from an API hook
  const recentAttendance = [
    { studentName: 'Nguyen Van A', courseName: 'Data Science', checkInTime: '09:15 AM', attendanceStatus: 'present' }
  ];

  return (
    <DashboardLayout>
      <div className="faculty-dashboard">
        <div className="header-actions">
          <h1>Faculty Dashboard</h1>
          <button className="btn-primary">+ Start New Session</button>
        </div>

        <div className="stats-grid">
          <Card><h3>Total Students</h3><p>240</p></Card>
          <Card><h3>Total Sessions</h3><p>48</p></Card>
          <Card className="gold"><h3>Today's Attendance</h3><p>94%</p></Card>
        </div>

        <div className="dashboard-grid">
          <div className="camera-section">
            <h2>Live Recognition</h2>
            <CameraStream />
          </div>

          <div className="attendance-table-section">
            <h2>Recent Attendance</h2>
            <AttendanceTable 
              data={recentAttendance} 
              columns={['course', 'status', 'time']} 
            />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};
