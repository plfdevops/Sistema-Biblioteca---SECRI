from database import get_db
from datetime import date


def loan_book(book_id, person, deadline_date=None, email=None):
    with get_db() as conn:
        book = conn.execute("SELECT available FROM books WHERE id = ?", (book_id,)).fetchone()
        if not book:
            raise ValueError("Livro não encontrado")
        if not book["available"]:
            raise ValueError("Livro já está alugado")
        conn.execute("INSERT INTO loans (book_id, person, loan_date, deadline_date, email) VALUES (?, ?, ?, ?, ?)",
                     (book_id, person, date.today().isoformat(), deadline_date, email or None))
        conn.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))


def return_book(book_id):
    with get_db() as conn:
        conn.execute("UPDATE loans SET return_date = ? WHERE book_id = ? AND return_date IS NULL",
                     (date.today().isoformat(), book_id))
        conn.execute("UPDATE books SET available = 1 WHERE id = ?", (book_id,))


def loan_history(book_id):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM loans WHERE book_id = ? ORDER BY loan_date DESC", (book_id,)).fetchall()
        return [dict(r) for r in rows]


def active_loan(book_id):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM loans WHERE book_id = ? AND return_date IS NULL", (book_id,)).fetchone()
        return dict(row) if row else None


def is_overdue(book_id):
    loan = active_loan(book_id)
    if not loan or not loan.get("deadline_date"):
        return False
    return date.today() > date.fromisoformat(loan["deadline_date"])


def renew_loan(book_id, new_deadline_date):
    with get_db() as conn:
        loan = conn.execute("SELECT id FROM loans WHERE book_id=? AND return_date IS NULL",
                            (book_id,)).fetchone()
        if not loan:
            raise ValueError("Nenhum empréstimo ativo para este livro")
        conn.execute("UPDATE loans SET deadline_date=?, notified_at=NULL WHERE id=?",
                     (new_deadline_date, loan["id"]))


def overdue_loans():
    with get_db() as conn:
        rows = conn.execute("""SELECT l.*, b.title FROM loans l JOIN books b ON l.book_id = b.id
            WHERE l.return_date IS NULL AND l.deadline_date IS NOT NULL AND l.deadline_date < ?""",
            (date.today().isoformat(),)).fetchall()
        return [dict(r) for r in rows]


def top_loaned_books(limit=10):
    with get_db() as conn:
        rows = conn.execute("""SELECT b.title, b.author, COUNT(l.id) as total
            FROM loans l JOIN books b ON l.book_id = b.id
            GROUP BY l.book_id ORDER BY total DESC LIMIT ?""", (limit,)).fetchall()
        return [dict(r) for r in rows]


def top_borrowers(limit=10):
    with get_db() as conn:
        rows = conn.execute("""SELECT person, COUNT(id) as total
            FROM loans GROUP BY person ORDER BY total DESC LIMIT ?""", (limit,)).fetchall()
        return [dict(r) for r in rows]
