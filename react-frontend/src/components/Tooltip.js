import React, { useState } from 'react';
import '../styles/Tooltip.css';

const Tooltip = ({ content, children }) => {
  const [isVisible, setIsVisible] = useState(false);

  const handleToggle = () => setIsVisible(prev => !prev);

  return (
    <span
      className="tooltip-container"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onClick={handleToggle}
      tabIndex={0}
      aria-describedby="tooltip"
    >
      {children}
      {isVisible && (
        <span className="tooltip-box" id="tooltip">
          {content}
        </span>
      )}
    </span>
  );
};

export default Tooltip;
