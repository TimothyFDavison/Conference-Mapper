import os

# API parameters
HOST = '0.0.0.0'
PORT = 5000

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
