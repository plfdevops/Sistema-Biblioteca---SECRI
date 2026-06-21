import smtplib
import os
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from services import overdue_loans, format_date
from database import get_db


def _load_config():
    email = os.environ.get("SMTP_EMAIL")
    if not email:
        raise RuntimeError("SMTP_EMAIL não configurado. Defina as variáveis de ambiente.")
    return {
        "smtp": {
            "server": os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
            "port": int(os.environ.get("SMTP_PORT", "587")),
            "email": email,
            "password": os.environ.get("SMTP_PASSWORD", ""),
        },
        "notify_emails": [e.strip() for e in os.environ.get("NOTIFY_EMAILS", "").split(",") if e.strip()],
        "notify_cooldown_days": int(os.environ.get("NOTIFY_COOLDOWN_DAYS", "7")),
    }


def _send_email(smtp_cfg, to, subject, body):
    msg = MIMEMultipart()
    msg["From"] = smtp_cfg["email"]
    msg["To"] = to if isinstance(to, str) else ", ".join(to)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    server = smtplib.SMTP(smtp_cfg["server"], smtp_cfg["port"])
    server.starttls()
    server.login(smtp_cfg["email"], smtp_cfg["password"])
    recipients = [to] if isinstance(to, str) else to
    server.sendmail(smtp_cfg["email"], recipients, msg.as_string())
    server.quit()


def send_manager_notification():
    """Envia relatório consolidado de atrasos para os e-mails do gestor."""
    loans = overdue_loans()
    if not loans:
        return "Nenhum atraso encontrado."

    config = _load_config()
    recipients = config["notify_emails"]

    body = "Os seguintes livros estão com devolução atrasada:\n\n"
    for loan in loans:
        body += (f"- {loan['title']} | Pessoa: {loan['person']} | "
                 f"Devolver até: {format_date(loan['deadline_date'])} | "
                 f"Emprestado em: {format_date(loan['loan_date'])}\n")
    body += f"\nTotal de atrasos: {len(loans)}"

    _send_email(config["smtp"], recipients,
                f"[Biblioteca SECRI] {len(loans)} livro(s) com devolução atrasada", body)
    return f"E-mail enviado para {', '.join(recipients)} com {len(loans)} atraso(s)."


def send_student_notifications():
    """Envia e-mail individual para cada aluno com empréstimo atrasado (respeitando cooldown)."""
    loans = overdue_loans()
    if not loans:
        return 0

    config = _load_config()
    cooldown = config.get("notify_cooldown_days", 3)
    today = date.today()
    sent = 0

    for loan in loans:
        if not loan.get("email"):
            continue
        if loan.get("notified_at"):
            last = date.fromisoformat(loan["notified_at"])
            if (today - last).days < cooldown:
                continue

        body = (
            f"Olá {loan['person']},\n\n"
            f"O livro \"{loan['title']}\" emprestado em {format_date(loan['loan_date'])} "
            f"tinha prazo de devolução para {format_date(loan['deadline_date'])}.\n"
            f"Por favor, devolva o quanto antes na biblioteca.\n\n"
            f"Atenciosamente,\nBiblioteca SECRI"
        )

        try:
            _send_email(config["smtp"], loan["email"],
                        f"[Biblioteca SECRI] Devolução pendente - {loan['title']}", body)
            with get_db() as conn:
                conn.execute("UPDATE loans SET notified_at = ? WHERE id = ?",
                             (today.isoformat(), loan["id"]))
            sent += 1
        except Exception:
            pass  # Falha no envio: não marca notified_at, retry na próxima verificação

    return sent
