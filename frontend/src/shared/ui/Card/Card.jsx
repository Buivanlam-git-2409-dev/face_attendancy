import React from 'react';
import PropTypes from 'prop-types';
import '../theme.css';
import './Card.css';

export const Card = ({
  children,
  variant = 'default',
  padding = 'md',
  header,
  footer,
  className = '',
  ...props
}) => {
  const cardClasses = [
    'ui-card',
    `ui-card--${variant}`,
    `ui-card--${padding}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={cardClasses} {...props}>
      {header && <div className="ui-card__header">{header}</div>}
      <div className="ui-card__body">{children}</div>
      {footer && <div className="ui-card__footer">{footer}</div>}
    </div>
  );
};

Card.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['default', 'outlined', 'subtle']),
  padding: PropTypes.oneOf(['none', 'sm', 'md', 'lg']),
  header: PropTypes.node,
  footer: PropTypes.node,
  className: PropTypes.string
};

Card.defaultProps = {
  variant: 'default',
  padding: 'md'
};

export default Card;