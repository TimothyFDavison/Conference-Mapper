import React, { useState } from 'react';
import '../styles/Tooltip.css';

const Tooltip = ({ content, children }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <span
      className="tooltip-container"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
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
