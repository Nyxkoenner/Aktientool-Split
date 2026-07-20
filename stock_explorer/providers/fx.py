from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Optional

import pandas as pd
import yfinance as yf


class FxProvider(ABC):
    name: str = "Unbekannt"

    @abstractmethod
    def to_eur(self, currency: str) -> Optional[float]:
        raise NotImplementedError

    def history_to_base(
        self,
        currency: str,
        start: date | datetime | pd.Timestamp,
        end: date | datetime | pd.Timestamp,
        base_currency: str = "EUR",
    ) -> pd.Series:
        """Return local-currency units converted into one base-currency unit.

        Providers without historical FX support may return a constant series from
        their current spot conversion. The index uses business days and is kept
        timezone-naive so it can be aligned with market histories.
        """

        start_ts = pd.Timestamp(start).tz_localize(None).normalize()
        end_ts = pd.Timestamp(end).tz_localize(None).normalize()
        index = pd.date_range(start_ts, end_ts, freq="B")
        normalized = str(currency or base_currency).upper().strip()
        base = str(base_currency or "EUR").upper().strip()
        if normalized == base:
            return pd.Series(1.0, index=index, name=normalized)
        if base != "EUR":
            return pd.Series(dtype=float, name=normalized)
        spot = self.to_eur(currency)
        if spot is None:
            return pd.Series(dtype=float, name=normalized)
        return pd.Series(float(spot), index=index, name=normalized)


class YahooFxProvider(FxProvider):
    name = "Yahoo Finance FX"

    @staticmethod
    def _currency_details(currency: str) -> tuple[str, float]:
        raw = str(currency or "EUR").strip()
        multiplier = 0.01 if raw in {"GBp", "GBX", "p"} else 1.0
        code = {"GBp": "GBP", "GBX": "GBP", "p": "GBP"}.get(raw, raw.upper())
        return code, multiplier

    @staticmethod
    def _eur_pair(code: str) -> str | None:
        return {
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

    def to_eur(self, currency: str) -> Optional[float]:
        code, multiplier = self._currency_details(currency)
        if code == "EUR":
            return multiplier
        pair = self._eur_pair(code)
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

    def history_to_base(
        self,
        currency: str,
        start: date | datetime | pd.Timestamp,
        end: date | datetime | pd.Timestamp,
        base_currency: str = "EUR",
    ) -> pd.Series:
        code, multiplier = self._currency_details(currency)
        base = str(base_currency or "EUR").upper().strip()
        start_ts = pd.Timestamp(start).tz_localize(None).normalize()
        end_ts = pd.Timestamp(end).tz_localize(None).normalize()
        index = pd.date_range(start_ts, end_ts, freq="B")
        if code == base:
            return pd.Series(multiplier, index=index, name=code)
        if base != "EUR":
            return super().history_to_base(currency, start_ts, end_ts, base_currency)
        pair = self._eur_pair(code)
        if pair is None:
            return super().history_to_base(currency, start_ts, end_ts, base_currency)
        try:
            history = yf.download(
                pair,
                start=start_ts,
                end=end_ts + pd.Timedelta(days=1),
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=False,
            )
        except Exception:
            history = pd.DataFrame()
        if history is None or history.empty:
            return super().history_to_base(currency, start_ts, end_ts, base_currency)
        close_raw = history.get("Close")
        if isinstance(close_raw, pd.DataFrame):
            close_raw = close_raw.iloc[:, 0]
        close = pd.to_numeric(close_raw, errors="coerce")
        close.index = pd.to_datetime(close.index, errors="coerce").tz_localize(None)
        close = close.loc[~close.index.isna()].sort_index().reindex(index).ffill().bfill()
        converted = multiplier / close.replace(0.0, pd.NA)
        return converted.astype(float).rename(code)
