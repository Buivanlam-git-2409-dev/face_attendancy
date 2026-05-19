---
name: web-ui-designer
description: Design production-grade web interfaces for facial recognition attendance system
based_on: bencium-controlled-ux-designer, bencium-impact-designer
---

# Web UI Designer for Attendance System

## Design System Rules

### 1. Layout Structure
- Use responsive grid system (mobile-first)
- Sidebar navigation for dashboard
- Card-based design for attendance records
- Real-time status indicators

### 2. Color Palette (WCAG 2.1 AA compliant)
```css
Primary: #3B82F6 (Blue - Trust/Action)
Secondary: #10B981 (Green - Success/Absent?)
Danger: #EF4444 (Red - Error/Alert)
Warning: #F59E0B (Amber)
Background: #F9FAFB
Surface: #FFFFFF
Text Primary: #111827
Text Secondary: #6B7280

### 3. Typography
Headings: Inter, 6-step modular scale

Body: system-ui, 1rem base, 1.5 line-height

Use proper quotes, dashes, spacing

### 4. Components Needed
1. Camera Stream Component:
- Real-time video feed (640x480)
- Face detection overlay (green bounding box)
- Confidence score display
- Manual capture button

2. Attendance Table:
- Search/filter by date, student name
- Pagination (20 items/page)
- Export to CSV/PDF
- Status badges (Present/Late/Absent)
- Student Management:

3. Card grid or table view
- Register new student (upload photo)
- Edit/delete student info
- Face encoding status indicator

4. Dashboard:
- Today's attendance summary (cards)
- Real-time counter (Present/Total)
- Chart.js integration (weekly/monthly trends)
- Recent activity feed

### 5. Accessibility Requirements
ARIA labels on all interactive elements

Keyboard navigation support

Focus indicators (2px ring)

Color contrast ≥ 4.5:1

6.  Tech Stack
Frontend: HTML5, TailwindCSS, Alpine.js or React

Camera: WebRTC (getUserMedia)

Charts: Chart.js or ApexCharts

Icons: Heroicons or Lucide