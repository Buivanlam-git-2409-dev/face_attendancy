import React, { useEffect, useState } from 'react';
import { DashboardLayout } from '../shared/ui/DashboardLayout';
import { attendanceService } from '../shared/api/attendanceService';
import './StudentDashboard.css';

const StudentDashboard = () => {
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
          <div className="stat-card"><h3>Total Classes</h3><p>{totalClasses}</p></div>
          <div className="stat-card"><h3>Present</h3><p>{attended}</p></div>
          <div className="stat-card gold"><h3>Attendance Rate</h3><p>{percentage}%</p></div>
        </div>

        <div className="attendance-history">
          <h2>Attendance History</h2>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Course</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <tr key={index}>
                  <td>{item.date}</td>
                  <td>{item.course}</td>
                  <td>
                    <span className={`badge ${item.status.toLowerCase()}`}>
                      {item.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default StudentDashboard;
