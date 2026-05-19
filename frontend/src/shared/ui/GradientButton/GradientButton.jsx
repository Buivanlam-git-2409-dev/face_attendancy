import React from 'react'
import './GradientButton.css'

export const GradientButton = ({
  children,
  onClick,
  loading = false,
  disabled = false,
  variant = 'navy-gold',
  size = 'md',
  icon: Icon,
  className = '',
  type = 'button',
  ...props
}) => {
  const variantClass = `gradient-btn--${variant}`
  const sizeClass = `gradient-btn--${size}`
  const stateClass = disabled ? 'gradient-btn--disabled' : loading ? 'gradient-btn--loading' : ''

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`gradient-btn ${variantClass} ${sizeClass} ${stateClass} ${className}`.trim()}
      {...props}
    >
      <span className="gradient-btn__content">
        {Icon && <Icon className="gradient-btn__icon" />}
        {!loading ? children : (
          <span className="gradient-btn__spinner" />
        )}
      </span>
    </button>
  )
}
