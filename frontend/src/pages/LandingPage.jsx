import React from 'react'
import { Link } from 'react-router-dom'
import { GradientButton } from '../shared/ui/GradientButton/GradientButton'
import { GlassPanel } from '../shared/ui/GlassPanel/GlassPanel'
import './LandingPage.css'

const LandingPage = () => {
  const features = [
    {
      title: 'Face Check-in',
      description: 'Students verify their identity with camera-based facial recognition before joining a class session.',
      icon: 'face',
    },
    {
      title: 'Faculty Control',
      description: 'Faculty can review, create, edit, and correct attendance records when needed.',
      icon: 'faculty',
    },
    {
      title: 'Student History',
      description: 'Students can track their own attendance records securely from their dashboard.',
      icon: 'history',
    },
    {
      title: 'PostgreSQL Storage',
      description: 'Attendance, users, roles, and face embeddings are stored in a structured database.',
      icon: 'database',
    },
  ]

  const steps = [
    'Create student account',
    'Register face image',
    'Student checks in',
    'Faculty reviews records',
  ]

  return (
    <div className="landing-page">
      <header className="landing-header">
        <div className="landing-container landing-header__inner">
          <Link to="/" className="landing-logo">
            <span className="landing-logo__mark">AI</span>
            <span className="landing-logo__text">Attendify</span>
          </Link>

          <nav className="landing-nav">
            <a href="#features">Features</a>
            <a href="#workflow">Workflow</a>
            <Link to="/login" className="landing-nav__login">
              Login
            </Link>
          </nav>
        </div>
      </header>

      <main>
        <section className="landing-hero">
          <div className="landing-container landing-hero__grid">
            <div className="landing-hero__content">
              <div className="landing-eyebrow">
                Facial Recognition Attendance System
              </div>

              <h1>
                Smarter attendance for modern classrooms.
              </h1>

              <p>
                A secure attendance platform where students can check in with facial
                recognition, while faculty manage records, corrections, and classroom
                attendance data in real time.
              </p>

              <div className="landing-hero__actions">
                <Link to="/login">
                  <GradientButton variant="navy-gold" size="lg">
                    Go to Login
                  </GradientButton>
                </Link>

                <a href="#features" className="landing-secondary-link">
                  Explore features
                </a>
              </div>

              <div className="landing-hero__stats">
                <div>
                  <strong>JWT</strong>
                  <span>Secure auth</span>
                </div>
                <div>
                  <strong>Face ID</strong>
                  <span>Camera check-in</span>
                </div>
                <div>
                  <strong>PostgreSQL</strong>
                  <span>Reliable storage</span>
                </div>
              </div>
            </div>

            <div className="landing-hero__visual">
              <div className="dashboard-preview">
                <div className="dashboard-preview__top">
                  <span />
                  <span />
                  <span />
                </div>

                <div className="dashboard-preview__body">
                  <div className="scan-card">
                    <div className="scan-card__frame">
                      <div className="scan-card__face">
                        <span className="scan-card__eye scan-card__eye--left" />
                        <span className="scan-card__eye scan-card__eye--right" />
                        <span className="scan-card__smile" />
                      </div>
                      <span className="scan-corner scan-corner--tl" />
                      <span className="scan-corner scan-corner--tr" />
                      <span className="scan-corner scan-corner--bl" />
                      <span className="scan-corner scan-corner--br" />
                    </div>

                    <div>
                      <h3>Face verified</h3>
                      <p>Roll No: 12001 · Lecture 102</p>
                    </div>
                  </div>

                  <div className="preview-list">
                    <div className="preview-row">
                      <span className="preview-dot is-green" />
                      <div>
                        <strong>Computer Science</strong>
                        <small>Present · 09:30 AM</small>
                      </div>
                    </div>

                    <div className="preview-row">
                      <span className="preview-dot is-gold" />
                      <div>
                        <strong>Faculty Review</strong>
                        <small>3 records updated today</small>
                      </div>
                    </div>

                    <div className="preview-row">
                      <span className="preview-dot is-blue" />
                      <div>
                        <strong>Student Dashboard</strong>
                        <small>Attendance history synced</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="floating-badge floating-badge--top">
                Live Camera
              </div>
              <div className="floating-badge floating-badge--bottom">
                Check-in success
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="landing-section">
          <div className="landing-container">
            <div className="landing-section__header">
              <span>Core modules</span>
              <h2>Everything needed for attendance management</h2>
              <p>
                Built around student self check-in, faculty control, and secure
                attendance records.
              </p>
            </div>

            <div className="landing-feature-grid">
              {features.map((feature) => (
                <GlassPanel key={feature.title} className="landing-feature-card" animated>
                  <div className={`landing-feature-card__icon icon-${feature.icon}`} />
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                </GlassPanel>
              ))}
            </div>
          </div>
        </section>

        <section id="workflow" className="landing-workflow">
          <div className="landing-container landing-workflow__grid">
            <div>
              <span className="landing-section-label">Workflow</span>
              <h2>Simple flow from registration to check-in</h2>
              <p>
                Faculty prepares student profiles and face images. Students then
                check in by camera, and the system stores the attendance result.
              </p>
            </div>

            <div className="workflow-steps">
              {steps.map((step, index) => (
                <div className="workflow-step" key={step}>
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  <strong>{step}</strong>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="landing-final-cta">
          <div className="landing-container">
            <div className="landing-final-cta__panel">
              <h2>Ready to manage attendance smarter?</h2>
              <p>
                Login as faculty or student to start testing the complete attendance flow.
              </p>
              <Link to="/login">
                <GradientButton variant="navy-gold" size="lg">
                  Open Dashboard
                </GradientButton>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="landing-footer">
        <div className="landing-container landing-footer__inner">
          <span>Attendify</span>
          <p>Facial Recognition Attendance System</p>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage