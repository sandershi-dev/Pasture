# database/database.py

import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling, Error

# Load .env file
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST","localhost")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))

# Connection Pool Configuration
POOL_NAME = "main_pool"
POOL_SIZE = int(os.getenv("MYSQL_POOL_SIZE", 10))   # optional

# Create a connection pool at startup
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name=POOL_NAME,
        pool_size=POOL_SIZE,
        pool_reset_session=True,
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
    )
except Error as e:
    raise Exception(f"Failed to create MySQL pool: {e}")


def get_connection():
    """Get a pooled MySQL connection."""
    try:
        conn = connection_pool.get_connection()
        if conn.is_connected():
            return conn
        else:
            raise Exception("Connection returned from pool is not connected.")

    except Error as e:
        raise Exception(f"Failed to get pooled connection: {e}")
