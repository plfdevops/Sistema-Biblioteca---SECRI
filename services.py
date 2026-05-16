from database import get_connection
from datetime import date, timedelta


def add_book(title, author, category=None, year=None, code=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO books (title, author, category, year, code) VALUES (?, ?, ?, ?, ?)",
        (title, author, category or None, year or None, code or None),
    )
    conn.commit()
    conn.close()


def remove_book(book_id):
    conn = get_connection()
    conn.execute("DELETE FROM loans WHERE book_id = ?", (book_id,))
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()


def edit_book(book_id, title, author, category=None, year=None, code=None):
    conn = get_connection()
    conn.execute(
        "UPDATE books SET title = ?, author = ?, category = ?, year = ?, code = ? WHERE id = ?",
        (title, author, category or None, year or None, code or None, book_id),
    )
    conn.commit()
    conn.close()


def get_book(book_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def loan_book(book_id, person, deadline_days=None):
    conn = get_connection()
    book = conn.execute("SELECT available FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        conn.close()
        raise ValueError("Livro nao encontrado")
    if not book["available"]:
        conn.close()
        raise ValueError("Livro ja esta alugado")
    conn.execute(
        "INSERT INTO loans (book_id, person, loan_date, deadline_days) VALUES (?, ?, ?, ?)",
        (book_id, person, date.today().isoformat(), deadline_days),
    )
    conn.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()


def return_book(book_id):
    conn = get_connection()
    conn.execute(
        "UPDATE loans SET return_date = ? WHERE book_id = ? AND return_date IS NULL",
        (date.today().isoformat(), book_id),
    )
    conn.execute("UPDATE books SET available = 1 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()


def list_books():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_books(term):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR category LIKE ? ORDER BY title",
        (f"%{term}%", f"%{term}%", f"%{term}%"),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def filter_by_category(category):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM books WHERE category = ? ORDER BY title", (category,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_categories():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL ORDER BY category").fetchall()
    conn.close()
    return [r["category"] for r in rows]


def loan_history(book_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM loans WHERE book_id = ? ORDER BY loan_date DESC",
        (book_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def active_loan(book_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM loans WHERE book_id = ? AND return_date IS NULL",
        (book_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def is_overdue(book_id):
    loan = active_loan(book_id)
    if not loan or not loan["deadline_days"]:
        return False
    loan_date = date.fromisoformat(loan["loan_date"])
    deadline = loan_date + timedelta(days=loan["deadline_days"])
    return date.today() > deadline
