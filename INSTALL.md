### Installation

#### PostgreSQL
Install postgres, dependencies
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
pip install psycopg2
sudo -u postgres psql
```

Create database and users
```postgresql
CREATE DATABASE conference_mapper
CREATE USER malevolentelk WITH ENCRYPTED PASSWORD 'malevolentelk';
GRANT ALL PRIVILEGES ON DATABASE conference_mapper TO malevolentelk;
\q
```

Connect to database
```python
import psycopg2

# Database connection parameters
DB_NAME = "conference_mapper"
DB_USER = "malevolentelk"
DB_PASSWORD = "malevolentelk"
DB_HOST = "localhost"
DB_PORT = "5432"

# Establish the connection
conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
)
cur = conn.cursor()
```

Create a new table
```python
def create_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            age INT
        );
    """)
    conn.commit()
    print("Table created successfully.")

create_table()
```

Insert into the table
```python
def insert_user(name, age):
    cur.execute("INSERT INTO users (name, age) VALUES (%s, %s) RETURNING id;", (name, age))
    user_id = cur.fetchone()[0]
    conn.commit()
    print(f"User {name} inserted with ID {user_id}")

insert_user("Alice", 30)
insert_user("Bob", 25)
```

Retrieve data from the table
```python
def fetch_users():
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    for user in users:
        print(user)

fetch_users()
```
Close connection to database
```python
cur.close()
conn.close()
```
