import pytest
from datetime import date, timedelta
import services


class TestFormatDate:
    def test_iso_to_br(self):
        assert services.format_date("2025-12-25") == "25/12/2025"

    def test_none_returns_empty(self):
        assert services.format_date(None) == ""
        assert services.format_date("") == ""

    def test_invalid_returns_itself(self):
        assert services.format_date("invalid") == "invalid"


class TestParseDateBr:
    def test_valid(self):
        assert services.parse_date_br("25/12/2025") == "2025-12-25"

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            services.parse_date_br("25-12-2025")

    def test_none_returns_none(self):
        assert services.parse_date_br(None) is None


class TestAddBook:
    def test_add_and_list(self):
        services.add_book("Título", "Autor", "Cat", 2020, "001")
        books = services.list_books()
        assert len(books) == 1
        assert books[0]["title"] == "Título"
        assert books[0]["author"] == "Autor"
        assert books[0]["code"] == "001"

    def test_optional_fields_none(self):
        services.add_book("T", "A")
        book = services.list_books()[0]
        assert book["category"] is None
        assert book["year"] is None
        assert book["code"] is None


class TestEditBook:
    def test_edit_persists(self):
        services.add_book("Old", "Author")
        book_id = services.list_books()[0]["id"]
        services.edit_book(book_id, "New", "New Author", "NewCat", 2024, "X1")
        book = services.get_book(book_id)
        assert book["title"] == "New"
        assert book["author"] == "New Author"
        assert book["category"] == "NewCat"


class TestRemoveBook:
    def test_removes_book_and_loans(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        services.loan_book(book_id, "Pessoa", None, "e@x.com")
        services.remove_book(book_id)
        assert services.get_book(book_id) is None
        assert services.loan_history(book_id) == []


class TestGetBook:
    def test_existing(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        assert services.get_book(book_id)["title"] == "T"

    def test_not_found(self):
        assert services.get_book(9999) is None


class TestLoanBook:
    def test_loan_sets_unavailable(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        services.loan_book(book_id, "Pessoa", "2025-12-31", "p@x.com")
        book = services.get_book(book_id)
        assert book["available"] == 0

    def test_loan_already_loaned_raises(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        services.loan_book(book_id, "P1")
        with pytest.raises(ValueError, match="já está alugado"):
            services.loan_book(book_id, "P2")

    def test_loan_not_found_raises(self):
        with pytest.raises(ValueError, match="não encontrado"):
            services.loan_book(9999, "P")

    def test_email_persisted(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        services.loan_book(book_id, "P", None, "test@x.com")
        loan = services.active_loan(book_id)
        assert loan["email"] == "test@x.com"


class TestReturnBook:
    def test_return_sets_available(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        services.loan_book(book_id, "P")
        services.return_book(book_id)
        book = services.get_book(book_id)
        assert book["available"] == 1

    def test_return_date_filled(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        services.loan_book(book_id, "P")
        services.return_book(book_id)
        history = services.loan_history(book_id)
        assert history[0]["return_date"] is not None


class TestSearchBooks:
    def test_search_by_title(self):
        services.add_book("Dom Casmurro", "Machado")
        services.add_book("Outro", "Outro")
        results = services.search_books("Casmurro")
        assert len(results) == 1

    def test_search_by_author(self):
        services.add_book("T", "Machado de Assis")
        results = services.search_books("Machado")
        assert len(results) == 1

    def test_search_no_result(self):
        services.add_book("T", "A")
        assert services.search_books("inexistente") == []


class TestFilterByCategory:
    def test_filter(self):
        services.add_book("T1", "A", "Romance")
        services.add_book("T2", "A", "Conto")
        results = services.filter_by_category("Romance")
        assert len(results) == 1
        assert results[0]["title"] == "T1"


class TestListCategories:
    def test_distinct(self):
        services.add_book("T1", "A", "Romance")
        services.add_book("T2", "A", "Romance")
        services.add_book("T3", "A", "Conto")
        cats = services.list_categories()
        assert sorted(cats) == ["Conto", "Romance"]


class TestActiveLoan:
    def test_active(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        services.loan_book(book_id, "P", None, "p@x.com")
        loan = services.active_loan(book_id)
        assert loan["person"] == "P"
        assert loan["email"] == "p@x.com"

    def test_no_active(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        assert services.active_loan(book_id) is None


class TestIsOverdue:
    def test_overdue(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        past = (date.today() - timedelta(days=5)).isoformat()
        services.loan_book(book_id, "P", past)
        assert services.is_overdue(book_id) is True

    def test_not_overdue(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        future = (date.today() + timedelta(days=5)).isoformat()
        services.loan_book(book_id, "P", future)
        assert services.is_overdue(book_id) is False

    def test_no_deadline(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        services.loan_book(book_id, "P")
        assert services.is_overdue(book_id) is False


class TestOverdueLoans:
    def test_returns_overdue_with_email(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        past = (date.today() - timedelta(days=3)).isoformat()
        services.loan_book(book_id, "P", past, "p@x.com")
        overdue = services.overdue_loans()
        assert len(overdue) == 1
        assert overdue[0]["email"] == "p@x.com"
        assert overdue[0]["title"] == "T"

    def test_future_not_in_overdue(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        future = (date.today() + timedelta(days=10)).isoformat()
        services.loan_book(book_id, "P", future)
        assert services.overdue_loans() == []


class TestTopLoaned:
    def test_ranking(self):
        services.add_book("T1", "A")
        services.add_book("T2", "A")
        b1 = services.list_books()[0]["id"]
        b2 = services.list_books()[1]["id"]
        services.loan_book(b1, "P1")
        services.return_book(b1)
        services.loan_book(b1, "P2")
        services.return_book(b1)
        services.loan_book(b2, "P3")
        services.return_book(b2)
        top = services.top_loaned_books()
        assert top[0]["title"] == "T1"
        assert top[0]["total"] == 2


class TestTopBorrowers:
    def test_ranking(self):
        services.add_book("T1", "A")
        services.add_book("T2", "A")
        b1 = services.list_books()[0]["id"]
        b2 = services.list_books()[1]["id"]
        services.loan_book(b1, "Ana")
        services.return_book(b1)
        services.loan_book(b2, "Ana")
        services.return_book(b2)
        services.loan_book(b1, "Bob")
        services.return_book(b1)
        top = services.top_borrowers()
        assert top[0]["person"] == "Ana"
        assert top[0]["total"] == 2


class TestRenewLoan:
    def test_renew_updates_deadline(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        services.loan_book(book_id, "P", "2025-01-01")
        services.renew_loan(book_id, "2025-06-01")
        loan = services.active_loan(book_id)
        assert loan["deadline_date"] == "2025-06-01"
        assert loan["notified_at"] is None  # reset

    def test_renew_no_active_raises(self):
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        with pytest.raises(ValueError):
            services.renew_loan(book_id, "2025-06-01")


class TestDashboardStats:
    def test_stats(self):
        services.add_book("T1", "A")
        services.add_book("T2", "A")
        b1 = services.list_books()[0]["id"]
        services.loan_book(b1, "P", "2020-01-01")
        stats = services.dashboard_stats()
        assert stats["total"] == 2
        assert stats["available"] == 1
        assert stats["loaned"] == 1
        assert stats["overdue"] == 1


class TestStudents:
    def test_add_and_list(self):
        services.add_student("Ana", "ana@x.com")
        students = services.list_students()
        assert len(students) == 1
        assert students[0]["name"] == "Ana"
        assert students[0]["email"] == "ana@x.com"

    def test_edit(self):
        services.add_student("Ana", "ana@x.com")
        sid = services.list_students()[0]["id"]
        services.edit_student(sid, "Ana S.", "ana2@x.com")
        s = services.list_students()[0]
        assert s["name"] == "Ana S."
        assert s["email"] == "ana2@x.com"

    def test_remove(self):
        services.add_student("Ana")
        sid = services.list_students()[0]["id"]
        services.remove_student(sid)
        assert services.list_students() == []

    def test_search(self):
        services.add_student("Ana", "ana@x.com")
        services.add_student("Bob")
        assert len(services.search_students("Ana")) == 1
        assert len(services.search_students("bob")) == 1


class TestValidateEmail:
    def test_valid(self):
        assert services.validate_email("test@example.com") is True

    def test_invalid(self):
        assert services.validate_email("notanemail") is False

    def test_none_is_ok(self):
        assert services.validate_email(None) is True
        assert services.validate_email("") is True
