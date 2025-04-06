import React, { useState, useRef } from 'react';
import useOutsideClick from '../hooks/useOutsideClick';
import Select, { components } from 'react-select';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { FiFilter, FiX, FiHelpCircle } from 'react-icons/fi';
import { MdClear } from 'react-icons/md';
import Tooltip from './Tooltip';
import '../styles/MapFilters.css';

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

  // Handle select all functionality
  const handleSelectChange = (selected) => {
    // Check if the select all option was clicked
    if (selected?.some(option => option.value === '*')) {
      // If selecting "all", return all options except the "Select All" option
      onSelectChange(categoryOptions);
    } else {
      // Normal selection
      onSelectChange(selected || []);
    }
  };

  // Create options array with Select All option
  const allOptions = [
    {
      label: 'Select All Categories',
      value: '*',
      isSelectAll: true
    },
    { label: '──────────────', value: 'separator', isDisabled: true },
    ...categoryOptions
  ];

  // Custom components for Select
  const Option = ({ children, ...props }) => {
    // Style select all option differently
    const optionStyle = props.data.isSelectAll ? {
      fontWeight: 500,
      color: '#007bff',
      padding: '10px 12px'
    } : undefined;

    return (
      <components.Option 
        {...props} 
        data-is-select-all={props.data.isSelectAll}
      >
        <div style={optionStyle}>{children}</div>
      </components.Option>
    );
  };

  // Custom clear indicator that preserves the native styling
  const ClearIndicator = props => {
    const {
      children = <components.ClearIndicator {...props} />,
      innerProps: { ref, ...restInnerProps }
    } = props;
    return (
      <div
        {...restInnerProps}
        ref={ref}
        onMouseDown={e => {
          e.preventDefault(); // Prevent the menu from closing
          e.stopPropagation();
          handleSelectChange([]); // Clear the selection
        }}
      >
        {children}
      </div>
    );
  };

  return (
    <div className="filter-container" ref={containerRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="filter-toggle"
        style={{
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          boxShadow: '0 2px 5px rgba(0, 0, 0, 0.2)',
        }}
      >
        {isOpen ? 'Hide Filters' : 'Show Filters'}
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
              onChange={handleSelectChange}
              placeholder="Conference category"
              options={allOptions}
              styles={customStyles}
              components={{ Option, ClearIndicator }}
              hideSelectedOptions={false}
              isClearable={true}
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
