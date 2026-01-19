import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import MarkerLayer from '../components/MarkerLayer';
import MapFilters from '../components/MapFilters';
import AboutModal from '../components/AboutModal';
import useCategories from '../hooks/useCategories';
import useMarkers from '../hooks/useMarkers';
import '../config/leafletConfig';

const MyMap = () => {

  const [darkMode, setDarkMode] = useState(true);
  const darkTile = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";
  const lightTile = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";

  const [selectedOptions, setSelectedOptions] = useState([]);
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(null);
  const [openCfp, setOpenCfp] = useState(false);

  const [showModal, setShowModal] = useState(false);

  const { categoryOptions } = useCategories();
  const hasSetDefaultCategory = useRef(false);

  // Set "Artificial Intelligence" as default category once categories load
  useEffect(() => {
    if (categoryOptions.length > 0 && !hasSetDefaultCategory.current) {
      const aiCategory = categoryOptions.find(
        option => option.label === 'Artificial Intelligence'
      );
      if (aiCategory) {
        setSelectedOptions([aiCategory]);
      }
      hasSetDefaultCategory.current = true;
    }
  }, [categoryOptions]);

  const { markers, loading, error } = useMarkers(selectedOptions, startDate, endDate, openCfp);

  const customStyles = {
    control: (provided) => ({
      ...provided,
      minHeight: '38px',
      height: 'auto',
      maxHeight: '60px',
      padding: '0',
    }),
    menu: (provided) => ({
      ...provided,
      width: '100%',
    }),
    multiValue: (provided) => ({
      ...provided,
      maxWidth: '100%',
      overflow: 'hidden',
      margin: '1px 4px',
    }),
    multiValueLabel: (provided) => ({
      ...provided,
      maxWidth: '100%',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      padding: '2px 6px',
    }),
    valueContainer: (provided) => ({
      ...provided,
      height: '100%',
      overflowY: 'auto',
      maxHeight: '60px',
      alignItems: 'center',
      padding: '2px 6px',
      gap: '2px',
    }),
    placeholder: (provided) => ({
      ...provided,
      alignSelf: "center",
      margin: "0",
      padding: "0",
      fontSize: "14px",
    }),
  };

  const generatePopupContent = (marker) => (
    <div style={{ maxWidth: '250px' }}>
      <h3 style={{ margin: '0 0 10px' }}>{marker.abbreviation}</h3>
      {marker.location && (
        <p style={{ fontSize: '14px', margin: '0 0 5px' }}>
          <strong>Location:</strong> {marker.location}
        </p>
      )}
      <p style={{ fontSize: '14px', margin: '0 0 5px' }}>
        <strong>Description:</strong> {marker.name}
      </p>
      <p style={{ fontSize: '14px', margin: '0 0 5px' }}>
        <strong>Date:</strong> {marker.dates}
      </p>
      <p style={{ fontSize: '14px', margin: '0 0 5px' }}>
        <strong>CFP Deadline:</strong> {marker.cfp}
      </p>
    </div>
  );

  return (
    <div style={{ position: "relative", height: "100vh", width: "100%" }}>
      {/* Filters Component */}
      <MapFilters
        categoryOptions={categoryOptions}
        selectedOptions={selectedOptions}
        onSelectChange={setSelectedOptions}
        startDate={startDate}
        onStartDateChange={setStartDate}
        endDate={endDate}
        onEndDateChange={setEndDate}
        openCfp={openCfp}
        onOpenCfpChange={() => setOpenCfp(!openCfp)}
        customStyles={customStyles}
      />

      {/* Map control buttons */}
      <div className="map-controls-bottom">
        <button
          className="map-control-btn map-control-btn--about"
          onClick={() => setShowModal(true)}
        >
          About
        </button>
        <button
          className={`map-control-btn ${darkMode ? 'map-control-btn--theme-light' : 'map-control-btn--theme-dark'}`}
          onClick={() => setDarkMode(!darkMode)}
        >
          {darkMode ? "Light" : "Dark"} Mode
        </button>
      </div>

      {/* About Modal Component */}
      <AboutModal showModal={showModal} onClose={() => setShowModal(false)} />

      {/* Map Container */}
      <MapContainer center={[20, 0]} zoom={2} minZoom={2} zoomControl={false} attributionControl={false} worldCopyJump={true} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          url={darkMode ? darkTile : lightTile}
          attribution='TFD'
          zIndex={1}
        />
        {loading ? (
          <p>Loading markers...</p>
        ) : error ? (
          <p>Error loading markers</p>
        ) : (
          <MarkerLayer markers={markers} generatePopupContent={generatePopupContent} />
        )}
      </MapContainer>
    </div>
  );
};

export default MyMap;
