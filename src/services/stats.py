from database import get_db
from datetime import date
from services.loans import overdue_loans


def dashboard_stats():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM books").fetchone()["c"]
        available = conn.execute("SELECT COUNT(*) as c FROM books WHERE available=1").fetchone()["c"]
        loaned = total - available
        overdue_count = len(overdue_loans())
        month_start = date.today().replace(day=1).isoformat()
        returns_month = conn.execute(
            "SELECT COUNT(*) as c FROM loans WHERE return_date >= ?", (month_start,)).fetchone()["c"]
        return {"total": total, "available": available, "loaned": loaned,
                "overdue": overdue_count, "returns_month": returns_month}
