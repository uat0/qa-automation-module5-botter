"""Reference validators for the test basis; these are not DemoQA source code."""
import re
from datetime import date


def validate_name(value: str) -> bool:
    value = value.strip()
    return bool(value) and all(ch.isalpha() or ch in " -" for ch in value)


def validate_email(value: str) -> bool:
    """Optional, simplified application email contract; not full RFC 5322."""
    if not value:
        return True
    if value.count("@") != 1:
        return False
    local, domain = value.split("@")
    if not local or local.startswith(".") or local.endswith(".") or ".." in local:
        return False
    if re.fullmatch(r"[A-Za-z0-9_.+\-]+", local) is None:
        return False
    labels = domain.split(".")
    if len(labels) < 2 or re.fullmatch(r"[A-Za-z]{2,63}", labels[-1]) is None:
        return False
    return all(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?", label) is not None for label in labels[:-1])


def validate_mobile(value: str) -> bool:
    return len(value) == 10 and value.isascii() and value.isdigit()


def validate_age(value: int) -> bool:
    return 18 <= value <= 100


def validate_birth_date(value: date, today: date) -> bool:
    return date(1900, 1, 1) <= value <= today


def normalize_name(value: str) -> str:
    return " ".join(value.split())
