import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import MarkerClusterGroup from "react-leaflet-markercluster";
import 'react-leaflet-markercluster/styles'


const MarkerLayer = React.memo(({ markers, generatePopupContent }) => {
  return (
    <MarkerClusterGroup maxClusterRadius={5}>
      {markers.map((marker, idx) => (
        <Marker key={idx} position={[marker.lat, marker.lon]}>
          <Popup>{generatePopupContent(marker)}</Popup>
        </Marker>
      ))}
    </MarkerClusterGroup>
  );
});

export default MarkerLayer;
