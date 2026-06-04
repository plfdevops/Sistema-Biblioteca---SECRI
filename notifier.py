import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from services import overdue_loans, format_date

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def send_overdue_notification():
    loans = overdue_loans()
    if not loans:
        return "Nenhum atraso encontrado."

    config = load_config()
    smtp_cfg = config["smtp"]
    recipients = config["notify_emails"]

    body = "Os seguintes livros estão com devolução atrasada:\n\n"
    for loan in loans:
        body += f"- {loan['title']} | Pessoa: {loan['person']} | Devolver até: {format_date(loan['deadline_date'])} | Emprestado em: {format_date(loan['loan_date'])}\n"
    body += f"\nTotal de atrasos: {len(loans)}"

    msg = MIMEMultipart()
    msg["From"] = smtp_cfg["email"]
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = f"[Biblioteca SECRI] {len(loans)} livro(s) com devolução atrasada"
    msg.attach(MIMEText(body, "plain", "utf-8"))

    server = smtplib.SMTP(smtp_cfg["server"], smtp_cfg["port"])
    server.starttls()
    server.login(smtp_cfg["email"], smtp_cfg["password"])
    server.sendmail(smtp_cfg["email"], recipients, msg.as_string())
    server.quit()

    return f"E-mail enviado para {', '.join(recipients)} com {len(loans)} atraso(s)."
