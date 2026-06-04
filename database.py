import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "biblioteca.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
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
    """)
    try:
        conn.execute("ALTER TABLE loans ADD COLUMN deadline_date TEXT")
    except Exception:
        pass
    conn.commit()
    conn.close()
