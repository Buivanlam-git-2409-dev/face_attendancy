import React, { useEffect, useState } from 'react'
import './StatCard.css'

const AnimatedCounter = ({ target, duration = 2000, prefix = '', suffix = '' }) => {
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (typeof target !== 'number') {
      setCount(target)
      return
    }

    let currentValue = 0
    const increment = target / (duration / 16)
    const interval = setInterval(() => {
      currentValue += increment
      if (currentValue >= target) {
        setCount(target)
        clearInterval(interval)
      } else {
        setCount(Math.floor(currentValue))
      }
    }, 16)

    return () => clearInterval(interval)
  }, [target, duration])

  return (
    <span>
      {prefix}
      {typeof count === 'number' ? count.toLocaleString() : count}
      {suffix}
    </span>
  )
}

export const StatCard = ({
  icon: Icon,
  label,
  value,
  suffix = '',
  prefix = '',
  description,
  trend,
  trendLabel,
  animated = true,
  className = '',
  delay = 0,
  ...props
}) => {
  const classes = [
    'stat-card',
    'stat-card--animated',
    className,
  ]
    .filter(Boolean)
    .join(' ')

  const style = { '--delay': `${delay}ms` }

  return (
    <div className={classes} style={style} {...props}>
      {Icon && (
        <div className="stat-card__icon">
          <Icon />
        </div>
      )}

      <div className="stat-card__content">
        <p className="stat-card__label">{label}</p>

        <div className="stat-card__value">
          {animated ? (
            <AnimatedCounter target={value} prefix={prefix} suffix={suffix} />
          ) : (
            <>
              {prefix}
              {value}
              {suffix}
            </>
          )}
        </div>

        {description && (
          <p className="stat-card__description">{description}</p>
        )}

        {trend && (
          <div className={`stat-card__trend stat-card__trend--${trend}`}>
            <span className="stat-card__trend-label">
              {trend === 'up' && '↑'}
              {trend === 'down' && '↓'}
              {trend === 'stable' && '→'}
              {trendLabel}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
