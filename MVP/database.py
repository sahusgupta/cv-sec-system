import psycopg2
from psycopg2.extras import DictCursor
import os

# Pull DB credentials from environment variables or set them directly
DB_NAME = os.getenv("DB_NAME", "proctoring_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_connection():
    """
    Returns a psycopg2 connection to the PostgreSQL database.
    """
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

def create_tables():
    """
    Creates all necessary tables if they don't already exist.
    """
    table_creation_queries = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            role VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS exams (
            exam_id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            course_code VARCHAR(50) NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            CONSTRAINT fk_exam_creator
                FOREIGN KEY(created_by)
                REFERENCES users(user_id)
                ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS exam_sessions (
            session_id SERIAL PRIMARY KEY,
            exam_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            start_time TIMESTAMP NOT NULL DEFAULT NOW(),
            end_time TIMESTAMP,
            status VARCHAR(50) DEFAULT 'active',
            CONSTRAINT fk_exam_sessions_exam
                FOREIGN KEY(exam_id)
                REFERENCES exams(exam_id)
                ON DELETE CASCADE,
            CONSTRAINT fk_exam_sessions_student
                FOREIGN KEY(student_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS suspicious_events (
            event_id SERIAL PRIMARY KEY,
            session_id INTEGER NOT NULL,
            event_type VARCHAR(100) NOT NULL,
            confidence NUMERIC(5, 2),
            detected_at TIMESTAMP DEFAULT NOW(),
            CONSTRAINT fk_suspicious_session
                FOREIGN KEY(session_id)
                REFERENCES exam_sessions(session_id)
                ON DELETE CASCADE
        );
        """
    ]

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        for query in table_creation_queries:
            cur.execute(query)
        conn.commit()
    except Exception as e:
        print("Error creating tables:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
