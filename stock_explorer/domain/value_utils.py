"""Gemeinsam genutzte, von der Oberfläche unabhängige Datenhelfer."""

from __future__ import annotations

import re
from typing import Any, Iterable

import pandas as pd

GERMAN_INDEX_ALLOWED_SUFFIXES = (".DE", ".F", ".PA")
FINANCIAL_SECTOR_TERMS = {
    "financial",
    "bank",
    "insurance",
    "asset management",
    "capital markets",
}


def safe_float(value: Any) -> float | None:
    """Wandelt Werte robust in ``float`` um; unbrauchbare Werte werden ``None``."""
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if pd.notna(result) else None


def deduplicate_dataframe_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Entfernt doppelte Spalten und behält die zuletzt berechnete Variante."""
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return frame.copy()
    if not frame.columns.duplicated().any():
        return frame.copy()
    return frame.loc[:, ~frame.columns.duplicated(keep="last")].copy()


def merge_computed_columns(base: pd.DataFrame, computed: Any) -> pd.DataFrame:
    """Schreibt berechnete Spalten in einen Frame und überschreibt Platzhalter."""
    result = deduplicate_dataframe_columns(base)
    if computed is None:
        return result
    if isinstance(computed, pd.Series):
        computed = computed.to_frame()
    if not isinstance(computed, pd.DataFrame) or computed.empty:
        return result
    computed = deduplicate_dataframe_columns(computed)
    for column in computed.columns:
        result[column] = computed[column].reindex(result.index)
    return result


def display_text(value: Any, fallback: str = "–") -> str:
    """Bereitet Einzelwerte, Listen und versehentlich gelieferte Series fürs UI auf."""
    if isinstance(value, pd.Series):
        parts: list[str] = []
        for item in value.tolist():
            rendered = display_text(item, fallback="")
            if rendered and rendered not in parts:
                parts.append(rendered)
        return " | ".join(parts) if parts else fallback
    if isinstance(value, (list, tuple, set)):
        parts = [display_text(item, fallback="") for item in value]
        parts = [part for part in parts if part]
        return " | ".join(parts) if parts else fallback
    if isinstance(value, dict):
        if not value:
            return fallback
        return " | ".join(f"{key}: {display_text(item, fallback='')}" for key, item in value.items())
    if value is None:
        return fallback
    try:
        if pd.isna(value):
            return fallback
    except (TypeError, ValueError):
        pass
    text_value = str(value).strip()
    return text_value if text_value else fallback


def safe_session_date(
    value: Any,
    fallback: Any,
    min_date: Any = None,
    max_date: Any = None,
) -> Any:
    """Liest ein Datum aus einem Session-State robust ein."""
    try:
        fallback_date = pd.Timestamp(fallback).date()
    except Exception:
        fallback_date = fallback

    try:
        parsed = pd.to_datetime(value, errors="coerce")
        if pd.isna(parsed):
            return fallback_date
        result = pd.Timestamp(parsed).date()
    except Exception:
        return fallback_date

    if min_date is not None and result < min_date:
        return fallback_date
    if max_date is not None and result > max_date:
        return fallback_date
    return result


def to_percent(value: Any) -> float | None:
    """Normalisiert Dezimalquoten und bereits prozentuale Werte auf Prozent."""
    number = safe_float(value)
    if number is None:
        return None
    return number * 100.0 if abs(number) <= 1 else number


def clean_ticker(ticker: Any) -> str:
    """Normalisiert Yahoo-Ticker und entfernt Artefakte aus Webtabellen."""
    value = str(ticker or "").strip().upper()
    value = re.sub(r"\[.*?\]", "", value)
    value = value.replace("\xa0", " ").replace("–", "-").replace("—", "-")
    value = value.strip().lstrip("$")
    value = re.sub(r"\s+", "", value)
    return re.sub(r"[^A-Z0-9.\-]", "", value)


def is_probably_german_yahoo_symbol(symbol: str, exchange: str = "") -> bool:
    """Prüft, ob ein Yahoo-Suchtreffer zu einem deutschen Index plausibel ist."""
    symbol = clean_ticker(symbol)
    exchange = str(exchange or "").upper().strip()
    if not symbol:
        return False
    if symbol.endswith(GERMAN_INDEX_ALLOWED_SUFFIXES):
        return True
    german_exchanges = {
        "GER",
        "ETR",
        "EUX",
        "FRA",
        "STU",
        "MUN",
        "HAM",
        "HAN",
        "DUS",
        "BER",
    }
    return exchange in german_exchanges and "." not in symbol


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result.columns = [str(column).strip() for column in result.columns]
    return result


def find_col(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    """Findet Spalten auch bei leicht abweichender Benennung."""
    candidate_list = tuple(candidates)
    available = {str(column).lower(): str(column) for column in columns}
    for candidate in candidate_list:
        if candidate.lower() in available:
            return available[candidate.lower()]

    for column in columns:
        column_lower = str(column).lower()
        if any(candidate.lower() in column_lower for candidate in candidate_list):
            return str(column)
    return None


def format_number(value: Any, decimals: int = 2, suffix: str = "") -> str:
    """Formatiert Zahlen im deutschen Stil."""
    number = safe_float(value)
    if number is None:
        return "–"
    return f"{number:,.{decimals}f}{suffix}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percent(value: Any, decimals: int = 1, signed: bool = False) -> str:
    number = safe_float(value)
    if number is None:
        return "–"
    prefix = "+" if signed and number > 0 else ""
    return f"{prefix}{format_number(number, decimals)} %"


def format_eur(value: Any, decimals: int = 2, signed: bool = False) -> str:
    number = safe_float(value)
    if number is None:
        return "–"
    prefix = "+" if signed and number > 0 else ""
    return f"{prefix}{format_number(number, decimals)} EUR"


def human_market_cap(value: Any) -> str:
    number = safe_float(value)
    if number is None:
        return "–"
    absolute = abs(number)
    if absolute >= 1_000_000_000_000:
        return f"{format_number(number / 1_000_000_000_000, 1)} Bio."
    if absolute >= 1_000_000_000:
        return f"{format_number(number / 1_000_000_000, 1)} Mrd."
    if absolute >= 1_000_000:
        return f"{format_number(number / 1_000_000, 1)} Mio."
    return format_number(number, 0)


def is_financial_sector(sector: Any) -> bool:
    text = str(sector or "").lower()
    return any(term in text for term in FINANCIAL_SECTOR_TERMS)


def ensure_datetime_index(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result.index = pd.to_datetime(result.index, errors="coerce")
    result = result[~result.index.isna()]
    if getattr(result.index, "tz", None) is not None:
        result.index = result.index.tz_localize(None)
    return result.sort_index()


def empty_metrics_frame() -> pd.DataFrame:
    columns = [
        "name",
        "ticker_yahoo",
        "sector",
        "currency",
        "last_price",
        "change_1d",
        "change_5d",
        "change_1y",
        "total_return_1y",
        "vol_30d",
        "vol_1y",
        "max_drawdown_1y",
        "drawdown_3y_high_pct",
        "drawdown_5y_high_pct",
        "high_52w",
        "low_52w",
        "market_cap",
        "pe_ratio",
        "forward_pe",
        "pb_ratio",
        "ps_ratio",
        "ev_ebitda",
        "net_margin",
        "operating_margin",
        "roe",
        "roa",
        "dividend_yield",
        "dividend_per_share",
        "payout_ratio",
        "dividend_growth_5y",
        "dividend_frequency",
        "dividend_yield_5y_avg",
        "dividend_yield_vs_5y_avg_pct",
        "operating_cashflow",
        "free_cashflow",
        "shares_outstanding",
        "cashflow_dividend_coverage",
        "debt_to_equity",
        "net_debt_ebitda",
        "beta",
        "revenue_growth",
        "earnings_growth",
        "earnings_quarterly_growth",
        "gross_margin",
        "ebitda_margin",
        "current_ratio",
        "quick_ratio",
        "change_1m",
        "change_3m",
        "change_6m",
        "price_vs_sma50_pct",
        "price_vs_sma200_pct",
        "growth_score",
        "growth_coverage",
        "growth_components",
        "momentum_score",
        "momentum_coverage",
        "momentum_components",
        "safety_score",
        "safety_coverage",
        "safety_components",
        "data_updated_at",
    ]
    return pd.DataFrame(columns=columns)


__all__ = [
    "clean_ticker",
    "deduplicate_dataframe_columns",
    "display_text",
    "empty_metrics_frame",
    "ensure_datetime_index",
    "find_col",
    "format_eur",
    "format_number",
    "format_percent",
    "human_market_cap",
    "is_financial_sector",
    "is_probably_german_yahoo_symbol",
    "merge_computed_columns",
    "normalize_columns",
    "safe_float",
    "safe_session_date",
    "to_percent",
]
