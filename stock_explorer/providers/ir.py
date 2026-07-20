from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from stock_explorer.domain.event_resolution import verification_score
from stock_explorer.domain.news_analysis import NewsAnalyzer

from .events import EVENT_COLUMNS, EventProvider, empty_events
from .http import HttpClient, RequestsHttpClient
from .models import EventFetchResult, ProviderDiagnostic
from .news import _parse_entries

IR_SOURCE_COLUMNS = [
    "ticker_yahoo",
    "source_name",
    "source_type",
    "feed_url",
    "source_url",
    "verification_level",
    "enabled",
    "notes",
]


def _clean_ticker(value: Any) -> str:
    return str(value or "").strip().upper().replace("$", "")


def _parse_ics_datetime(value: str) -> pd.Timestamp | pd.NaT:
    raw = str(value or "").strip()
    if not raw:
        return pd.NaT
    for fmt in ("%Y%m%d", "%Y%m%dT%H%M%SZ", "%Y%m%dT%H%M%S", "%Y%m%dT%H%M"):
        try:
            return pd.Timestamp(datetime.strptime(raw, fmt))
        except ValueError:
            continue
    return pd.to_datetime(raw, errors="coerce")


def parse_ics_payload(payload: bytes) -> list[dict[str, str]]:
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = payload.decode("latin-1", errors="replace")

    raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines: list[str] = []
    for line in raw_lines:
        if line.startswith((" ", "\t")) and lines:
            lines[-1] += line[1:]
        else:
            lines.append(line)

    events: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in lines:
        stripped = line.strip()
        if stripped == "BEGIN:VEVENT":
            current = {}
            continue
        if stripped == "END:VEVENT":
            if current is not None:
                events.append(current)
            current = None
            continue
        if current is None or ":" not in line:
            continue
        key_part, value = line.split(":", 1)
        key = key_part.split(";", 1)[0].strip().upper()
        current[key] = value.replace("\\n", " ").replace("\\,", ",").strip()
    return events


class IrRegistryEventProvider(EventProvider):
    name = "Unternehmens-IR"

    def __init__(
        self,
        path: Path,
        *,
        http_client: HttpClient | None = None,
        headers: dict[str, str] | None = None,
        analyzer: NewsAnalyzer | None = None,
    ) -> None:
        self._path = path
        self._http = http_client or RequestsHttpClient()
        self._headers = headers or {}
        self._analyzer = analyzer or NewsAnalyzer()

    def _sources(self, ticker: str) -> pd.DataFrame:
        if not self._path.exists():
            return pd.DataFrame(columns=IR_SOURCE_COLUMNS)
        try:
            frame = pd.read_csv(self._path, dtype=str).fillna("")
        except Exception:
            return pd.DataFrame(columns=IR_SOURCE_COLUMNS)
        for column in IR_SOURCE_COLUMNS:
            if column not in frame.columns:
                frame[column] = ""
        frame["ticker_yahoo"] = frame["ticker_yahoo"].map(_clean_ticker)
        enabled = frame["enabled"].astype(str).str.strip().str.lower().isin({"true", "1", "yes", "ja", "x"})
        return frame[(frame["ticker_yahoo"] == _clean_ticker(ticker)) & enabled][IR_SOURCE_COLUMNS].copy()

    @staticmethod
    def _base_row(
        *,
        ticker: str,
        date: pd.Timestamp,
        event_type: str,
        title: str,
        source_name: str,
        source_url: str,
        link: str,
        verification_level: str,
        source_type: str,
        notes: str,
    ) -> dict[str, Any]:
        normalized_date = pd.Timestamp(date)
        if normalized_date.tzinfo is not None:
            normalized_date = normalized_date.tz_localize(None)
        return {
            "date": normalized_date,
            "ticker_yahoo": _clean_ticker(ticker),
            "event_type": event_type,
            "title": title,
            "source": source_name,
            "link": link,
            "sentiment_score": 0,
            "sentiment_label": "neutral",
            "sentiment_confidence": "niedrig",
            "sentiment_reason": "Offizielle IR-Quelle – keine automatische Richtung ohne Textsignal",
            "importance": "hoch" if event_type in {"earnings", "annual_meeting", "report"} else "mittel",
            "is_future_event": normalized_date.normalize() >= pd.Timestamp.now().normalize(),
            "verification_level": verification_level,
            "verification_score": verification_score(verification_level),
            "event_status": "bestätigt",
            "source_type": source_type,
            "source_url": source_url,
            "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "notes": notes,
            "conflict_note": "",
        }

    def _fetch_source(
        self,
        source: pd.Series,
        ticker: str,
        earliest: pd.Timestamp,
        latest: pd.Timestamp,
    ) -> tuple[pd.DataFrame, ProviderDiagnostic]:
        source_name = str(source.get("source_name") or self.name)
        source_type = str(source.get("source_type") or "rss").strip().lower()
        feed_url = str(source.get("feed_url") or "").strip()
        source_url = str(source.get("source_url") or feed_url).strip()
        verification_level = str(source.get("verification_level") or "official_ir").strip().lower()
        diagnostic = ProviderDiagnostic(
            source=source_name,
            kind=f"ir_{source_type}",
            status="Nicht konfiguriert",
            url=feed_url or source_url,
        )
        if source_type == "web" or not feed_url:
            diagnostic.status = "Nur Link" if source_url else "Nicht konfiguriert"
            diagnostic.message = "Referenzlink ohne automatisch lesbaren Feed oder Kalender."
            return empty_events(), diagnostic

        started = time.perf_counter()
        rows: list[dict[str, Any]] = []
        try:
            response = self._http.get(feed_url, headers=self._headers, timeout=25)
            diagnostic.http_status = response.status_code
            diagnostic.content_type = response.headers.get("Content-Type", "")

            if source_type == "ics":
                parsed = parse_ics_payload(response.content)
                diagnostic.entries = len(parsed)
                for item in parsed:
                    date_value = _parse_ics_datetime(item.get("DTSTART", ""))
                    if pd.isna(date_value):
                        continue
                    timestamp = pd.Timestamp(date_value)
                    if not earliest <= timestamp <= latest:
                        continue
                    title = str(item.get("SUMMARY") or "IR-Termin")
                    notes = str(item.get("DESCRIPTION") or "")
                    event_type = self._analyzer.classify_event(f"{title} {notes}")
                    rows.append(
                        self._base_row(
                            ticker=ticker,
                            date=timestamp,
                            event_type=event_type,
                            title=title,
                            source_name=source_name,
                            source_url=source_url or feed_url,
                            link=str(item.get("URL") or source_url or feed_url),
                            verification_level=verification_level,
                            source_type="company_calendar",
                            notes=notes,
                        )
                    )
            else:
                parsed_entries, parser_error = _parse_entries(response.content)
                if parser_error:
                    diagnostic.status = "Parser-Fehler"
                    diagnostic.message = parser_error
                    return empty_events(), diagnostic
                diagnostic.entries = len(parsed_entries)
                for entry in parsed_entries:
                    published = entry.get("published") or entry.get("updated")
                    timestamp = pd.to_datetime(published, errors="coerce", utc=True)
                    if pd.isna(timestamp):
                        parsed_struct = entry.get("published_parsed") or entry.get("updated_parsed")
                        if parsed_struct:
                            timestamp = pd.Timestamp(
                                datetime(
                                    parsed_struct.tm_year,
                                    parsed_struct.tm_mon,
                                    parsed_struct.tm_mday,
                                    parsed_struct.tm_hour,
                                    parsed_struct.tm_min,
                                    parsed_struct.tm_sec,
                                )
                            )
                    if pd.isna(timestamp):
                        continue
                    timestamp = pd.Timestamp(timestamp)
                    if timestamp.tzinfo is not None:
                        timestamp = timestamp.tz_localize(None)
                    if not earliest <= timestamp <= latest:
                        continue
                    title = str(entry.get("title", "") or "")
                    summary = str(entry.get("summary", "") or "")
                    event_type = self._analyzer.classify_event(f"{title} {summary}")
                    if event_type == "news":
                        continue
                    sentiment = self._analyzer.sentiment(title, summary)
                    row = self._base_row(
                        ticker=ticker,
                        date=timestamp,
                        event_type=event_type,
                        title=title,
                        source_name=source_name,
                        source_url=source_url or feed_url,
                        link=str(entry.get("link", "") or source_url or feed_url),
                        verification_level=verification_level,
                        source_type="company_feed",
                        notes=summary,
                    )
                    row.update(
                        {
                            "sentiment_score": sentiment.score,
                            "sentiment_label": sentiment.label,
                            "sentiment_confidence": sentiment.confidence,
                            "sentiment_reason": sentiment.reason,
                        }
                    )
                    rows.append(row)

            diagnostic.matches = len(rows)
            diagnostic.status = "OK" if rows else "Keine Kalenderereignisse"
            return pd.DataFrame(rows, columns=EVENT_COLUMNS), diagnostic
        except Exception as error:
            diagnostic.status = "Fehler"
            diagnostic.message = f"{type(error).__name__}: {error}"
            return empty_events(), diagnostic
        finally:
            diagnostic.duration_ms = round((time.perf_counter() - started) * 1000)

    def fetch(self, ticker: str, company_name: str, days_back: int, days_forward: int) -> EventFetchResult:
        sources = self._sources(ticker)
        if sources.empty:
            diagnostic = ProviderDiagnostic(
                source=self.name,
                kind="ir_registry",
                status="Nicht konfiguriert",
                url=str(self._path),
                message="Für diesen Ticker wurde noch kein offizieller RSS-/ICS-Link hinterlegt.",
            )
            return EventFetchResult(empty_events(), pd.DataFrame([diagnostic.to_dict()]))

        earliest = pd.Timestamp.now().normalize() - pd.Timedelta(days=int(days_back))
        latest = pd.Timestamp.now().normalize() + pd.Timedelta(days=int(days_forward))
        frames: list[pd.DataFrame] = []
        diagnostics: list[dict[str, Any]] = []
        for _, source in sources.iterrows():
            frame, diagnostic = self._fetch_source(source, ticker, earliest, latest)
            if not frame.empty:
                frames.append(frame)
            diagnostics.append(diagnostic.to_dict())

        events = pd.concat(frames, ignore_index=True) if frames else empty_events()
        return EventFetchResult(events, pd.DataFrame(diagnostics))
