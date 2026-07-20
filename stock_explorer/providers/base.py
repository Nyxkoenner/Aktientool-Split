from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional

import pandas as pd


class MarketDataProvider(ABC):
    """Austauschbare Schnittstelle für Markt-, Fundamental- und FX-Daten."""

    name: str = "Unbekannt"

    @abstractmethod
    def download_price_histories(
        self, tickers: tuple[str, ...], period: str = "5y"
    ) -> dict[str, pd.DataFrame]:
        raise NotImplementedError

    @abstractmethod
    def get_info(self, ticker: str, wanted_keys: Iterable[str]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_dividends(self, ticker: str) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def fx_to_eur(self, currency: str) -> Optional[float]:
        raise NotImplementedError
