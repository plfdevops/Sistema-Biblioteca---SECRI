from database import get_db


def add_book(title, author, category=None, year=None, code=None):
    with get_db() as conn:
        conn.execute("INSERT INTO books (title, author, category, year, code) VALUES (?, ?, ?, ?, ?)",
                     (title, author, category or None, year or None, code or None))


def remove_book(book_id):
    with get_db() as conn:
        conn.execute("DELETE FROM loans WHERE book_id = ?", (book_id,))
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))


def edit_book(book_id, title, author, category=None, year=None, code=None):
    with get_db() as conn:
        conn.execute("UPDATE books SET title=?, author=?, category=?, year=?, code=? WHERE id=?",
                     (title, author, category or None, year or None, code or None, book_id))


def get_book(book_id):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
        return dict(row) if row else None


def list_books():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
        return [dict(r) for r in rows]


def search_books(term):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR category LIKE ? ORDER BY title",
                            (f"%{term}%", f"%{term}%", f"%{term}%")).fetchall()
        return [dict(r) for r in rows]


def filter_by_category(category):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM books WHERE category = ? ORDER BY title", (category,)).fetchall()
        return [dict(r) for r in rows]


def list_categories():
    with get_db() as conn:
        rows = conn.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL ORDER BY category").fetchall()
        return [r["category"] for r in rows]
