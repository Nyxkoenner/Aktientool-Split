from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FeatureSet:
    frame: pd.DataFrame
    start: pd.Timestamp
    end: pd.Timestamp
    observations: int


def extract_close_series(history: pd.DataFrame | pd.Series) -> pd.Series:
    """Return a clean, timezone-naive close series from common provider payloads."""
    if isinstance(history, pd.Series):
        close = history.copy()
    elif isinstance(history, pd.DataFrame):
        close = pd.Series(dtype=float)
        for candidate in ("Adj Close", "Close", "close", "price"):
            if candidate in history.columns:
                close = history[candidate].copy()
                break
        if close.empty:
            numeric = history.select_dtypes(include=["number"])
            if not numeric.empty:
                close = numeric.iloc[:, 0].copy()
    else:
        raise TypeError("history must be a pandas Series or DataFrame")

    close = pd.to_numeric(close, errors="coerce")
    close.index = pd.to_datetime(close.index, errors="coerce")
    close = close.loc[~close.index.isna()].dropna()
    if getattr(close.index, "tz", None) is not None:
        close.index = close.index.tz_localize(None)
    close = close.loc[close > 0].sort_index()
    close = close.loc[~close.index.duplicated(keep="last")]
    close.name = "close"
    if len(close) < 260:
        raise ValueError("Für das KI-Labor werden mindestens rund 260 Handelstage benötigt.")
    return close.astype(float)


def _rsi(close: pd.Series, window: int = 14) -> pd.Series:
    change = close.diff()
    gain = change.clip(lower=0).rolling(window).mean()
    loss = -change.clip(upper=0).rolling(window).mean()
    relative_strength = gain / loss.replace(0, np.nan)
    rsi = 100.0 - 100.0 / (1.0 + relative_strength)
    return rsi.fillna(50.0)


def build_feature_frame(
    history: pd.DataFrame | pd.Series,
    *,
    current_scores: Mapping[str, float | int | None] | None = None,
) -> FeatureSet:
    """Build backward-looking price features without historical fundamental leakage.

    ``current_scores`` are stored only as metadata columns prefixed with ``context_``.
    They are deliberately excluded from the RL state because today's fundamental
    scores are not point-in-time historical data.
    """
    close = extract_close_series(history)
    frame = pd.DataFrame(index=close.index)
    frame["close"] = close
    frame["asset_return"] = close.pct_change().fillna(0.0)
    frame["return_5d"] = close.pct_change(5)
    frame["return_20d"] = close.pct_change(20)
    frame["return_60d"] = close.pct_change(60)
    frame["volatility_20d"] = frame["asset_return"].rolling(20).std() * np.sqrt(252.0)
    frame["sma_20"] = close.rolling(20).mean()
    frame["sma_50"] = close.rolling(50).mean()
    frame["sma_200"] = close.rolling(200).mean()
    frame["price_to_sma20"] = close / frame["sma_20"] - 1.0
    frame["price_to_sma50"] = close / frame["sma_50"] - 1.0
    frame["price_to_sma200"] = close / frame["sma_200"] - 1.0
    frame["sma50_to_sma200"] = frame["sma_50"] / frame["sma_200"] - 1.0
    frame["drawdown"] = close / close.cummax() - 1.0
    frame["rsi_14"] = _rsi(close)

    for key, value in (current_scores or {}).items():
        numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
        frame[f"context_{key}"] = float(numeric) if pd.notna(numeric) else np.nan

    required = [
        "close",
        "asset_return",
        "return_20d",
        "volatility_20d",
        "price_to_sma50",
        "price_to_sma200",
        "sma50_to_sma200",
        "drawdown",
        "rsi_14",
    ]
    frame = frame.dropna(subset=required).copy()
    if len(frame) < 80:
        raise ValueError("Nach der Feature-Berechnung bleiben zu wenige Beobachtungen übrig.")
    return FeatureSet(
        frame=frame,
        start=pd.Timestamp(frame.index.min()),
        end=pd.Timestamp(frame.index.max()),
        observations=len(frame),
    )
