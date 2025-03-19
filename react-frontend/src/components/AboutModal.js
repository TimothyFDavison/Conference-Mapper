import React from 'react';

const AboutModal = ({ showModal, onClose }) => {
  if (!showModal) return null;

  return (
    <div
      className="modal"
      onClick={onClose}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.5)',
        zIndex: 3000, // Increased z-index
      }}
    >
      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="close-btn"
          onClick={onClose}
          style={{ position: 'absolute', top: '10px', right: '10px' }}
        >
          X
        </button>
        <h2>Conference Mapper</h2>
        <p>For when you want your work travel to be fun travel.</p>
        <p>
          Data is scraped nightly from WikiCFP. Conferences not listed on WikiCFP will not be shown.
          Accuracy, completeness, and proper data cleaning are not guaranteed.
          Conferences with missing or incomplete location data are ignored.
        </p>
        <p>
          In the conference information markers, "CFP Deadline" refers to the call for proposals, i.e.
          when you need to submit your abstract in order to present.
        </p>
      </div>
    </div>
  );
};

export default AboutModal;
