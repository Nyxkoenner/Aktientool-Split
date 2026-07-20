from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import pandas as pd


@dataclass(frozen=True)
class SimulationResult:
    equity_curve: pd.Series
    returns: pd.Series
    final_value: float
    max_drawdown_pct: float


def simulate_buy_and_hold(
    price_frame: pd.DataFrame,
    weights: Mapping[str, float],
    initial_capital: float = 10_000.0,
    rebalance_frequency: str | None = None,
) -> SimulationResult:
    if initial_capital <= 0:
        raise ValueError("Das Startkapital muss positiv sein.")
    prices = price_frame.sort_index().ffill().dropna(how="all")
    tickers = [ticker for ticker in weights if ticker in prices.columns]
    if not tickers:
        raise ValueError("Keine passenden Kursreihen vorhanden.")
    clean_weights = pd.Series({t: max(float(weights[t]), 0.0) for t in tickers})
    if clean_weights.sum() <= 0:
        raise ValueError("Die Gewichtung muss größer als null sein.")
    clean_weights /= clean_weights.sum()
    normalized = prices[tickers] / prices[tickers].iloc[0]

    if rebalance_frequency is None:
        curve = normalized.mul(clean_weights, axis=1).sum(axis=1) * initial_capital
    else:
        returns = prices[tickers].pct_change().fillna(0.0)
        curve_values = []
        value = initial_capital
        active_weights = clean_weights.copy()
        last_period = None
        for date, row in returns.iterrows():
            period = date.to_period(rebalance_frequency)
            if last_period is not None and period != last_period:
                active_weights = clean_weights.copy()
            value *= 1.0 + float((row * active_weights).sum())
            active_weights = active_weights * (1.0 + row)
            if active_weights.sum() > 0:
                active_weights /= active_weights.sum()
            curve_values.append(value)
            last_period = period
        curve = pd.Series(curve_values, index=returns.index, name="portfolio")

    returns = curve.pct_change().dropna()
    drawdown = curve / curve.cummax() - 1.0
    return SimulationResult(
        equity_curve=curve,
        returns=returns,
        final_value=float(curve.iloc[-1]),
        max_drawdown_pct=float(drawdown.min() * 100.0),
    )
