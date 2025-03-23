import L from 'leaflet';

// Set leaflet to use locally stored icons
const markerIconUrl = '/leaflet-icons/marker-icon.png';
const markerShadowUrl = '/leaflet-icons/marker-shadow.png';
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconUrl: markerIconUrl,
  shadowUrl: markerShadowUrl,
});

export default L;
