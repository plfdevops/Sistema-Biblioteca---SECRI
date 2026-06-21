import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "biblioteca.db"))


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT,
                year INTEGER,
                available INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                person TEXT NOT NULL,
                loan_date TEXT NOT NULL,
                return_date TEXT,
                deadline_days INTEGER,
                deadline_date TEXT,
                FOREIGN KEY (book_id) REFERENCES books(id)
            );

            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                turma TEXT
            );
        """)
        for col in ("deadline_date TEXT", "email TEXT", "notified_at TEXT"):
            try:
                conn.execute(f"ALTER TABLE loans ADD COLUMN {col}")
            except Exception:
                pass
