import React, { useEffect, useState } from 'react';
import { DashboardLayout, Card, AttendanceTable } from '../shared/ui';
import { attendanceService } from '../shared/api/attendanceService';
import './StudentDashboard.css';

export const StudentDashboard = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAttendance = async () => {
      try {
        const response = await attendanceService.getMyAttendances();
        setData(response);
      } catch (error) {
        console.error("Error fetching attendance", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAttendance();
  }, []);

  const totalClasses = data.length;
  const attended = data.filter(a => a.status === 'Present').length;
  const percentage = totalClasses ? Math.round((attended / totalClasses) * 100) : 0;

  return (
    <DashboardLayout>
      <div className="student-dashboard">
        <h1>My Attendance Overview</h1>

        <div className="stats-grid">
          <Card><h3>Total Classes</h3><p>{totalClasses}</p></Card>
          <Card><h3>Present</h3><p>{attended}</p></Card>
          <Card className="gold"><h3>Attendance Rate</h3><p>{percentage}%</p></Card>
        </div>

        <div className="attendance-history">
          <h2>Attendance History</h2>
          <AttendanceTable 
            data={data} 
            loading={loading}
            columns={['date', 'course', 'status']}
          />
        </div>
      </div>
    </DashboardLayout>
  );
};
