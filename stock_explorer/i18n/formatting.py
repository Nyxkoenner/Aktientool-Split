from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd

from .translations import normalize_language


def _localized_number(text: str, language: str) -> str:
    if normalize_language(language) != "de":
        return text
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def format_number(value: Any, decimals: int = 2, language: str = "de") -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "–"
    return _localized_number(f"{float(numeric):,.{decimals}f}", language)


def format_percent(
    value: Any,
    decimals: int = 1,
    language: str = "de",
    *,
    signed: bool = False,
) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "–"
    sign = "+" if signed and float(numeric) > 0 else ""
    return f"{sign}{format_number(numeric, decimals, language)} %"


def format_currency(value: Any, currency: str = "EUR", decimals: int = 2, language: str = "de") -> str:
    formatted = format_number(value, decimals, language)
    return "–" if formatted == "–" else f"{formatted} {currency}"


def format_date(value: Any, language: str = "de") -> str:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return "–"
    timestamp = parsed.to_pydatetime() if hasattr(parsed, "to_pydatetime") else parsed
    if isinstance(timestamp, (datetime, date)):
        return timestamp.strftime("%d.%m.%Y" if normalize_language(language) == "de" else "%Y-%m-%d")
    return str(value)
