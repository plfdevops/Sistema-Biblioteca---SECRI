import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
import os
import services
import notifier


@pytest.fixture(autouse=True)
def smtp_env(monkeypatch):
    monkeypatch.setenv("SMTP_EMAIL", "test@test.com")
    monkeypatch.setenv("SMTP_PASSWORD", "pass")
    monkeypatch.setenv("SMTP_SERVER", "localhost")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("NOTIFY_EMAILS", "gestor@test.com")
    monkeypatch.setenv("NOTIFY_COOLDOWN_DAYS", "7")


class TestSendManagerNotification:
    def test_no_overdue_returns_message(self):
        result = notifier.send_manager_notification()
        assert "Nenhum atraso" in result

    @patch("notifier.smtplib.SMTP")
    def test_with_overdue_sends_email(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        past = (date.today() - timedelta(days=3)).isoformat()
        services.loan_book(book_id, "P", past, "p@x.com")

        result = notifier.send_manager_notification()
        assert "1 atraso" in result
        mock_server.sendmail.assert_called_once()


class TestSendStudentNotifications:
    @patch("notifier.smtplib.SMTP")
    def test_sends_to_student_with_email(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        past = (date.today() - timedelta(days=3)).isoformat()
        services.loan_book(book_id, "P", past, "aluno@x.com")

        sent = notifier.send_student_notifications()
        assert sent == 1
        mock_server.sendmail.assert_called_once()

    @patch("notifier.smtplib.SMTP")
    def test_skips_without_email(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        past = (date.today() - timedelta(days=3)).isoformat()
        services.loan_book(book_id, "P", past)  # sem email

        sent = notifier.send_student_notifications()
        assert sent == 0
        mock_server.sendmail.assert_not_called()

    @patch("notifier.smtplib.SMTP")
    def test_respects_cooldown(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        past = (date.today() - timedelta(days=10)).isoformat()
        services.loan_book(book_id, "P", past, "a@x.com")

        notifier.send_student_notifications()
        mock_server.sendmail.reset_mock()

        sent = notifier.send_student_notifications()
        assert sent == 0

    @patch("notifier.smtplib.SMTP")
    def test_smtp_failure_no_mark(self, mock_smtp):
        mock_server = MagicMock()
        mock_server.sendmail.side_effect = Exception("SMTP error")
        mock_smtp.return_value = mock_server
        services.add_book("T", "A")
        book_id = services.list_books()[0]["id"]
        past = (date.today() - timedelta(days=3)).isoformat()
        services.loan_book(book_id, "P", past, "a@x.com")

        sent = notifier.send_student_notifications()
        assert sent == 0
        loan = services.active_loan(book_id)
        assert loan["notified_at"] is None
