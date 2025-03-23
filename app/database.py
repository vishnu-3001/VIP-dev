from psycopg2 import pool
import os

db_pool = None

def init_db():
    global db_pool
    if db_pool is None:
        db_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME")
        )
        print("Database pool initialized.")

def get_connection():
    if db_pool is None:
        raise Exception("Database pool not initialized. Call 'init_db()' first.")
    return db_pool.getconn()

def close_pool():
    global db_pool
    if db_pool:
        db_pool.closeall()
        db_pool = None
        print("Database pool closed.")
