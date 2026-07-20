"""Kleine, testbare Datenmodelle für den Streamlit-Anwendungsablauf."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pandas as pd


@dataclass(frozen=True)
class ScannerThresholds:
    drawdown_trigger: float
    payout_max: float
    score_min: float
    yield_min: float


@dataclass(frozen=True)
class SidebarSelection:
    index_name: str
    filtered_constituents: pd.DataFrame
    max_stocks: int
    profile_name: str
    thresholds: ScannerThresholds
    reload_clicked: bool

    def selected_constituents(self) -> pd.DataFrame:
        return self.filtered_constituents.head(self.max_stocks).reset_index(drop=True)


def selected_tickers(
    constituents: pd.DataFrame,
    cleaner: Callable[[object], str],
) -> tuple[str, ...]:
    """Erzeugt einen stabilen Vergleichsschlüssel für die aktuell gewählte Auswahl."""
    if constituents.empty or "ticker_yahoo" not in constituents.columns:
        return ()
    return tuple(constituents["ticker_yahoo"].map(cleaner))


__all__ = ["ScannerThresholds", "SidebarSelection", "selected_tickers"]
