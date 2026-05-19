import React, { useId } from 'react';
import PropTypes from 'prop-types';
import './theme.css';
import './Modal.css';

export const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  variant = 'default',
  closeOnOverlayClick = true,
  className = '',
  ...props
}) => {
  if (!isOpen) return null;
  const titleId = useId();

  const handleOverlayClick = (e) => {
    if (closeOnOverlayClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  const modalClasses = [
    'ui-modal',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={modalClasses} onClick={handleOverlayClick}>
      <div className="ui-modal__overlay" aria-hidden="true" />
      <div className="ui-modal__frame" role="dialog" aria-modal="true" aria-labelledby={title ? titleId : undefined} {...props}>
        <div className={`ui-modal__panel ui-modal__panel--${size} ui-modal__panel--${variant}`}>
          {title && (
            <div className="ui-modal__header">
              <h3 className="ui-modal__title" id={titleId}>{title}</h3>
            </div>
          )}
          <div className="ui-modal__body">
            {children}
          </div>
          {footer && (
            <div className="ui-modal__footer">
              {footer}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

Modal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  title: PropTypes.string,
  children: PropTypes.node.isRequired,
  footer: PropTypes.node,
  size: PropTypes.oneOf(['sm', 'md', 'lg', 'xl', '2xl']),
  variant: PropTypes.oneOf(['default', 'danger']),
  closeOnOverlayClick: PropTypes.bool,
  className: PropTypes.string
};

Modal.defaultProps = {
  size: 'md',
  variant: 'default',
  closeOnOverlayClick: true
};

export default Modal;