import os

# Database parameters
DB_NAME = "conference_mapper"
DB_USER = "REDACTED"
DB_PASSWORD = "REDACTED"
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
    'computer science',
    'machine learning',
    'engineering',
    'information technology',
    'education',
    'software engineering',
    'security',
    'data mining',
    'communications',
    'big data',
    'robotics',
    'cloud computing',
    'image processing',
    'signal processing',
    'computer vision',
    'multimedia',
    'humanities',
    'bioinformatics',
    'medicine',
    'medical',
    'health informatics',
    'social networks',
    'social media',
]
