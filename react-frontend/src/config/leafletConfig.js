import L from 'leaflet';

// Set leaflet to use locally stored icons
const markerIconUrl = '/leaflet-icons/marker-icon.png';
const markerIcon2xUrl = '/leaflet-icons/marker-icon-2x.png';
const markerShadowUrl = '/leaflet-icons/marker-shadow.png';
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconUrl: markerIconUrl,
  iconRetinaUrl: markerIcon2xUrl,
  shadowUrl: markerShadowUrl,
});

export default L;
