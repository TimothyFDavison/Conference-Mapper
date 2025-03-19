import React, { useState } from 'react';
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
  const { markers, loading, error } = useMarkers(selectedOptions, startDate, endDate, openCfp);

  const customStyles = {
    control: (provided) => ({
      ...provided,
      width: 300,
      height: 60,
    }),
    menu: (provided) => ({
      ...provided,
      width: 300,
    }),
    multiValue: (provided) => ({
      ...provided,
      maxWidth: '100%',
      overflow: 'hidden',
    }),
    multiValueLabel: (provided) => ({
      ...provided,
      maxWidth: '100%',
      overflow: 'hidden',
    }),
    valueContainer: (provided) => ({
      ...provided,
      height: '100%',
      overflowY: 'auto',
      maxHeight: 60,
      alignItems: 'flex-start'
    }),
    placeholder: (provided) => ({
      ...provided,
      alignSelf: "center",
      margin: "0",
      padding: "0",
      fontSize: "16px",
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

      {/* Theme toggle button */}
      <button
        onClick={() => setDarkMode(!darkMode)}
        style={{
          position: "absolute",
          bottom: "10px",
          left: "85px",
          zIndex: 1000,
          padding: "10px 15px",
          backgroundColor: darkMode ? "#fff" : "#333",
          color: darkMode ? "#333" : "#fff",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
        }}
      >
        {darkMode ? "Light" : "Dark"} Mode
      </button>

      {/* About Modal Toggle Button */}
      <button
        onClick={() => setShowModal(true)}
        style={{
          position: 'absolute',
          bottom: '10px',
          left: '10px',
          zIndex: 1000,
          padding: '10px 15px',
          backgroundColor: '#fff',
          color: '#333',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
        }}
      >
        About
      </button>

      {/* About Modal Component */}
      <AboutModal showModal={showModal} onClose={() => setShowModal(false)} />

      {/* Map Container */}
      <MapContainer center={[20, 0]} zoom={2} zoomControl={false} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          url={darkMode ? darkTile : lightTile}
          attribution='malevolentelk'
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
