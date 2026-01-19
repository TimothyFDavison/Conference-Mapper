# React Frontend
A map-based interface for browsing academic conferences. Built with React and Leaflet, the application displays
conference markers on an interactive world map with filtering capabilities for category, date range, and CFP status.

### Installation
The frontend runs inside a Docker container and is served via nginx. To build and run independently,
```bash
docker build -t conference-frontend .
docker run -p 3000:80 conference-frontend
```
The application will be available at port 3000. Note that the frontend expects the API backend to be
available at port 5000; see the main README for full-system deployment.

### Structure
```
src/
  components/   # Reusable UI components (filters, markers, modals, tooltips)
  config/       # Leaflet configuration
  hooks/        # Custom React hooks for data fetching
  pages/        # Main page components
  services/     # API service layer
  styles/       # CSS stylesheets
```

### Dependencies
Key libraries include React 19, Leaflet for mapping, react-select for dropdowns, and react-datepicker
for date inputs. See package.json for the full list.
