import React from 'react';
import './Alert.css';

export const Alert = ({ 
  children, 
  variant = 'info', 
  title,
  className = '' 
}) => {
  return (
    <div className={`alert alert-${variant} ${className}`} role="alert">
      {title && <div className="alert-title">{title}</div>}
      <div className="alert-content">{children}</div>
    </div>
  );
};
