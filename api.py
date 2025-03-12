# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date
from pydantic import BaseModel
from typing import Optional

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
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(tables)


class ConferenceQuery(BaseModel):
    categories: Optional[list] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    past_cfp_deadline: Optional[bool] = None

@app.route('/api/markers', methods=['POST'])
def get_markers():
    """
    Return data based on query parameters.
    """
    data = request.get_json()
    categories = data.get('categories') or None
    start_date = data.get('start_date') or None
    end_date = data.get('end_date') or None
    past_cfp_deadline = data.get('past_cfp_deadline') or None

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Build query based on input parameters
    queries = []
    if categories:
        for category in categories:
            table = f"{config.CLEANED_OUTPUT_TABLE}_{category['value'].lower().replace(' ', '_')}"
            query = f"SELECT * FROM {table} WHERE 1=1"
            if start_date:
                query += f" AND start_date >= {start_date}"
            if end_date:
                query += f" AND end_date <= {end_date}"
            if past_cfp_deadline:
                query += f" AND past_submission_date == {past_cfp_deadline}"

            queries.append(query)
    else:
        return jsonify([])

    full_query = " UNION ALL ".join(queries)
    cur.execute(full_query)
    markers = cur.fetchall()
    print(len(markers))
    cur.close()
    conn.close()
    return jsonify(markers)


if __name__ == '__main__':
    app.run(debug=True)
