from datetime import datetime
from time import sleep

from geopy.geocoders import Nominatim
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

import config
from scraper import run_spider, WikiCFPSpider


# Persist geolocator to avoid reloading
geolocator = Nominatim(user_agent="geocoding_app")


def get_db_connection(retries=30, delay=2):
    for attempt in range(1, retries + 1):
        try:
            conn = psycopg2.connect(
                dbname=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                host=config.DB_HOST,
                port=config.DB_PORT
            )
            cur = conn.cursor()
            return conn, cur
            break
        except psycopg2.OperationalError as e:
            print(f"Attempt {attempt}/{retries}: Postgres not ready, waiting {delay} seconds...")
            sleep(delay)
    if not conn:
        raise Exception("Postgres did not become available after several attempts.")
    return conn, cur

def initialize_tables():
    """
    After two hours of wrestling with postgres' native Docker image and failing to get my init.sql script
    to deploy when/where I wanted it to, here's the nuclear option.
    """
    conn, cur = get_db_connection()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS conference_categories (
                    id SERIAL PRIMARY KEY,
                    category TEXT UNIQUE NOT NULL
                );
    """)
    values = sql.SQL(', ').join(
        sql.SQL("({})").format(sql.Literal(category))
        for category in config.CATEGORIES
    )

    insert_query = sql.SQL("""
                INSERT INTO conference_categories (category)
                VALUES {}
                ON CONFLICT (category) DO NOTHING;
            """).format(values)
    cur.execute(insert_query)

    conn.commit()
    cur.close()
    conn.close()

def fetch_categories():
    """
    Retrieve the list of conference categories.
    Entries are returned in tuples of (ID, 'name')
    """
    conn, cur = get_db_connection()
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
    conn, cur = get_db_connection()
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
    conn, cur = get_db_connection()
    location_name = location_name.strip().lower()

    # Look up in location cache
    cur.execute(f"""
        SELECT * FROM {config.GEOLOCATION_TABLE} WHERE location = %s;
    """, (location_name,))
    result = cur.fetchone()
    if result:
        return result[1], result[2]

    # Handle some edge cases
    if location_name in {"virtual conference", "", "n/a", "hybrid", "online", "publication"}:
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

def store_cleaned_conferences(conferences, category):
    """
    Create a table for cleaned data by category, if not exists.
    Table naming convention, "scraped_conferences_cleaned_<category-name>".
    """
    conn, cur = get_db_connection()
    table_name = f'{config.CLEANED_OUTPUT_TABLE}_{category.replace(" ", "_")}'
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            abbreviation TEXT,
            name TEXT,
            dates TEXT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            location TEXT,
            cfp TEXT, 
            past_submission_date BOOLEAN,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION
            
        );
    """)
    conn.commit()

    # Add to database using insert_many for efficiency
    insert_query = sql.SQL(f"""
        INSERT INTO {table_name} 
        (abbreviation, name, dates, start_date, end_date, location, cfp, 
        past_submission_date, lat, lon)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """)
    data_tuples = [
        (
            conf["abbreviation"], conf["name"], conf["dates"], conf["start_date"],
            conf["end_date"], conf["location"], conf["cfp"], conf["past_submission_date"],
            conf["lat"], conf["long"]
        )
        for conf in conferences
    ]
    if data_tuples:
        cur.executemany(insert_query, data_tuples)
    conn.commit()

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
    conn, cur = get_db_connection()
    for category in categories:
        print(f"Cleaning {category}...")
        # Retrieve raw data
        cur.execute(f'SELECT * FROM {config.RAW_OUTPUT_TABLE}_{category.replace(" ", "_")};')
        data = cur.fetchall()

        # Iterate through raw data in pairs of lines
        conferences = []
        past_submission_date = False  # Use WikiCFP's table break to store cfp deadline
        i = 0
        while i < len(data):
            entry = data[i][1].split("||||")
            if len(entry) <= 1:  # WikiCFP table break after which deadlines for cfp are past
                i += 1
                past_submission_date = True
                continue
            try:
                entry2 = data[i+1][1].split("||||")
            except Exception as e:
                print("Encountered an error while cleaning {category}.")
                print(f"Line: {data[i]}")
                print(f"Values: i={i}, len(data)={len(data)}")
                print(e)
                break
            # Geo lookup
            try:
                lat, long = geo_lookup(entry2[1])
            except Exception as e:  # currently skipping conferences without location data
                i += 2
                continue

            # Date splitter
            try:
                start_str, end_str = entry2[0].split(" - ")
                start_date = datetime.strptime(start_str, "%b %d, %Y")
                end_date = datetime.strptime(end_str, "%b %d, %Y")
            except:
                start_date = None
                end_date = None

            conference = {
                "abbreviation": entry[0],
                "name": entry[1],
                "dates": entry2[0],
                "start_date": start_date,
                "end_date": end_date,
                "location": entry2[1],
                "cfp": entry2[2],
                "past_submission_date": past_submission_date,
                "lat": lat,
                "long": long
            }
            i += 2
            conferences.append(conference)
        store_cleaned_conferences(conferences, category)

def drop_duplicates(categories, column="name"):
    """
    Iterate over all tables in the database. Remove rows with duplicate "name" entries.
    """
    conn, cur = get_db_connection()
    for category in categories:
        print(f"Dropping duplicate entries from {category}...")
        table = f'{config.RAW_OUTPUT_TABLE}_{category.replace(" ", "_")}'
        query = f"""
            WITH cte AS (
                SELECT 
                    ctid, 
                    ROW_NUMBER() OVER (PARTITION BY '{column}' ORDER BY ctid) AS rnk
                FROM {table}
            )
            DELETE FROM {table}
            WHERE ctid IN (
                SELECT ctid FROM cte WHERE rnk > 1
            );
            """
        cur.execute(query)
    conn.commit()


if __name__ == "__main__":
    # Initialize database if necessary
    initialize_tables()
    create_geolocation_cache()

    # Retrieve categories
    categories = [x[1] for x in fetch_categories()]
    scrape_categories(categories)

    # Clean data
    clean_categories(categories)

    # Drop duplicates
    drop_duplicates(categories)
