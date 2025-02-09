import psycopg2
from psycopg2 import pool
import os

# Read environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
max_conn=os.getenv("DB_POOL_MAX")
min_conn=os.getenv("DB_POOL_MIN")
db_pool = None

def init_db():
    global db_pool
    if not db_pool:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=min_conn,
            maxconn=max_conn,  
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        print("Database connection pool created.")

def get_connection():
    if not db_pool:
        raise Exception("Database pool not initialized. Call 'init_db()' first.")
    return db_pool.getconn()

def release_connection(conn):
    if db_pool:
        db_pool.putconn(conn)

def close_pool():
    if db_pool:
        db_pool.closeall()
        print("Database connection pool closed.")
