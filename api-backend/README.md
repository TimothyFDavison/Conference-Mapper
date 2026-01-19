# API Backend
A Flask-based REST API that serves conference data from the PostgreSQL database. The API provides endpoints
for retrieving available categories and querying conference markers based on filter criteria.

### Installation
The API runs inside a Docker container. To build and run independently,
```bash
docker build -t conference-api .
docker run -p 5000:5000 -e DB_HOST=localhost conference-api
```
The API will be available at port 5000. Note that the database must be running and accessible
at the configured host; see the main README for full-system deployment.

### Endpoints

**GET /api/categories**

Returns a list of available conference categories. Categories are derived from the database tables
created by the scraper.

**POST /api/markers**

Returns conference markers based on query parameters. Accepts a JSON body with the following fields:
- `categories`: Array of category objects with `value` field
- `start_date`: ISO date string for filtering by conference start date
- `end_date`: ISO date string for filtering by conference end date
- `open_cfp`: Boolean to filter for conferences with open calls for papers

### Configuration
Database connection parameters are defined in config.py and can be overridden via environment variables.
The `DB_HOST` variable is particularly relevant for Docker deployments.
