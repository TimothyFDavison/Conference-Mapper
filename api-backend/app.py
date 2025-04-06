# backend/app.py
import time

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional

import config

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://conference-mapper.com"}})


def get_db_connection():
    conn = psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )
    return conn

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """
    Return a list of category names.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
    try:
        tables = [
            x["table_name"].split("cleaned_")[1].replace("_", " ").title()
                  for x in cur.fetchall() if "cleaned" in x["table_name"]
        ]
        tables.sort()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(tables)


class ConferenceQuery(BaseModel):
    categories: Optional[list] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    open_cfp: Optional[bool] = None

@app.route('/api/markers', methods=['POST'])
def get_markers():
    """
    Return data based on query parameters.
    Filters conferences based on:
    - Selected categories
    - Date range
    - CFP status (open/closed based on current date)
    """
    data = request.get_json()
    categories = data.get('categories') or None
    start_date = data.get('start_date') or None
    end_date = data.get('end_date') or None
    open_cfp = data.get('open_cfp') or None
    current_date = datetime.now()

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Build query based on input parameters
    queries = []
    if categories:
        for category in categories:
            table = f"{config.CLEANED_OUTPUT_TABLE}_{category['value'].lower().replace(' ', '_')}"
            query = f"SELECT *, CASE WHEN cfp::timestamp > NOW() THEN false ELSE true END as past_submission_date FROM {table} WHERE 1=1"
            
            if start_date:
                start_date_obj = datetime.strptime(start_date.rstrip("Z"), '%Y-%m-%dT%H:%M:%S.%f')
                query += f" AND start_date >= '{start_date_obj}'"
            if end_date:
                end_date_obj = datetime.strptime(end_date.rstrip("Z"), '%Y-%m-%dT%H:%M:%S.%f')
                query += f" AND end_date <= '{end_date_obj}'"
            if open_cfp:
                query += f" AND cfp::timestamp > NOW()"

            queries.append(query)
    else:
        return jsonify([])

    # Retrieve the data
    full_query = " UNION ALL ".join(queries)
    cur.execute(full_query)
    markers = cur.fetchall()

    # Remove duplicates, i.e. conferences listed in multiple tables
    seen = set()
    unique = []
    for marker in markers:
        if marker['name'] not in seen:
            seen.add(marker['name'])
            unique.append(marker)

    cur.close()
    conn.close()
    return jsonify(unique)


if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=True, )
