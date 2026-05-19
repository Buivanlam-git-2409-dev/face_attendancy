import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { GradientButton } from '../shared/ui/GradientButton/GradientButton'
import { GlassPanel } from '../shared/ui/GlassPanel/GlassPanel'
import './LandingPage.css'

const LandingPage = () => {
  const [hoveredCard, setHoveredCard] = useState(null)

  const features = [
    {
      id: 1,
      title: 'Face Recognition',
      subtitle: 'Attendance',
      description:
        'Fast and accurate facial recognition technology for seamless student and faculty check-ins.',
      icon: '👤',
    },
    {
      id: 2,
      title: 'Real-time',
      subtitle: 'Monitoring',
      description:
        'Live attendance tracking for faculty with instant notifications and detailed analytics.',
      icon: '📊',
    },
    {
      id: 3,
      title: 'Attendance',
      subtitle: 'History',
      description:
        'Complete attendance records for students with visual trends and historical data.',
      icon: '📋',
    },
    {
      id: 4,
      title: 'Secure',
      subtitle: 'Access Control',
      description:
        'Role-based access with secure authentication for students, faculty, and administrators.',
      icon: '🔐',
    },
  ]

  const benefits = [
    {
      icon: '⚡',
      title: 'Lightning Fast',
      description: 'Check-in in under 2 seconds with advanced facial recognition',
    },
    {
      icon: '✓',
      title: 'Accurate',
      description: 'Eliminate manual errors with 99%+ recognition accuracy',
    },
    {
      icon: '📱',
      title: 'Real-time Dashboards',
      description: 'View live attendance data from anywhere, anytime',
    },
    {
      icon: '🛡️',
      title: 'Enterprise Security',
      description: 'Bank-grade encryption and role-based access control',
    },
  ]

  return (
    <div className="landing-page">
      {/* Header/Navigation */}
      <header className="landing-header">
        <div className="landing-container">
          <div className="landing-logo">
            <span className="logo-icon">📚</span>
            <span className="logo-text">AttendanceAI</span>
          </div>

          <nav className="landing-nav">
            <a href="#features" className="nav-link">
              Features
            </a>
            <a href="#benefits" className="nav-link">
              Benefits
            </a>
            <Link to="/login" className="nav-cta">
              Login
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="landing-hero">
        <div className="landing-container">
          <div className="hero-content fade-up-in">
            <h1 className="hero-title">
              Modern Facial Recognition
              <br />
              <span className="text-gradient">Attendance for Education</span>
            </h1>

            <p className="hero-subtitle">
              Secure, fast, and reliable attendance management system for schools and universities.
              Experience the future of student and faculty check-ins with cutting-edge AI technology.
            </p>

            <div className="hero-ctas">
              <Link to="/login">
                <GradientButton variant="navy-gold" size="lg">
                  Get Started →
                </GradientButton>
              </Link>
              <button className="cta-secondary">Learn More</button>
            </div>

            <p className="hero-trust">Trusted by educational institutions worldwide</p>
          </div>

          <div className="hero-visual fade-up-in" style={{ animationDelay: '200ms' }}>
            <div className="hero-illustration">
              <div className="illustration-box box-1" />
              <div className="illustration-box box-2" />
              <div className="illustration-box box-3" />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="landing-features">
        <div className="landing-container">
          <div className="section-header">
            <h2>Core Features</h2>
            <p>Everything you need for modern attendance management</p>
          </div>

          <div className="features-grid">
            {features.map((feature, idx) => (
              <GlassPanel
                key={feature.id}
                className="feature-card"
                animated
                delay={idx * 100}
                onMouseEnter={() => setHoveredCard(feature.id)}
                onMouseLeave={() => setHoveredCard(null)}
              >
                <div
                  className={`feature-card__icon ${
                    hoveredCard === feature.id ? 'active' : ''
                  }`}
                >
                  {feature.icon}
                </div>

                <h3 className="feature-card__title">
                  {feature.title}
                  <br />
                  <span className="feature-subtitle">{feature.subtitle}</span>
                </h3>

                <p className="feature-card__description">{feature.description}</p>
              </GlassPanel>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section id="benefits" className="landing-benefits">
        <div className="landing-container">
          <div className="section-header">
            <h2>Why Choose AttendanceAI?</h2>
            <p>Industry-leading features for educational institutions</p>
          </div>

          <div className="benefits-grid">
            {benefits.map((benefit, idx) => (
              <div
                key={idx}
                className="benefit-item fade-up-in"
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                <div className="benefit-icon">{benefit.icon}</div>
                <h3>{benefit.title}</h3>
                <p>{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="landing-cta-final">
        <div className="landing-container">
          <GlassPanel className="cta-panel" elevated animated>
            <div className="cta-content">
              <h2>Ready to Transform Your Institution's Attendance?</h2>
              <p>Join schools and universities that are modernizing their attendance systems.</p>

              <div className="cta-buttons">
                <Link to="/login">
                  <GradientButton variant="navy-gold" size="lg">
                    Start Your Journey
                  </GradientButton>
                </Link>
                <button className="cta-secondary">Schedule a Demo</button>
              </div>
            </div>
          </GlassPanel>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="landing-container">
          <div className="footer-content">
            <div className="footer-brand">
              <span className="logo-icon">📚</span>
              <span>AttendanceAI</span>
            </div>

            <div className="footer-links">
              <a href="#features">Features</a>
              <a href="#benefits">Benefits</a>
              <Link to="/login">Login</Link>
            </div>

            <p className="footer-copyright">
              © {new Date().getFullYear()} AttendanceAI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
