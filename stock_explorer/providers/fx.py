from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import yfinance as yf


class FxProvider(ABC):
    name: str = "Unbekannt"

    @abstractmethod
    def to_eur(self, currency: str) -> Optional[float]:
        raise NotImplementedError


class YahooFxProvider(FxProvider):
    name = "Yahoo Finance FX"

    def to_eur(self, currency: str) -> Optional[float]:
        raw = str(currency or "EUR").strip()
        multiplier = 0.01 if raw in {"GBp", "GBX", "p"} else 1.0
        code = {"GBp": "GBP", "GBX": "GBP", "p": "GBP"}.get(raw, raw.upper())
        if code == "EUR":
            return multiplier

        pair = {
            "USD": "EURUSD=X",
            "GBP": "EURGBP=X",
            "CHF": "EURCHF=X",
            "JPY": "EURJPY=X",
            "CAD": "EURCAD=X",
            "AUD": "EURAUD=X",
            "SEK": "EURSEK=X",
            "NOK": "EURNOK=X",
            "DKK": "EURDKK=X",
        }.get(code)
        if pair is None:
            return None
        try:
            history = yf.Ticker(pair).history(period="5d", auto_adjust=False)
            close = pd.to_numeric(history.get("Close"), errors="coerce").dropna()
            rate = float(close.iloc[-1]) if not close.empty else None
        except Exception:
            rate = None
        if rate is None or rate == 0:
            return None
        return multiplier / rate
