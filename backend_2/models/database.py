import psycopg2
from psycopg2.extras import RealDictCursor
from models.config import settings

def get_db_connection():
    try:
        conn = psycopg2.connect(
            settings.DATABASE_URL,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise
