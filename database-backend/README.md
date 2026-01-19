# Database Backend
A PostgreSQL database for storing conference data. The database is initialized with a categories table
that defines which WikiCFP categories to scrape; additional tables are created dynamically by the
scraper as data is ingested.

### Installation
The database runs inside a Docker container. To build and run independently,
```bash
docker build -t conference-db .
docker run -p 5432:5432 -v pg_data:/var/lib/postgresql/data conference-db
```
The database will be available at port 5432. For persistent storage across container restarts,
mount a volume to /var/lib/postgresql/data as shown above.

### Schema
The database initializes with a `conference_categories` table containing the list of categories to scrape.
For each category, the scraper creates two tables:
- `raw_<category>`: Unprocessed data directly from WikiCFP
- `cleaned_<category>`: Processed data with parsed dates and geocoded locations

Cleaned tables include columns for conference name, abbreviation, location, dates, coordinates,
and CFP deadline.

### Configuration
Database credentials are set via environment variables in the Dockerfile. For production deployments,
these should be overridden with secure values.
