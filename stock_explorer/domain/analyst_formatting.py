"""Formatierungshelfer für Analystenschätzungen und Kursziele."""

from __future__ import annotations

import re
from typing import Any, Literal

import pandas as pd

from stock_explorer.domain.value_utils import format_number, format_percent, safe_float, to_percent

AnalystTableKind = Literal[
    "recommendations",
    "revenue",
    "earnings",
    "growth",
    "upgrades",
]

_COLUMN_LABELS = {
    "period": "Zeitraum",
    "avg": "Durchschnitt",
    "low": "Untere Schätzung",
    "high": "Obere Schätzung",
    "numberofanalysts": "Analysten",
    "yearagorevenue": "Umsatz Vorjahr",
    "yearagoeps": "Ergebnis je Aktie Vorjahr",
    "growth": "Wachstum",
    "currency": "Währung",
    "stock": "Aktie",
    "industry": "Branche",
    "sector": "Sektor",
    "index": "Index",
}

_REVENUE_AMOUNT_COLUMNS = {"avg", "low", "high", "yearagorevenue"}
_EARNINGS_AMOUNT_COLUMNS = {"avg", "low", "high", "yearagoeps"}
_ANALYST_COUNT_COLUMNS = {"numberofanalysts"}
_GROWTH_COLUMNS = {"growth", "stock", "industry", "sector", "index"}


def _normalized_column_name(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).strip().lower())


def normalize_currency(*values: Any) -> str:
    """Liefert den ersten plausiblen ISO-Währungscode ohne eine Währung zu erraten."""
    for value in values:
        text = str(value or "").strip().upper()
        if re.fullmatch(r"[A-Z]{3}", text):
            return text
    return ""


def _unit_suffix(currency: str, *, per_share: bool = False) -> str:
    normalized = normalize_currency(currency)
    if per_share:
        return f" {normalized}/Aktie" if normalized else " je Aktie"
    return f" {normalized}" if normalized else ""


def format_currency_amount(
    value: Any,
    currency: str = "",
    *,
    compact: bool = True,
    per_share: bool = False,
) -> str:
    """Formatiert Geldwerte mit skalierter Größenordnung und Währung."""
    number = safe_float(value)
    if number is None:
        return "–"

    divisor = 1.0
    scale = ""
    if compact:
        absolute = abs(number)
        if absolute >= 1_000_000_000_000:
            divisor, scale = 1_000_000_000_000.0, " Bio."
        elif absolute >= 1_000_000_000:
            divisor, scale = 1_000_000_000.0, " Mrd."
        elif absolute >= 1_000_000:
            divisor, scale = 1_000_000.0, " Mio."
        elif absolute >= 1_000:
            divisor, scale = 1_000.0, " Tsd."

    decimals = 1 if scale else 2
    rendered = format_number(number / divisor, decimals)
    return f"{rendered}{scale}{_unit_suffix(currency, per_share=per_share)}"


def analyst_table_unit_caption(kind: AnalystTableKind, currency: str = "") -> str:
    """Erklärt die Einheit der aktuell angezeigten Analystentabelle."""
    normalized = normalize_currency(currency)
    if kind == "revenue":
        currency_text = f" in {normalized}" if normalized else ""
        return f"Umsatzbeträge{currency_text}; große Werte werden als Tsd., Mio., Mrd. oder Bio. dargestellt."
    if kind == "earnings":
        currency_text = normalized or "Berichtswährung"
        return f"Ergebnis je Aktie in {currency_text}/Aktie; Wachstum in Prozent."
    if kind == "growth":
        return "Wachstumsangaben in Prozent."
    return ""


def _format_growth(value: Any) -> str:
    percentage = to_percent(value)
    return format_percent(percentage, 1, signed=True)


def _format_analyst_count(value: Any) -> str:
    number = safe_float(value)
    return "–" if number is None else format_number(number, 0)


def format_analyst_table(
    frame: pd.DataFrame,
    kind: AnalystTableKind,
    currency: str = "",
) -> pd.DataFrame:
    """Ergänzt Analystentabellen um verständliche Spaltennamen und Einheiten."""
    if frame is None or frame.empty:
        return pd.DataFrame()

    result = frame.copy()
    normalized_columns = {column: _normalized_column_name(column) for column in result.columns}

    for column, normalized in normalized_columns.items():
        if normalized in _ANALYST_COUNT_COLUMNS:
            result[column] = result[column].map(_format_analyst_count)
            continue

        if kind == "revenue" and normalized in _REVENUE_AMOUNT_COLUMNS:
            result[column] = result[column].map(
                lambda value: format_currency_amount(value, currency, compact=True)
            )
            continue

        if kind == "earnings" and normalized in _EARNINGS_AMOUNT_COLUMNS:
            result[column] = result[column].map(
                lambda value: format_currency_amount(
                    value,
                    currency,
                    compact=False,
                    per_share=True,
                )
            )
            continue

        if normalized == "growth" or (kind == "growth" and normalized in _GROWTH_COLUMNS):
            result[column] = result[column].map(_format_growth)
            continue

        if normalized == "currency":
            result[column] = result[column].map(lambda value: normalize_currency(value, currency) or "–")

    result = result.rename(
        columns={
            column: _COLUMN_LABELS.get(normalized, str(column))
            for column, normalized in normalized_columns.items()
        }
    )
    return result


__all__ = [
    "AnalystTableKind",
    "analyst_table_unit_caption",
    "format_analyst_table",
    "format_currency_amount",
    "normalize_currency",
]
