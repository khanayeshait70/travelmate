
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "feedback.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                place_name TEXT NOT NULL,
                rating INTEGER NOT NULL,
                review TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_feedback(place_name, rating, review):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO feedback (place_name, rating, review)
            VALUES (?, ?, ?)
        """, (place_name, int(rating), review))
        conn.commit()


def get_all_feedback():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, place_name, rating, review, created_at
            FROM feedback
            ORDER BY created_at DESC
        """).fetchall()


def get_feedback_count():
    with get_connection() as conn:
        result = conn.execute(
            "SELECT COUNT(*) FROM feedback"
        ).fetchone()
    return result[0]
