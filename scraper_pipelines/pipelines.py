import psycopg2
from psycopg2 import sql

import config


class PostgreSQLPipeline:
    def open_spider(self, spider):
        """
        Establish a connection to the database.
        """
        self.conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
        )
        self.cur = self.conn.cursor()

        # Ensure table exists
        self.cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {config.RAW_OUTPUT_TABLE}_{spider.subpage} (
                id SERIAL PRIMARY KEY,
                data TEXT
            );
        """)
        self.conn.commit()

    def process_item(self, item, spider):
        """
        Insert each item into table.
        """
        data_value = item.get('data', None)
        sql_query = sql.SQL("""
            INSERT INTO {} (data) VALUES (%s);
        """).format(sql.Identifier(f"{config.RAW_OUTPUT_TABLE}_{spider.subpage}"))
        self.cur.execute(sql_query, (data_value,))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        """Runs when the spider finishes. Closes DB connection."""
        self.cur.close()
        self.conn.close()
