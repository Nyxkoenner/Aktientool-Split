from __future__ import annotations

import logging
import re
from typing import Any, Iterable, Optional

import pandas as pd
import yfinance as yf

from .base import MarketDataProvider

logging.getLogger("yfinance").setLevel(logging.CRITICAL)


def _datetime_index(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.index = pd.to_datetime(frame.index, errors="coerce")
    frame = frame.loc[~frame.index.isna()]
    if getattr(frame.index, "tz", None) is not None:
        frame.index = frame.index.tz_localize(None)
    return frame.sort_index()


def _extract(downloaded: pd.DataFrame, ticker: str, count: int) -> pd.DataFrame:
    if downloaded is None or downloaded.empty:
        return pd.DataFrame()
    if count == 1 and not isinstance(downloaded.columns, pd.MultiIndex):
        return downloaded.copy()
    if isinstance(downloaded.columns, pd.MultiIndex):
        level0 = downloaded.columns.get_level_values(0)
        level1 = downloaded.columns.get_level_values(1)
        if ticker in level0:
            return downloaded[ticker].copy()
        if ticker in level1:
            return downloaded.xs(ticker, axis=1, level=1).copy()
    return pd.DataFrame()


class YahooMarketDataProvider(MarketDataProvider):
    name = "Yahoo Finance (yfinance)"

    def download_price_histories(
        self, tickers: tuple[str, ...], period: str = "5y"
    ) -> dict[str, pd.DataFrame]:
        valid = tuple(
            dict.fromkeys(
                str(t).strip().upper()
                for t in tickers
                if t and re.match(r"^[A-Z0-9][A-Z0-9.\-]*$", str(t).strip().upper())
            )
        )
        if not valid:
            return {}
        try:
            downloaded = yf.download(
                list(valid),
                period=period,
                interval="1d",
                group_by="ticker",
                auto_adjust=False,
                actions=False,
                threads=True,
                progress=False,
                repair=False,
            )
        except Exception:
            downloaded = pd.DataFrame()

        result: dict[str, pd.DataFrame] = {}
        for ticker in valid:
            frame = _extract(downloaded, ticker, len(valid))
            if frame.empty:
                try:
                    frame = yf.Ticker(ticker).history(period=period, auto_adjust=False)
                except Exception:
                    frame = pd.DataFrame()
            if frame.empty:
                result[ticker] = pd.DataFrame()
                continue
            frame = _datetime_index(frame)
            columns = [
                c for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in frame.columns
            ]
            result[ticker] = frame[columns].copy()
        return result

    def get_info(self, ticker: str, wanted_keys: Iterable[str]) -> dict[str, Any]:
        try:
            raw = yf.Ticker(ticker).get_info() or {}
        except Exception:
            raw = {}
        return {key: raw.get(key) for key in wanted_keys}

    def get_dividends(self, ticker: str) -> pd.DataFrame:
        try:
            values = yf.Ticker(ticker).dividends
        except Exception:
            values = pd.Series(dtype=float)
        if values is None or values.empty:
            return pd.DataFrame(columns=["date", "amount"])
        frame = values.rename("amount").to_frame().reset_index()
        frame.columns = ["date", "amount"]
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        if getattr(frame["date"].dt, "tz", None) is not None:
            frame["date"] = frame["date"].dt.tz_localize(None)
        frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce")
        return frame.dropna(subset=["date", "amount"]).sort_values("date")

    def fx_to_eur(self, currency: str) -> Optional[float]:
        raw = str(currency or "EUR").strip()
        multiplier = 0.01 if raw in {"GBp", "GBX", "p"} else 1.0
        code = {"GBp": "GBP", "GBX": "GBP", "p": "GBP"}.get(raw, raw.upper())
        if code == "EUR":
            return multiplier
        pairs = {
            "USD": "EURUSD=X",
            "GBP": "EURGBP=X",
            "CHF": "EURCHF=X",
            "JPY": "EURJPY=X",
            "CAD": "EURCAD=X",
            "AUD": "EURAUD=X",
            "SEK": "EURSEK=X",
            "NOK": "EURNOK=X",
            "DKK": "EURDKK=X",
        }
        pair = pairs.get(code)
        if pair is None:
            return None
        try:
            hist = yf.Ticker(pair).history(period="5d", auto_adjust=False)
            close = pd.to_numeric(hist.get("Close"), errors="coerce").dropna()
            rate = float(close.iloc[-1]) if not close.empty else None
        except Exception:
            rate = None
        if rate is None or rate == 0:
            return None
        return multiplier / float(rate)
