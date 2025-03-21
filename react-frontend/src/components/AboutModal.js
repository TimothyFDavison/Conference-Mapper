import React from 'react';
import '../styles/AboutModal.css';

const AboutModal = ({ showModal, onClose }) => {
  if (!showModal) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>
          &times;
        </button>
        <h2 className="modal-heading">Conference Mapper</h2>
        <div className="modal-body">
          <p>
            Data scraped nightly from{" "}
            <a href="http://www.wikicfp.com/cfp/" className={"link"}
               target="_blank" rel="noopener noreferrer">WikiCFP</a>.
            Neither accuracy nor completeness guaranteed.
            Conferences with missing or incomplete location data are ignored.
          </p>
          <p>
            Not all{" "}
            <a href="http://www.wikicfp.com/cfp/allcat" className={"link"}
               target="_blank" rel="noopener noreferrer">available categories</a>{" "}
            are represented here, but feel free to{" "}
            <a href="https://timothyfdavison.com/" className={"link"}
               target="_blank" rel="noopener noreferrer">reach out</a>{" "}
            if there are any that you'd like me to add to the scraper.
          </p>
          <p>
            If WikiCFP ever goes down, so will this website. In the meantime, enjoy!
          </p>
        </div>
      </div>
    </div>
  );
};

export default AboutModal;
