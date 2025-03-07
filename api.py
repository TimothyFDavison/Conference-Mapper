# backend/app.py
from flask import Flask, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_cors import CORS

import config

app = Flask(__name__)
CORS(app)


def get_db_connection():
    conn = psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )
    return conn


@app.route('/api/markers', methods=['GET'])
def get_markers():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT lat, lon, abbreviation, name, dates, location, cfp "
                "FROM scraped_conferences_cleaned_artificial_intelligence")
    markers = cur.fetchall()
    cur.close()
    conn.close()

    # Return a list of dictionaries as JSON
    print(jsonify(markers))
    return jsonify(markers)


if __name__ == '__main__':
    app.run(debug=True)
