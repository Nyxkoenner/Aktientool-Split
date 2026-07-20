from __future__ import annotations

import os

from .base import MarketDataProvider
from .yahoo import YahooMarketDataProvider


def get_market_provider(name: str | None = None) -> MarketDataProvider:
    configured = name if name is not None else os.environ.get("AKTIEN_EXPLORER_MARKET_PROVIDER")
    provider_name = (configured or "yahoo").strip().lower()
    if provider_name == "yahoo":
        return YahooMarketDataProvider()
    raise ValueError(f"Unbekannter Marktdatenanbieter: {provider_name}. Aktuell verfügbar: yahoo")
