import os

# API parameters
HOST = '0.0.0.0'
PORT = 5000

# Database parameters
DB_NAME = "conference_mapper"
DB_USER = "malevolentelk"
DB_PASSWORD = "malevolentelk"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = "5432"

CATEGORIES_TABLE = "conference_categories"
GEOLOCATION_TABLE = "geolocation_mapping"
RAW_OUTPUT_TABLE = "scraped_conferences"
CLEANED_OUTPUT_TABLE = "scraped_conferences_cleaned"

# Scraper parameters
SCRAPER_NAME = "wikicfp_scraper"
SCRAPER_DOMAIN = "wikicfp.com"
START_URL = "http://www.wikicfp.com/cfp/call?conference={}"
PAGE_COUNT_MAXIMUM = 20

# Scraper categories from WikiCFP
CATEGORIES = [
    'artificial intelligence',
    'machine learning',
    'communications',
    'image processing',
    'computer science',
    'medicine',
    'medical'
]
