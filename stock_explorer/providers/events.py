from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from .models import EventFetchResult, ProviderDiagnostic
from .sec import SecProvider

EVENT_COLUMNS = [
    "date",
    "ticker_yahoo",
    "event_type",
    "title",
    "source",
    "link",
    "sentiment_score",
    "sentiment_label",
    "sentiment_confidence",
    "sentiment_reason",
    "importance",
    "is_future_event",
    "verification_level",
    "verification_score",
    "event_status",
    "source_type",
    "source_url",
    "retrieved_at",
    "notes",
    "conflict_note",
]


class EventProvider(ABC):
    name: str = "Unbekannt"

    @abstractmethod
    def fetch(self, ticker: str, company_name: str, days_back: int, days_forward: int) -> EventFetchResult:
        raise NotImplementedError


def empty_events() -> pd.DataFrame:
    return pd.DataFrame(columns=EVENT_COLUMNS)


def _normalize(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy() if isinstance(frame, pd.DataFrame) else empty_events()
    for column in EVENT_COLUMNS:
        if column not in result.columns:
            result[column] = None
    result = result[EVENT_COLUMNS]
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    if not result.empty and getattr(result["date"].dt, "tz", None) is not None:
        result["date"] = result["date"].dt.tz_localize(None)
    return result.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)


class ManualCsvEventProvider(EventProvider):
    name = "Manuell bestätigte Termine"

    def __init__(self, path: Path) -> None:
        self._path = path

    def fetch(self, ticker: str, company_name: str, days_back: int, days_forward: int) -> EventFetchResult:
        diagnostic = ProviderDiagnostic(
            source=self.name,
            kind="manual_csv",
            status="Nicht konfiguriert",
            url=str(self._path),
        )
        if not self._path.exists():
            return EventFetchResult(empty_events(), pd.DataFrame([diagnostic.to_dict()]))
        try:
            frame = pd.read_csv(self._path)
            diagnostic.entries = len(frame)
            if "ticker_yahoo" not in frame.columns or "date" not in frame.columns:
                raise ValueError("Spalten ticker_yahoo und date fehlen.")
            frame = frame[frame["ticker_yahoo"].astype(str).str.upper() == str(ticker).upper()].copy()
            frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
            earliest = pd.Timestamp.now().normalize() - pd.Timedelta(days=days_back)
            latest = pd.Timestamp.now().normalize() + pd.Timedelta(days=days_forward)
            frame = frame[frame["date"].between(earliest, latest)]
            frame["source"] = frame.get("source", self.name)
            frame["verification_level"] = "manual_confirmed"
            frame["verification_score"] = 85
            frame["event_status"] = "bestätigt"
            frame["source_type"] = "manual"
            frame["is_future_event"] = frame["date"] >= pd.Timestamp.now().normalize()
            diagnostic.matches = len(frame)
            diagnostic.status = "OK" if not frame.empty else "Keine Termine"
            return EventFetchResult(_normalize(frame), pd.DataFrame([diagnostic.to_dict()]))
        except Exception as error:
            diagnostic.status = "Fehler"
            diagnostic.message = f"{type(error).__name__}: {error}"
            return EventFetchResult(empty_events(), pd.DataFrame([diagnostic.to_dict()]))


class YahooCalendarEventProvider(EventProvider):
    name = "Yahoo Finance Calendar"

    def fetch(self, ticker: str, company_name: str, days_back: int, days_forward: int) -> EventFetchResult:
        diagnostic = ProviderDiagnostic(
            source=self.name,
            kind="data_provider",
            status="Nicht verfügbar",
            url=f"https://finance.yahoo.com/quote/{ticker}",
        )
        rows: list[dict[str, Any]] = []
        try:
            obj = yf.Ticker(ticker)
            calendar = obj.calendar
            if isinstance(calendar, pd.DataFrame):
                calendar_data: dict[str, Any] = {}
                if calendar.shape[1] == 1:
                    for label, value in calendar.iloc[:, 0].items():
                        calendar_data[str(label)] = value
                else:
                    calendar_data = calendar.to_dict()
            elif isinstance(calendar, dict):
                calendar_data = calendar
            else:
                calendar_data = {}

            def calendar_values(*keys: str) -> list[Any]:
                raw: Any = None
                for key in keys:
                    if key in calendar_data:
                        raw = calendar_data[key]
                        break
                if raw is None:
                    return []
                if isinstance(raw, dict):
                    return list(raw.values())
                if isinstance(raw, (list, tuple, pd.Series, pd.Index)):
                    return list(raw)
                return [raw]

            event_specs = [
                (
                    calendar_values("Earnings Date", "EarningsDate"),
                    "earnings",
                    "Quartalszahlen / Earnings",
                    "hoch",
                ),
                (
                    calendar_values("Ex-Dividend Date", "Ex-Dividend Date "),
                    "dividend",
                    "Ex-Dividende",
                    "mittel",
                ),
                (
                    calendar_values("Dividend Date", "DividendDate"),
                    "dividend",
                    "Dividendenzahlung",
                    "mittel",
                ),
            ]
            for raw_dates, event_type, title, importance in event_specs:
                for value in raw_dates:
                    date_value = pd.to_datetime(value, errors="coerce")
                    if pd.isna(date_value):
                        continue
                    timestamp = pd.Timestamp(date_value)
                    if timestamp.tzinfo is not None:
                        timestamp = timestamp.tz_localize(None)
                    rows.append(
                        {
                            "date": timestamp,
                            "ticker_yahoo": ticker,
                            "event_type": event_type,
                            "title": title,
                            "source": self.name,
                            "source_url": diagnostic.url,
                            "verification_level": "data_provider",
                            "verification_score": 65,
                            "event_status": "Datenanbieter",
                            "source_type": "calendar",
                            "importance": importance,
                            "sentiment_label": "neutral",
                            "sentiment_confidence": "niedrig",
                            "sentiment_reason": "Kalendertermin ohne inhaltliche Bewertung",
                        }
                    )
            frame = _normalize(pd.DataFrame(rows))
            earliest = pd.Timestamp.now().normalize() - pd.Timedelta(days=days_back)
            latest = pd.Timestamp.now().normalize() + pd.Timedelta(days=days_forward)
            if not frame.empty:
                frame = frame[frame["date"].between(earliest, latest)].copy()
                frame["is_future_event"] = frame["date"] >= pd.Timestamp.now().normalize()
            diagnostic.entries = len(rows)
            diagnostic.matches = len(frame)
            diagnostic.status = "OK" if not frame.empty else "Keine Termine"
            return EventFetchResult(frame, pd.DataFrame([diagnostic.to_dict()]))
        except Exception as error:
            diagnostic.status = "Fehler"
            diagnostic.message = f"{type(error).__name__}: {error}"
            return EventFetchResult(empty_events(), pd.DataFrame([diagnostic.to_dict()]))


class SecFilingEventProvider(EventProvider):
    name = "SEC EDGAR"

    def __init__(self, sec_provider: SecProvider) -> None:
        self._sec = sec_provider

    @staticmethod
    def _meta(form: str) -> tuple[str, str, str] | None:
        normalized = str(form or "").upper().strip()
        if normalized in {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"}:
            return "report", f"Jahresbericht / {normalized}", "hoch"
        if normalized in {"10-Q", "10-Q/A"}:
            return "earnings", f"Quartalsbericht / {normalized}", "hoch"
        if normalized in {"8-K", "8-K/A", "6-K", "6-K/A"}:
            return "report", f"Unternehmensmeldung / {normalized}", "mittel"
        if normalized in {"DEF 14A", "DEFA14A", "PRE 14A"}:
            return "annual_meeting", f"Proxy Statement / {normalized}", "hoch"
        return None

    def fetch(self, ticker: str, company_name: str, days_back: int, days_forward: int) -> EventFetchResult:
        filings, diagnostic = self._sec.recent_filings(ticker, days_back=days_back)
        rows: list[dict[str, Any]] = []
        for _, filing in filings.iterrows():
            meta = self._meta(str(filing.get("form", "")))
            if meta is None:
                continue
            event_type, base_title, importance = meta
            description = str(filing.get("description", "") or "").strip()
            rows.append(
                {
                    "date": filing.get("filing_date"),
                    "ticker_yahoo": ticker,
                    "event_type": event_type,
                    "title": base_title if not description else f"{base_title}: {description}",
                    "source": self.name,
                    "link": filing.get("link", ""),
                    "sentiment_score": 0.0,
                    "sentiment_label": "neutral",
                    "sentiment_confidence": "niedrig",
                    "sentiment_reason": "Offizielles Filing – keine automatische inhaltliche Bewertung",
                    "importance": importance,
                    "is_future_event": False,
                    "verification_level": "official",
                    "verification_score": 100,
                    "event_status": "bestätigt",
                    "source_type": "regulator",
                    "source_url": diagnostic.url,
                    "retrieved_at": filing.get("retrieved_at", ""),
                    "notes": f"SEC-CIK {filing.get('cik', '')} · {company_name}",
                    "conflict_note": "",
                }
            )
        diagnostic.matches = len(rows)
        return EventFetchResult(
            _normalize(pd.DataFrame(rows)),
            pd.DataFrame([diagnostic.to_dict()]),
        )
