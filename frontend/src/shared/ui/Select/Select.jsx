import React, { useId } from 'react';
import PropTypes from 'prop-types';
import '../theme.css';
import './Select.css';

export const Select = ({
  label,
  options = [],
  value,
  onChange,
  error,
  id,
  className = '',
  disabled = false,
  ...props
}) => {
  const selectId = id || useId();
  const selectClasses = [
    'ui-select',
    error ? 'ui-select--error' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="ui-select__wrapper">
      {label && (
        <label className="ui-select__label" htmlFor={selectId}>
          {label}
        </label>
      )}
      <div className="ui-select__field">
        <select
          id={selectId}
          value={value}
          onChange={onChange}
          className={selectClasses}
          disabled={disabled}
          {...props}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
      {error && <p className="ui-select__error">{error}</p>}
    </div>
  );
};

Select.propTypes = {
  label: PropTypes.string,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired
    })
  ),
  value: PropTypes.string,
  onChange: PropTypes.func,
  error: PropTypes.string,
  id: PropTypes.string,
  className: PropTypes.string,
  disabled: PropTypes.bool
};

export default Select;
