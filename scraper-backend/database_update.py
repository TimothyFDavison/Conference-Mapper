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

def truncate_raw_tables(categories):
    conn, cur = get_db_connection()
    for category in categories:
        table_name = f'{config.RAW_OUTPUT_TABLE}_{category.replace(" ", "_")}'
        query = sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE;").format(sql.Identifier(table_name))
        try:
            cur.execute(query)
            print(f"Table {table_name} truncated successfully.")
        except Exception as e:
            print(f"Error truncating table {table_name}: {e}")
            continue
    conn.commit()

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
            name TEXT UNIQUE NOT NULL,
            dates TEXT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            location TEXT,
            cfp TEXT, 
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION
        );
    """)
    conn.commit()

    # Add to database using insert_many for efficiency
    insert_query = sql.SQL(f"""
        INSERT INTO {table_name} 
        (abbreviation, name, dates, start_date, end_date, location, cfp, lat, lon)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (name) DO NOTHING;
    """)
    data_tuples = [
        (
            conf["abbreviation"], conf["name"], conf["dates"], conf["start_date"],
            conf["end_date"], conf["location"], conf["cfp"],
            conf["lat"], conf["long"]
        )
        for conf in conferences
    ]
    if data_tuples:
        cur.executemany(insert_query, data_tuples)
    conn.commit()

def clean_categories(categories):
    """
    Clean and store conference data, filtering out entries with incomplete information.
    Only conferences with valid location (with geo coordinates) and complete date information
    will be stored in the cleaned tables.
    """
    conn, cur = get_db_connection()
    for category in categories:
        print(f"\nProcessing {category}...")
        # Retrieve raw data
        table_name = f'{config.RAW_OUTPUT_TABLE}_{category.replace(" ", "_")}'
        cur.execute(sql.SQL("SELECT * FROM {};").format(sql.Identifier(table_name)))
        data = cur.fetchall()

        # Statistics tracking
        total_conferences = 0
        filtered_no_location = 0
        filtered_no_dates = 0
        accepted_conferences = 0

        # Iterate through raw data in pairs of lines
        conferences = []
        i = 0
        while i < len(data):
            entry = data[i][1].split("||||")
            if len(entry) <= 1:  # WikiCFP table break after which deadlines for cfp are past
                i += 1
                continue
                
            try:
                entry2 = data[i+1][1].split("||||")
            except Exception as e:
                print(f"Error processing entry at index {i}: {e}")
                break

            total_conferences += 1

            # Initialize conference data
            conference_data = {
                "abbreviation": entry[0],
                "name": entry[1],
                "dates": entry2[0],
                "location": entry2[1],
                "cfp": entry2[2],
                "start_date": None,
                "end_date": None,
                "lat": None,
                "long": None
            }

            # Geo lookup - skip if no valid coordinates
            try:
                coordinates = geo_lookup(entry2[1])
                if not coordinates:
                    print(f"Skipping conference '{entry[1]}': No valid coordinates for location '{entry2[1]}'")
                    filtered_no_location += 1
                    i += 2
                    continue
                conference_data["lat"], conference_data["long"] = coordinates
            except Exception as e:
                print(f"Skipping conference '{entry[1]}': Geo lookup failed for '{entry2[1]}': {e}")
                filtered_no_location += 1
                i += 2
                continue

            # Date parsing - skip if invalid dates
            try:
                start_str, end_str = entry2[0].split(" - ")
                conference_data["start_date"] = datetime.strptime(start_str, "%b %d, %Y")
                conference_data["end_date"] = datetime.strptime(end_str, "%b %d, %Y")
            except Exception as e:
                print(f"Skipping conference '{entry[1]}': Invalid date format '{entry2[0]}': {e}")
                filtered_no_dates += 1
                i += 2
                continue

            # Check submission date - just validate the format
            try:
                cfp_date = datetime.strptime(entry2[2], "%b %d, %Y")
            except Exception as e:
                print(f"Note: CFP date parsing failed for '{entry[1]}': {entry2[2]}: {e}")

            # If we got here, the conference has all required data
            conferences.append(conference_data)
            accepted_conferences += 1
            i += 2

        # Store the cleaned conferences
        if conferences:
            print(f"\nCategory {category} statistics:")
            print(f"Total conferences processed: {total_conferences}")
            print(f"Filtered due to missing location: {filtered_no_location}")
            print(f"Filtered due to invalid dates: {filtered_no_dates}")
            print(f"Accepted conferences: {accepted_conferences}")
            print(f"Storing {len(conferences)} cleaned conferences...")
            store_cleaned_conferences(conferences, category)
        else:
            print(f"\nNo valid conferences found for {category}")

    conn.close()

def drop_duplicates(categories, column="name"):
    """
    Iterate over all tables in the database. Remove rows with duplicate "name" entries.
    """
    conn, cur = get_db_connection()
    for category in categories:
        print(f"Dropping duplicate entries from {category}...")
        table = f'{config.CLEANED_OUTPUT_TABLE}_{category.replace(" ", "_")}'
        query = f"""
            WITH cte AS (
                SELECT 
                    ctid, 
                    ROW_NUMBER() OVER (PARTITION BY {column} ORDER BY ctid) AS rnk
                FROM {table}
            )
            DELETE FROM {table}
            WHERE ctid IN (
                SELECT ctid FROM cte WHERE rnk > 1
            );
            """
        try:
            cur.execute(query)
            conn.commit()
        except psycopg2.Error as e:
            print(f"Error executing query for {table}: {e}")
            continue



if __name__ == "__main__":
    # Initialize database if necessary
    initialize_tables()
    create_geolocation_cache()

    # Retrieve categories
    categories = [x[1] for x in fetch_categories()]

    # Drop duplicates - probably unnecessary, but running this preemptively in case
    # any one of the scraping or cleaning operations is interrupted (so that DB doesn't fill up
    # with duplicate entries)
    # drop_duplicates(categories)
    truncate_raw_tables(categories)

    # Scrape new data
    scrape_categories(categories)

    # Clean data
    clean_categories(categories)

    # Drop duplicates
    drop_duplicates(categories)
