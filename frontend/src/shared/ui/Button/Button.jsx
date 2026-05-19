import React from 'react';
import PropTypes from 'prop-types';
import '../theme.css';
import './Button.css';

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  type = 'button',
  disabled = false,
  loading = false,
  fullWidth = false,
  icon,
  iconPosition = 'left',
  onClick,
  className = '',
  ...props
}) => {
  const buttonClasses = [
    'ui-button',
    `ui-button--${variant}`,
    `ui-button--${size}`,
    fullWidth ? 'ui-button--block' : '',
    loading ? 'ui-button--loading' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      className={buttonClasses}
      type={type}
      disabled={disabled || loading}
      aria-busy={loading}
      onClick={onClick}
      {...props}
    >
      {loading && (
        <span className="ui-button__spinner" aria-hidden="true" />
      )}
      {icon && iconPosition === 'left' && (
        <span className="ui-button__icon ui-button__icon--left">{icon}</span>
      )}
      <span className="ui-button__label">{children}</span>
      {icon && iconPosition === 'right' && (
        <span className="ui-button__icon ui-button__icon--right">{icon}</span>
      )}
    </button>
  );
};

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary', 'outline', 'ghost', 'destructive', 'link']),
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  type: PropTypes.oneOf(['button', 'submit', 'reset']),
  disabled: PropTypes.bool,
  loading: PropTypes.bool,
  fullWidth: PropTypes.bool,
  icon: PropTypes.node,
  iconPosition: PropTypes.oneOf(['left', 'right']),
  onClick: PropTypes.func,
  className: PropTypes.string
};

Button.defaultProps = {
  variant: 'primary',
  size: 'md',
  iconPosition: 'left'
};

export default Button;