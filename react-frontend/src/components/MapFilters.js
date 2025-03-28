import React, { useState, useRef } from 'react';
import useOutsideClick from '../hooks/useOutsideClick';
import Select from 'react-select';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { FiFilter, FiX, FiHelpCircle } from 'react-icons/fi';
import Tooltip from './Tooltip';

const MapFilters = ({
  categoryOptions,
  selectedOptions,
  onSelectChange,
  startDate,
  onStartDateChange,
  endDate,
  onEndDateChange,
  openCfp,
  onOpenCfpChange,
  customStyles,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  useOutsideClick(containerRef, () => setIsOpen(false));

  return (
    <div className="filter-container" ref={containerRef}>
      <button className="filter-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? <FiX /> : <FiFilter />} Filters
      </button>
      {isOpen && (
        <div className="filter-box">
          <div className="filter-section">
            <label>
              Conference Category
              <Tooltip content={
                <>
                  Conference categories as defined by:<br/>
                  <a href=" http://www.wikicfp.com/cfp/allcat" target="_blank" rel="noopener noreferrer">
                    http://www.wikicfp.com/cfp/allcat
                  </a>
                </>
              }>
                <FiHelpCircle className="tooltip-icon" />
              </Tooltip>
            </label>
            <Select
              isMulti
              className="react-select-container"
              classNamePrefix="react-select"
              value={selectedOptions}
              onChange={onSelectChange}
              placeholder="Conference category"
              options={categoryOptions}
              styles={customStyles}
            />
          </div>
          <div className="filter-section">
            <label>Start Date</label>
            <DatePicker
              selected={startDate}
              onChange={onStartDateChange}
              selectsStart
              startDate={startDate}
              endDate={endDate}
              placeholderText="Select start date"
              isClearable
            />
          </div>
          <div className="filter-section">
            <label>End Date</label>
            <DatePicker
              selected={endDate}
              onChange={onEndDateChange}
              selectsEnd
              startDate={startDate}
              endDate={endDate}
              minDate={startDate}
              placeholderText="Select end date"
              isClearable
            />
          </div>
          <div className="filter-section checkbox">
            <input
              type="checkbox"
              id="open-cfp"
              checked={openCfp}
              onChange={onOpenCfpChange}
            />
            <label htmlFor="open-cfp">
              Only show open CFPs
              <Tooltip content={
                <>
                  Call for papers (CFP), referring to the deadline <br/>
                  to submit an abstract and present at the conference.
                </>
              }>
                <FiHelpCircle className="tooltip-icon"/>
              </Tooltip></label>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapFilters;
