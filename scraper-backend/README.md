# Scraper Backend
A Scrapy-based web scraper that pulls conference data from WikiCFP. The scraper runs on a cron schedule,
fetching conference listings by category and storing them in the PostgreSQL database after cleaning
and geocoding.

### Installation
The scraper runs inside a Docker container with cron for scheduling. To build and run independently,
```bash
docker build -t conference-scraper .
docker run -e DB_HOST=localhost conference-scraper
```
The scraper will run immediately on container startup and then nightly at midnight. Note that the
database must be running and accessible; see the main README for full-system deployment.

### How It Works
1. The cron job triggers database_update.py on startup and nightly
2. For each category defined in the database, a Scrapy spider crawls WikiCFP
3. Raw conference data is passed through a pipeline that cleans and geocodes entries
4. Cleaned data is written to category-specific tables in PostgreSQL

### Configuration
Scraper settings are defined in config.py, including:
- `PAGE_COUNT_MAXIMUM`: Number of pages to crawl per category
- `START_URL`: WikiCFP URL template for category pages
- Database connection parameters (overridable via environment variables)

### Structure
```
scraper.py              # Scrapy spider definition
database_update.py      # Orchestration script for running scrapes
scraper_pipelines/      # Scrapy pipelines for data processing
scraper.cron            # Cron schedule definition
```

### Notes
Web scraping is inherently brittle. If WikiCFP changes their page structure, the spider's XPath
selectors may need updating. Check /var/log/cron.log inside the container for error output.
