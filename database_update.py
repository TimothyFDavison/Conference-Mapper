from geopy.geocoders import Nominatim
import psycopg2

import config
from scraper import run_spider, WikiCFPSpider

# Establish database connection
conn = psycopg2.connect(
    dbname=config.DB_NAME, user=config.DB_USER, password=config.DB_PASSWORD, host=config.DB_HOST, port=config.DB_PORT
)
cur = conn.cursor()

# Persist geolocator to avoid reloading
geolocator = Nominatim(user_agent="geocoding_app")


def fetch_categories():
    """
    Retrieve the list of conference categories.
    Entries are returned in tuples of (ID, 'name')
    """
    cur.execute(f"SELECT * FROM {config.CATEGORIES_TABLE};")
    return cur.fetchall()

def scrape_categories(categories):
    """
    Iterate through the listed categories, use a Scrapy spider and pipeline to
    store collected data in postgres.

    Raw data is stored in tables as {data: <string>}, with table names following a convention
    of "scraped_conferences_<category-name>".
    """
    for category in categories:
        print(f"Scraping {category}...")
        run_spider(WikiCFPSpider, subpage=category)

def create_geolocation_cache():
    """
    Create geo table if it doesn't already exist.
    Add an index for O(1) lookups based on input location name.
    """
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.GEOLOCATION_TABLE} (
            location VARCHAR(255) PRIMARY KEY,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION
        );
    """)
    cur.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_city_btree ON {config.GEOLOCATION_TABLE} (location);
    """)
    conn.commit()

def geo_lookup(location_name):
    """
    If the location has been seen before, retrieve from the cache.
    Otherwise, query the geolocator for lat/long.
    """
    location_name = location_name.strip().lower()

    # Look up in location cache
    cur.execute(f"""
        SELECT * FROM {config.GEOLOCATION_TABLE} WHERE location = %s;
    """, (location_name,))
    result = cur.fetchone()
    if result:
        return result[1], result[2]

    # Handle some edge cases
    if location_name in {"virtual conference", "", "n/a"}:
        return None

    # If not in location cache, retrieve location and add it to the cache
    location = geolocator.geocode(location_name)
    if not location:
        return None

    # Store and return values
    cur.execute(f"""
        INSERT INTO {config.GEOLOCATION_TABLE} (location, lat, lon) 
        VALUES (%s, %s, %s);
    """, (location_name, location.latitude, location.longitude))
    conn.commit()
    return location.latitude, location.longitude

def clean_categories(categories):
    """
    Iterate through each table of raw scraped output. NB: entries come in pairs, i.e. two consecutive lines
    comprise one entry in the table (this is a byproduct of how the WikiCFP webpage is structured).

    For each academic conference category,
        1) Retrieve the raw data from its table
        2) Iterate through pairs of data lines and store conference entries
            - Extract conference identifier, name, date, location, and call-for-papers due date
        3) Supplement data with a geo lookup
            - If location is already known, use cached value
            - If location is unknown, use geopy's Nominatim package for a free lookup
        4) Store all values in a new table, named "scraped_conferences_cleaned_<category-name>".
    """
    for category in categories:
        # Retrieve raw data
        cur.execute(f'SELECT * FROM {config.RAW_OUTPUT_TABLE}_{category.replace(" ", "_")};')
        data = cur.fetchall()

        # Iterate through raw data in pairs of lines
        conferences = []
        past_submission_date = False  # Use WikiCFP's table break to store cfp deadline
        i = 0
        while i < len(data):
            print(i, len(data))
            entry = data[i][1].split("||||")
            if len(entry) <= 1:  # WikiCFP table break after which deadlines for cfp are past
                i += 1
                past_submission_date = True
                continue
            entry2 = data[i+1][1].split("||||")

            # Geo lookup
            try:
                lat, long = geo_lookup(entry2[1])
            except Exception as e:  # currently skipping conferences without location data
                i += 2
                continue

            conference = {
                "abbreviation": entry[0],
                "name": entry[1],
                "date": entry2[0],
                "location": entry2[1],
                "cfp": entry2[2],
                "past_submission_date": past_submission_date,
                "lat": lat,
                "long": long
            }
            i += 2
            conferences.append(conference)


if __name__ == "__main__":
    # Initialize database if necessary
    create_geolocation_cache()

    # Retrieve categories
    categories = [x[1] for x in fetch_categories()][:2]
    scrape_categories(categories)

    # Clean data
    clean_categories(categories)