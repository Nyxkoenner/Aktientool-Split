from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class StrategyMetrics:
    total_return_pct: float
    annualized_return_pct: float
    annualized_volatility_pct: float
    sharpe_ratio: float | None
    max_drawdown_pct: float
    positive_day_rate_pct: float
    exposure_pct: float
    trades: int
    turnover: float


@dataclass(frozen=True)
class StrategyResult:
    name: str
    positions: pd.Series
    returns: pd.Series
    equity_curve: pd.Series
    metrics: StrategyMetrics


def buy_and_hold_positions(features: pd.DataFrame) -> pd.Series:
    return pd.Series(1.0, index=features.index, name="position")


def momentum_positions(features: pd.DataFrame) -> pd.Series:
    signal = (features["sma50_to_sma200"] > 0.0) & (features["return_20d"] > 0.0)
    return signal.astype(float).rename("position")


def recovery_positions(features: pd.DataFrame) -> pd.Series:
    entry = (features["drawdown"] <= -0.18) & (features["rsi_14"] <= 42.0)
    recovery = (features["price_to_sma20"] > 0.0) | (features["return_20d"] > 0.03)
    position = pd.Series(0.0, index=features.index, name="position")
    active = False
    for timestamp in features.index:
        if not active and bool(entry.loc[timestamp]):
            active = True
        elif active and bool(recovery.loc[timestamp]):
            active = False
        position.loc[timestamp] = 1.0 if active else 0.0
    return position


def combined_positions(features: pd.DataFrame) -> pd.Series:
    trend = momentum_positions(features)
    recovery = recovery_positions(features)
    safety_filter = (features["volatility_20d"] < 0.65) & (features["drawdown"] > -0.55)
    return (((trend > 0) | (recovery > 0)) & safety_filter).astype(float).rename("position")


def baseline_positions(features: pd.DataFrame) -> Mapping[str, pd.Series]:
    return {
        "buy_hold": buy_and_hold_positions(features),
        "momentum": momentum_positions(features),
        "recovery": recovery_positions(features),
        "combined": combined_positions(features),
    }


def _metrics(returns: pd.Series, positions: pd.Series, turnover: pd.Series) -> StrategyMetrics:
    clean = pd.to_numeric(returns, errors="coerce").fillna(0.0)
    equity = (1.0 + clean).cumprod()
    total_return = float((equity.iloc[-1] - 1.0) * 100.0) if not equity.empty else 0.0
    periods = max(len(clean), 1)
    years = periods / 252.0
    annualized = ((float(equity.iloc[-1]) ** (1.0 / years)) - 1.0) * 100.0 if years > 0 else 0.0
    volatility = float(clean.std(ddof=0) * np.sqrt(252.0) * 100.0)
    sharpe = None
    if volatility > 1e-12:
        sharpe = float((clean.mean() / clean.std(ddof=0)) * np.sqrt(252.0))
    drawdown = equity / equity.cummax() - 1.0
    invested_returns = clean.loc[positions.shift(1).fillna(0.0) > 0]
    positive_rate = float((invested_returns > 0).mean() * 100.0) if not invested_returns.empty else 0.0
    return StrategyMetrics(
        total_return_pct=total_return,
        annualized_return_pct=float(annualized),
        annualized_volatility_pct=volatility,
        sharpe_ratio=sharpe,
        max_drawdown_pct=float(drawdown.min() * 100.0) if not drawdown.empty else 0.0,
        positive_day_rate_pct=positive_rate,
        exposure_pct=float(positions.mean() * 100.0),
        trades=int((turnover > 0).sum()),
        turnover=float(turnover.sum()),
    )


def simulate_positions(
    features: pd.DataFrame,
    positions: pd.Series,
    *,
    name: str,
    transaction_cost_bps: float = 10.0,
) -> StrategyResult:
    aligned = positions.reindex(features.index).ffill().fillna(0.0).clip(0.0, 1.0)
    turnover = aligned.diff().abs().fillna(aligned.abs())
    cost_rate = max(float(transaction_cost_bps), 0.0) / 10_000.0
    strategy_returns = aligned.shift(1).fillna(0.0) * features["asset_return"] - turnover * cost_rate
    equity = (1.0 + strategy_returns).cumprod() * 100.0
    equity.name = name
    return StrategyResult(
        name=name,
        positions=aligned,
        returns=strategy_returns.rename(name),
        equity_curve=equity,
        metrics=_metrics(strategy_returns, aligned, turnover),
    )
