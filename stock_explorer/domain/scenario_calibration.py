from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HistoricalCalibration:
    sample_count: int
    weak_return_pct: float | None
    median_return_pct: float | None
    strong_return_pct: float | None
    annualized_volatility_pct: float | None
    max_drawdown_pct: float | None


SECTOR_GROWTH_RANGES: dict[str, tuple[float, float]] = {
    "bank": (-5.0, 12.0),
    "insurance": (-4.0, 10.0),
    "real_estate": (-8.0, 10.0),
    "technology": (-10.0, 25.0),
    "industrial": (-12.0, 15.0),
    "utility": (-4.0, 8.0),
    "energy": (-20.0, 25.0),
    "consumer": (-10.0, 12.0),
    "healthcare": (-8.0, 18.0),
    "generic": (-10.0, 15.0),
}


def _price_series(history: pd.DataFrame | pd.Series | None) -> pd.Series:
    if history is None:
        return pd.Series(dtype=float)
    if isinstance(history, pd.Series):
        series = history.copy()
    else:
        column = next((name for name in ("Adj Close", "Close", "close") if name in history.columns), None)
        if column is None:
            return pd.Series(dtype=float)
        series = history[column].copy()
    series = pd.to_numeric(series, errors="coerce").dropna()
    if series.index.has_duplicates:
        series = series[~series.index.duplicated(keep="last")]
    return series.sort_index()


def calibrate_history(
    history: pd.DataFrame | pd.Series | None,
    years: int,
) -> HistoricalCalibration:
    series = _price_series(history)
    if series.empty or years <= 0:
        return HistoricalCalibration(0, None, None, None, None, None)

    periods = max(1, int(round(252 * years)))
    returns = (series / series.shift(periods) - 1.0).dropna() * 100.0
    daily_returns = series.pct_change().dropna()
    volatility = float(daily_returns.std(ddof=0) * np.sqrt(252) * 100.0) if not daily_returns.empty else None
    running_high = series.cummax()
    drawdown = (series / running_high - 1.0) * 100.0
    max_drawdown = float(drawdown.min()) if not drawdown.empty else None

    if returns.empty:
        return HistoricalCalibration(0, None, None, None, volatility, max_drawdown)
    return HistoricalCalibration(
        sample_count=int(len(returns)),
        weak_return_pct=float(returns.quantile(0.20)),
        median_return_pct=float(returns.median()),
        strong_return_pct=float(returns.quantile(0.80)),
        annualized_volatility_pct=volatility,
        max_drawdown_pct=max_drawdown,
    )


def assess_projection(total_return_pct: float | None, calibration: HistoricalCalibration) -> str:
    if total_return_pct is None or calibration.sample_count < 20:
        return "insufficient"
    weak = calibration.weak_return_pct
    strong = calibration.strong_return_pct
    if weak is None or strong is None:
        return "insufficient"
    if total_return_pct < weak:
        return "below"
    if total_return_pct > strong:
        return "above"
    return "within"


def assess_growth_assumption(growth_pct: float, sector_category: str) -> str:
    lower, upper = SECTOR_GROWTH_RANGES.get(sector_category, SECTOR_GROWTH_RANGES["generic"])
    if growth_pct < lower:
        return "very_weak"
    if growth_pct > upper:
        return "very_strong"
    return "plausible"
