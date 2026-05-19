name: attendance-analytics
description: Create interactive charts and analytics for attendance data
---

# Attendance Analytics Skill

## Chart Components

### Daily Attendance Trend
```javascript
// Chart.js configuration
const ctx = document.getElementById('attendanceTrend');
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
    datasets: [{
      label: 'Present',
      data: [45, 48, 42, 47, 44],
      borderColor: '#10B981',
      tension: 0.4
    }, {
      label: 'Late',
      data: [5, 3, 7, 4, 6],
      borderColor: '#F59E0B'
    }]
  }
});
```
### Real-time Counter

``` html
<div class="live-counter" hx-get="/api/attendance/count" hx-trigger="every 5s">
  Present: <span id="presentCount">0</span> / Total: <span id="totalCount">50</span>
</div>
```

### Export Features
CSV export with date range picker

PDF report generation

Email summary to facul