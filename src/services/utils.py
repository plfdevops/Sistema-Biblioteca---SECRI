import re
from datetime import date


def format_date(iso_date):
    if not iso_date:
        return ""
    try:
        d = date.fromisoformat(iso_date)
        return d.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return iso_date


def parse_date_br(date_str, must_be_future=False):
    if not date_str:
        return None
    parts = date_str.strip().split("/")
    if len(parts) != 3:
        raise ValueError("Formato inválido. Use dd/mm/aaaa")
    d, m, y = parts
    iso = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    try:
        parsed = date.fromisoformat(iso)
    except ValueError:
        raise ValueError("Data inválida")
    if must_be_future and parsed <= date.today():
        raise ValueError("A data deve ser futura")
    return iso


def validate_email(email):
    if not email:
        return True
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))
