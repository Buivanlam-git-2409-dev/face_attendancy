import React from 'react'
import './GlassPanel.css'

export const GlassPanel = ({
  children,
  className = '',
  elevated = false,
  animated = false,
  delay = 0,
  ...props
}) => {
  const classes = [
    'glass-panel',
    elevated && 'glass-panel--elevated',
    animated && 'glass-panel--animated',
    className,
  ]
    .filter(Boolean)
    .join(' ')

  const style = animated ? { '--delay': `${delay}ms` } : {}

  return (
    <div className={classes} style={style} {...props}>
      {children}
    </div>
  )
}
