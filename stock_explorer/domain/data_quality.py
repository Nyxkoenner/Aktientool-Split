from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass(frozen=True)
class HistoryQualityReport:
    score: int
    level: str
    observations: int
    start: pd.Timestamp | None
    end: pd.Timestamp | None
    years: float
    duplicate_rows: int
    invalid_rows: int
    nonpositive_rows: int
    missing_business_days: int
    missing_ratio: float
    latest_age_days: int | None
    issues: tuple[str, ...]


def _price_series(history: pd.DataFrame | pd.Series) -> pd.Series:
    if isinstance(history, pd.Series):
        return history.copy()
    if not isinstance(history, pd.DataFrame):
        raise TypeError("history must be a pandas Series or DataFrame")
    for candidate in ("Adj Close", "Close", "close", "price"):
        if candidate in history.columns:
            return history[candidate].copy()
    numeric = history.select_dtypes(include=["number"])
    return numeric.iloc[:, 0].copy() if not numeric.empty else pd.Series(dtype=float)


def assess_price_history(
    history: pd.DataFrame | pd.Series,
    *,
    as_of: pd.Timestamp | datetime | str | None = None,
) -> HistoryQualityReport:
    raw = _price_series(history)
    parsed_index = pd.to_datetime(raw.index, errors="coerce")
    invalid_index = int(parsed_index.isna().sum())
    numeric = pd.to_numeric(raw, errors="coerce")
    invalid_values = int(numeric.isna().sum())
    duplicate_rows = int(pd.Index(parsed_index[~parsed_index.isna()]).duplicated(keep=False).sum())
    nonpositive_rows = int((numeric <= 0).fillna(False).sum())

    clean = pd.Series(numeric.to_numpy(), index=parsed_index)
    clean = clean.loc[~clean.index.isna()].dropna()
    if getattr(clean.index, "tz", None) is not None:
        clean.index = clean.index.tz_localize(None)
    clean = clean.loc[clean > 0].sort_index()
    clean = clean.loc[~clean.index.duplicated(keep="last")]

    issues: list[str] = []
    score = 100
    if invalid_index or invalid_values:
        issues.append("invalid_rows")
        score -= min(25, (invalid_index + invalid_values) * 2)
    if duplicate_rows:
        issues.append("duplicates")
        score -= min(15, duplicate_rows)
    if nonpositive_rows:
        issues.append("nonpositive_prices")
        score -= min(25, nonpositive_rows * 3)

    if clean.empty:
        return HistoryQualityReport(
            score=0,
            level="poor",
            observations=0,
            start=None,
            end=None,
            years=0.0,
            duplicate_rows=duplicate_rows,
            invalid_rows=invalid_index + invalid_values,
            nonpositive_rows=nonpositive_rows,
            missing_business_days=0,
            missing_ratio=1.0,
            latest_age_days=None,
            issues=tuple(issues or ["empty"]),
        )

    start = pd.Timestamp(clean.index.min())
    end = pd.Timestamp(clean.index.max())
    years = max((end - start).days / 365.25, 0.0)
    expected = pd.bdate_range(start.normalize(), end.normalize())
    observed_days = pd.DatetimeIndex(clean.index.normalize()).unique()
    missing = max(len(expected.difference(observed_days)), 0)
    missing_ratio = missing / max(len(expected), 1)
    if missing_ratio > 0.15:
        issues.append("many_gaps")
        score -= 25
    elif missing_ratio > 0.08:
        issues.append("some_gaps")
        score -= 10

    reference = pd.Timestamp(as_of) if as_of is not None else pd.Timestamp.utcnow().tz_localize(None)
    if reference.tzinfo is not None:
        reference = reference.tz_localize(None)
    latest_age_days = max((reference.normalize() - end.normalize()).days, 0)
    if latest_age_days > 14:
        issues.append("stale")
        score -= 20
    elif latest_age_days > 7:
        issues.append("slightly_stale")
        score -= 5

    if len(clean) < 260:
        issues.append("short_history")
        score -= 30
    elif len(clean) < 750:
        issues.append("limited_history")
        score -= 10

    score = max(min(int(round(score)), 100), 0)
    level = "good" if score >= 85 else "warning" if score >= 60 else "poor"
    return HistoryQualityReport(
        score=score,
        level=level,
        observations=len(clean),
        start=start,
        end=end,
        years=years,
        duplicate_rows=duplicate_rows,
        invalid_rows=invalid_index + invalid_values,
        nonpositive_rows=nonpositive_rows,
        missing_business_days=missing,
        missing_ratio=missing_ratio,
        latest_age_days=latest_age_days,
        issues=tuple(issues),
    )


__all__ = ["HistoryQualityReport", "assess_price_history"]
