import React, { useId, useState } from 'react';
import PropTypes from 'prop-types';
import '../theme.css';
import './Input.css';

export const Input = ({
  label,
  variant = 'default',
  error,
  success,
  tooltip,
  icon,
  type = 'text',
  passwordToggle = false,
  className = '',
  id,
  ...props
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const inputId = id || useId();
  const resolvedVariant = error ? 'error' : (success ? 'success' : variant);
  const inputType = (type === 'password' && showPassword) ? 'text' : type;
  const inputClasses = [
    'ui-input',
    `ui-input--${resolvedVariant}`,
    icon ? 'ui-input--with-icon' : '',
    className
  ].filter(Boolean).join(' ');

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="ui-input__wrapper">
      {label && (
        <label className="ui-input__label" htmlFor={inputId}>
          {label}
          {tooltip && (
            <span className="ui-input__tooltip" title={tooltip}>i</span>
          )}
        </label>
      )}

      <div className="ui-input__field">
        {icon && (
          <div className="ui-input__icon" aria-hidden="true">
            {icon}
          </div>
        )}
        <input
          type={inputType}
          className={inputClasses}
          id={inputId}
          aria-invalid={Boolean(error)}
          {...props}
        />
        {type === 'password' && passwordToggle && (
          <button
            type="button"
            className="ui-input__toggle"
            onClick={togglePasswordVisibility}
            aria-pressed={showPassword}
          >
            {showPassword ? 'Hide' : 'Show'}
          </button>
        )}
      </div>

      {error && (
        <p className="ui-input__error">{error}</p>
      )}
    </div>
  );
};

Input.propTypes = {
  label: PropTypes.string,
  variant: PropTypes.oneOf(['default', 'filled', 'error', 'success']),
  error: PropTypes.string,
  success: PropTypes.bool,
  tooltip: PropTypes.string,
  icon: PropTypes.node,
  type: PropTypes.string,
  passwordToggle: PropTypes.bool,
  className: PropTypes.string,
  id: PropTypes.string
};

Input.defaultProps = {
  variant: 'default',
  type: 'text'
};

export default Input;