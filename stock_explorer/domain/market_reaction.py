from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd


def _price_series(frame: pd.DataFrame | pd.Series | None) -> pd.Series:
    if frame is None:
        return pd.Series(dtype=float)
    if isinstance(frame, pd.Series):
        series = pd.to_numeric(frame, errors="coerce")
    elif frame.empty:
        return pd.Series(dtype=float)
    else:
        column = next(
            (name for name in ("Adj Close", "Close", "close", "price") if name in frame.columns), None
        )
        if column is None:
            return pd.Series(dtype=float)
        series = pd.to_numeric(frame[column], errors="coerce")
    series.index = pd.to_datetime(series.index, errors="coerce")
    series = series.loc[~series.index.isna()].dropna().sort_index()
    if getattr(series.index, "tz", None) is not None:
        series.index = series.index.tz_localize(None)
    return series[~series.index.duplicated(keep="last")]


def _forward_return(
    series: pd.Series, date_value: pd.Timestamp, horizon: int
) -> tuple[float | None, pd.Timestamp | None]:
    if series.empty:
        return None, None
    position = int(series.index.searchsorted(date_value.normalize(), side="left"))
    if position >= len(series):
        return None, None
    end_position = position + int(horizon)
    if end_position >= len(series):
        return None, series.index[position]
    start_price = float(series.iloc[position])
    end_price = float(series.iloc[end_position])
    if start_price == 0:
        return None, series.index[position]
    return (end_price / start_price - 1.0) * 100.0, series.index[position]


def _annualized_volatility(series: pd.Series) -> float | None:
    returns = series.pct_change().dropna()
    if len(returns) < 3:
        return None
    value = float(returns.std(ddof=1) * np.sqrt(252) * 100)
    return value if np.isfinite(value) else None


def _post_drawdown(series: pd.Series, date_value: pd.Timestamp, days: int = 20) -> float | None:
    if series.empty:
        return None
    position = int(series.index.searchsorted(date_value.normalize(), side="left"))
    window = series.iloc[position : position + days + 1]
    if len(window) < 2:
        return None
    drawdown = window / window.cummax() - 1.0
    return float(drawdown.min() * 100)


def compute_market_reactions(
    events: pd.DataFrame,
    price_history: pd.DataFrame | pd.Series | None,
    benchmark_history: pd.DataFrame | pd.Series | None = None,
    *,
    horizons: Iterable[int] = (1, 5, 20),
) -> pd.DataFrame:
    if events is None or events.empty:
        return pd.DataFrame()
    prices = _price_series(price_history)
    benchmark = _price_series(benchmark_history)
    result = events.copy()
    date_column = "published" if "published" in result.columns else "date"
    result[date_column] = pd.to_datetime(result[date_column], errors="coerce")

    rows: list[dict[str, Any]] = []
    for _, row in result.dropna(subset=[date_column]).iterrows():
        event_date = pd.Timestamp(row[date_column])
        if event_date.tzinfo is not None:
            event_date = event_date.tz_localize(None)
        output = row.to_dict()
        trade_date: pd.Timestamp | None = None
        for horizon in horizons:
            stock_return, located_date = _forward_return(prices, event_date, int(horizon))
            benchmark_return, _ = _forward_return(benchmark, event_date, int(horizon))
            if trade_date is None:
                trade_date = located_date
            output[f"return_{horizon}d"] = stock_return
            output[f"benchmark_return_{horizon}d"] = benchmark_return
            output[f"excess_return_{horizon}d"] = (
                stock_return - benchmark_return
                if stock_return is not None and benchmark_return is not None
                else None
            )
        if trade_date is not None and not prices.empty:
            position = int(prices.index.searchsorted(trade_date, side="left"))
            output["volatility_before_20d"] = _annualized_volatility(
                prices.iloc[max(0, position - 20) : position + 1]
            )
            output["volatility_after_20d"] = _annualized_volatility(prices.iloc[position : position + 21])
            output["max_drawdown_after_20d"] = _post_drawdown(prices, trade_date, 20)
            output["reaction_trade_date"] = trade_date
        else:
            output["volatility_before_20d"] = None
            output["volatility_after_20d"] = None
            output["max_drawdown_after_20d"] = None
            output["reaction_trade_date"] = pd.NaT
        rows.append(output)
    return pd.DataFrame(rows)
