import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Card } from '../shared/ui';
import './HomeDashboard.css';

const HomeDashboard = () => {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Facial Recognition Attendance System</h1>
          <p className="hero-description">
            Automated attendance marking using AI-powered face recognition. 
            Experience seamless, secure, and efficient attendance tracking.
          </p>
          <div className="hero-cta">
            <Button 
              size="lg" 
              className="cta-button primary"
              onClick={() => navigate('/login?role=student')}
            >
              Student Login
            </Button>
            <Button 
              size="lg" 
              variant="secondary"
              className="cta-button secondary"
              onClick={() => navigate('/login?role=faculty')}
            >
              Faculty Login
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <h2>Key Features</h2>
        </div>
        <div className="features-grid">
          <Card className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>Real-time Recognition</h3>
            <p>Lightning fast face matching using state-of-the-art AI models for instant attendance marking.</p>
          </Card>
          <Card className="feature-card">
            <div className="feature-icon">🛡️</div>
            <h3>Accurate Records</h3>
            <p>Cryptographically secure and tamper-proof attendance logs that eliminate proxy marking.</p>
          </Card>
          <Card className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Easy Reporting</h3>
            <p>Generate detailed attendance reports and analytics with just a few clicks for faculty.</p>
          </Card>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-number">500+</span>
            <span className="stat-label">Students</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">12</span>
            <span className="stat-label">Courses</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">98%</span>
            <span className="stat-label">Accuracy Rate</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="home-footer">
        <div className="footer-content">
          <p>&copy; {new Date().getFullYear()} Attendance Management System. All rights reserved.</p>
          <div className="footer-links">
            <a href="#privacy">Privacy Policy</a>
            <a href="#terms">Terms of Service</a>
            <a href="#contact">Contact Support</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomeDashboard;
