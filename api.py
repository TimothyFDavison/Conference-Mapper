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

class ConferenceQuery(BaseModel):
    categories: Optional[list] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    past_cfp_deadline: Optional[bool] = None

@app.route('/api/markers', methods=['GET'])
def get_markers():
    """
    Return data based on query parameters.
    """
    categories = request.args.getlist('categories') or None
    start_date = request.args.get('start_date', type=str) or None
    end_date = request.args.get('end_date', type=str) or None
    past_cfp_deadline = request.args.get('past_cfp_deadline', type=bool) or None

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Build query based on input parameters
    if categories:
        tables = ", ".join([f"{config.CLEANED_OUTPUT_TABLE}_{x.replace(' ', '_')}" for x in categories])
    else:
        tables = f"{config.CLEANED_OUTPUT_TABLE}_artificial_intelligence"
    base_query = f"SELECT * FROM {tables} WHERE 1=1"
    if start_date:
        base_query += f" AND start_date >= {start_date}"
    if end_date:
        base_query += f" AND end_date <= {end_date}"
    if past_cfp_deadline:
        base_query += f" AND past_submission_date == {past_cfp_deadline}"

    # Execute query
    cur.execute(base_query)
    markers = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(markers)


if __name__ == '__main__':
    app.run(debug=True)
