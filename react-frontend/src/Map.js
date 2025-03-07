// react-frontent/MyMap.js
import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import markerIconPng from "leaflet/dist/images/marker-icon.png";
import markerShadowPng from "leaflet/dist/images/marker-shadow.png";
import 'react-leaflet-markercluster/styles'
import MarkerClusterGroup from "react-leaflet-markercluster";

// Default icons show up as boxes in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIconPng,
  shadowUrl: markerShadowPng,
});

function MyMap() {
  const [markers, setMarkers] = useState([]);
  const [loading, setLoading] = useState(true);

  const [darkMode, setDarkMode] = useState(true);
  const darkTile = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";
  const lightTile = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";

  const [showModal, setShowModal] = useState(false);
  const handleModalToggle = () => {
    setShowModal(!showModal);
  };


  // Fetch marker data from the backend API
  const categories = null; // or [] or other values
  const startDate = null; // or a valid date string like "2023-01-01"
  const endDate = null; // or a valid date string like "2023-12-31"
  const pastCfpDeadline = null; // or true/false
  const params = new URLSearchParams();
  if (categories !== null) {
    params.append('categories', categories);
  }
  if (startDate !== null) {
      params.append('start_date', startDate);
  }
  if (endDate !== null) {
      params.append('end_date', endDate);
  }
  if (pastCfpDeadline !== null) {
      params.append('past_cfp_deadline', pastCfpDeadline);
  }
  useEffect(() => {
    fetch(`http://localhost:5000/api/markers?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            setMarkers(data);
            setLoading(false);
        })
        .catch(err => {
            console.error('Error fetching markers:', err);
            setLoading(false);
        });
}, []);


    const generatePopupContent = (marker) => {
        return (
            <div style={{maxWidth: '250px'}}>
                <h3 style={{margin: '0 0 10px'}}>{marker.abbreviation}</h3>
                {marker.location &&
                    <p style={{fontSize: '14px', margin: '0 0 5px'}}><strong>Location:</strong> {marker.location}</p>}
                <p style={{fontSize: '14px', margin: '0 0 5px'}}><strong>Description:</strong> {marker.name}</p>
                <p style={{fontSize: '14px', margin: '0 0 5px'}}><strong>Date:</strong> {marker.dates}</p>
                <p style={{fontSize: '14px', margin: '0 0 5px'}}><strong>CFP Deadline:</strong> {marker.cfp}</p>
            </div>
        );
    };

    return (
    <div style={{position: "relative", height: "100vh", width: "100%" }}>
      <button
        onClick={() => setDarkMode(!darkMode)}
        style={{
          position: "absolute",
          bottom: "10px",
          left: "10px",
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
      <button
        onClick={handleModalToggle}
        style={{
          position: 'absolute',
          bottom: '50px',
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
        {showModal && (
        <div className="modal" onClick={() => setShowModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="close-btn" onClick={() => setShowModal(false)}>
                    X
                </button>
                <h2>Conference Mapper</h2>
                <p>For when you want your work travel to be fun travel.</p>
                <p>Data is scraped nightly from WikiCFP. Conferences not listed on WikiCFP will not be
                    shown. Accuracy, completeness, and proper data cleaning are not guaranteed. Conferences with
                    missing or incomplete location data are ignored.</p>
                <p>In the conference information markers, "CFP Deadline" refers to the call for proposals, i.e.
                    when you need to submit your abstract in order to present.</p>
            </div>
        </div>
        )}

        <MapContainer center={[20, 0]} zoom={2} zoomControl={false} style={{height: '100%', width: '100%'}}>
            <TileLayer
                url={darkMode ? darkTile : lightTile}
                attribution='malevolentelk'
            />
            {!loading && (
                <MarkerClusterGroup maxClusterRadius={5}>
          {markers.map((marker, idx) => (
            <Marker key={idx} position={[marker.lat, marker.lon]}>
              <Popup>{generatePopupContent(marker)}</Popup>
            </Marker>
          ))}
        </MarkerClusterGroup>
      )}
    </MapContainer>

  </div>
  );
}

export default MyMap;
