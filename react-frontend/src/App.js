import React from 'react';
import MyMap from './pages/Map';
import './styles/Base.css';
import './styles/MapFilters.css';
import './styles/Modal.css';
import './styles/Tooltip.css';
import './styles/Responsive.css';

function App() {
  return (
    <div style={{ height: '100%' }}>
      <MyMap />
    </div>
  );
}

export default App;
