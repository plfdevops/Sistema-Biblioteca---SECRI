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
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            categoria TEXT,
            ano INTEGER,
            disponivel INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livro_id INTEGER NOT NULL,
            pessoa TEXT NOT NULL,
            data_retirada TEXT NOT NULL,
            data_devolucao TEXT,
            prazo_dias INTEGER,
            FOREIGN KEY (livro_id) REFERENCES livros(id)
        );
    """)
    # Migrações
    try:
        conn.execute("ALTER TABLE emprestimos ADD COLUMN prazo_dias INTEGER")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE livros ADD COLUMN codigo TEXT")
    except Exception:
        pass
    conn.commit()
    conn.close()
