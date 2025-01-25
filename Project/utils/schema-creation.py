import psycopg2
from psycopg2 import sql

# Connection details for the PostgreSQL instance
DB_HOST = "localhost"  # Replace with your host if different
DB_PORT = 5432
DB_USER = "vishnu"   # Replace with your PostgreSQL superuser
DB_PASSWORD = "vishnu"  # Replace with your PostgreSQL password

# Database name to be created
NEW_DB_NAME = "VIP"

# Schema creation SQL
SCHEMA_SQL = """
-- Users Table
CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);

-- Documents Table
CREATE TABLE documents (
    document_id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    content_vector DOUBLE PRECISION[] NOT NULL
);

-- Evaluations Table
CREATE TABLE IF NOT EXISTS Evaluations (
    evaluation_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    evaluation_type VARCHAR(50) CHECK (evaluation_type IN ('manual', 'llm')) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES Documents(document_id) ON DELETE CASCADE
);

-- Rubrics Table
CREATE TABLE IF NOT EXISTS Rubrics (
    rubric_id SERIAL PRIMARY KEY,
    rubric_name VARCHAR(255) UNIQUE NOT NULL
);

-- Scores Table
CREATE TABLE IF NOT EXISTS Scores (
    score_id SERIAL PRIMARY KEY,
    evaluation_id INTEGER NOT NULL,
    rubric_id INTEGER NOT NULL,
    score DECIMAL(5, 2) NOT NULL,
    user_comment TEXT,
    FOREIGN KEY (evaluation_id) REFERENCES Evaluations(evaluation_id) ON DELETE CASCADE,
    FOREIGN KEY (rubric_id) REFERENCES Rubrics(rubric_id) ON DELETE CASCADE
);
"""

def create_database_and_schema():
    try:
        # Step 1: Connect to the default 'postgres' database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname="postgres",  # Default maintenance database
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True  # Enable autocommit to allow database creation
        cursor = conn.cursor()

        # Step 2: Create the new database
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(NEW_DB_NAME)))
        print(f"Database '{NEW_DB_NAME}' created successfully.")

        # Step 3: Connect to the newly created database
        conn.close()
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=NEW_DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Step 4: Execute the schema creation SQL
        cursor.execute(SCHEMA_SQL)
        conn.commit()
        print("Schema created successfully in database 'VIP'.")

    except psycopg2.Error as e:
        print(f"Error: {e}")

    finally:
        # Close connections
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database_and_schema()
