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
    transaction_costs: float = 0.0
    dividends_received: float = 0.0


def simulate_buy_and_hold(
    price_frame: pd.DataFrame,
    weights: Mapping[str, float],
    initial_capital: float = 10_000.0,
    rebalance_frequency: str | None = None,
    transaction_cost_bps: float = 0.0,
    annual_dividend_yields: Mapping[str, float] | None = None,
) -> SimulationResult:
    if initial_capital <= 0:
        raise ValueError("Das Startkapital muss positiv sein.")
    prices = price_frame.sort_index().ffill().dropna(how="all")
    tickers = [ticker for ticker in weights if ticker in prices.columns]
    if not tickers:
        raise ValueError("Keine passenden Kursreihen vorhanden.")
    prices = prices[tickers].dropna()
    if prices.empty:
        raise ValueError("Keine vollständigen Kursdaten vorhanden.")
    clean_weights = pd.Series({ticker: max(float(weights[ticker]), 0.0) for ticker in tickers})
    if clean_weights.sum() <= 0:
        raise ValueError("Die Gewichtung muss größer als null sein.")
    clean_weights /= clean_weights.sum()
    returns = prices.pct_change().fillna(0.0)
    dividend_yields = pd.Series(
        {
            ticker: max(float((annual_dividend_yields or {}).get(ticker, 0.0)), 0.0) / 100.0
            for ticker in tickers
        }
    )
    daily_dividends = dividend_yields / 252.0

    value = float(initial_capital)
    active_weights = clean_weights.copy()
    curve_values: list[float] = []
    total_costs = initial_capital * max(transaction_cost_bps, 0.0) / 10_000.0
    value -= total_costs
    dividends_received = 0.0
    last_period = None

    for date, row in returns.iterrows():
        period = date.to_period(rebalance_frequency) if rebalance_frequency else None
        if rebalance_frequency and last_period is not None and period != last_period:
            turnover = float((active_weights - clean_weights).abs().sum()) / 2.0
            cost = value * turnover * max(transaction_cost_bps, 0.0) / 10_000.0
            value -= cost
            total_costs += cost
            active_weights = clean_weights.copy()
        dividend = value * float((active_weights * daily_dividends).sum())
        dividends_received += dividend
        value *= 1.0 + float((row * active_weights).sum())
        value += dividend
        active_weights = active_weights * (1.0 + row)
        if active_weights.sum() > 0:
            active_weights /= active_weights.sum()
        curve_values.append(value)
        last_period = period

    curve = pd.Series(curve_values, index=returns.index, name="portfolio")
    curve_returns = curve.pct_change().dropna()
    drawdown = curve / curve.cummax() - 1.0
    return SimulationResult(
        equity_curve=curve,
        returns=curve_returns,
        final_value=float(curve.iloc[-1]),
        max_drawdown_pct=float(drawdown.min() * 100.0),
        transaction_costs=float(total_costs),
        dividends_received=float(dividends_received),
    )
