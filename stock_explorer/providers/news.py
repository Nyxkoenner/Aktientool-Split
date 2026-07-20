from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import quote_plus

try:
    import feedparser
except ModuleNotFoundError:  # isolierte Tests oder Minimalinstallation
    feedparser = None

from .http import HttpClient, RequestsHttpClient
from .models import NewsEntry, NewsFetchResult, ProviderDiagnostic


class NewsProvider(ABC):
    name: str
    kind: str

    @abstractmethod
    def fetch(self) -> NewsFetchResult:
        raise NotImplementedError


def _parse_datetime(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = parsedate_to_datetime(raw)
    except (TypeError, ValueError, OverflowError):
        parsed = None
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _entry_datetime(entry: Any) -> datetime | None:
    raw = entry.get("published") or entry.get("updated")
    parsed = _parse_datetime(raw)
    if parsed is not None:
        return parsed

    for field in ("published_parsed", "updated_parsed"):
        parsed_struct = entry.get(field)
        if not parsed_struct:
            continue
        try:
            return datetime(
                parsed_struct.tm_year,
                parsed_struct.tm_mon,
                parsed_struct.tm_mday,
                parsed_struct.tm_hour,
                parsed_struct.tm_min,
                parsed_struct.tm_sec,
                tzinfo=timezone.utc,
            )
        except Exception:
            continue
    return None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _child_text(element: ET.Element, names: set[str]) -> str:
    for child in element.iter():
        if _local_name(child.tag) in names and child.text:
            return child.text.strip()
    return ""


def _xml_entries(payload: bytes) -> list[dict[str, Any]]:
    root = ET.fromstring(payload)
    result: list[dict[str, Any]] = []
    for element in root.iter():
        if _local_name(element.tag) not in {"item", "entry"}:
            continue
        link = _child_text(element, {"link"})
        if not link:
            for child in element:
                if _local_name(child.tag) == "link" and child.attrib.get("href"):
                    link = str(child.attrib["href"])
                    break
        result.append(
            {
                "title": _child_text(element, {"title"}),
                "summary": _child_text(element, {"description", "summary", "content"}),
                "link": link,
                "published": _child_text(element, {"pubdate", "published", "updated"}),
            }
        )
    return result


def _parse_entries(payload: bytes) -> tuple[list[Any], str | None]:
    if feedparser is not None:
        parsed = feedparser.parse(payload)
        if getattr(parsed, "bozo", False) and not getattr(parsed, "entries", []):
            error = getattr(parsed, "bozo_exception", None)
            return [], f"{type(error).__name__ if error else 'unbekannter Parserfehler'}"
        return list(getattr(parsed, "entries", [])), None
    try:
        return _xml_entries(payload), None
    except ET.ParseError as error:
        return [], f"ParseError: {error}"


class RssNewsProvider(NewsProvider):
    def __init__(
        self,
        *,
        name: str,
        url: str,
        kind: str = "global",
        http_client: HttpClient | None = None,
        headers: dict[str, str] | None = None,
        timeout: int = 20,
    ) -> None:
        self.name = name
        self.url = url
        self.kind = kind
        self._http = http_client or RequestsHttpClient()
        self._headers = headers or {}
        self._timeout = timeout

    def fetch(self) -> NewsFetchResult:
        started = time.perf_counter()
        diagnostic = ProviderDiagnostic(
            source=self.name,
            kind=self.kind,
            status="Fehler",
            url=self.url,
        )
        try:
            response = self._http.get(
                self.url,
                headers=self._headers,
                timeout=self._timeout,
            )
            diagnostic.http_status = response.status_code
            diagnostic.content_type = response.headers.get("Content-Type", "")
            parsed_entries, parser_error = _parse_entries(response.content)
            if parser_error:
                diagnostic.status = "Parser-Fehler"
                diagnostic.message = parser_error
                return NewsFetchResult(diagnostic=diagnostic)

            entries: list[NewsEntry] = []
            for entry in parsed_entries:
                published = _entry_datetime(entry)
                title = str(entry.get("title", "") or "").strip()
                if published is None or not title:
                    continue
                entries.append(
                    NewsEntry(
                        published=published,
                        title=title,
                        summary=str(entry.get("summary", "") or "").strip(),
                        link=str(entry.get("link", "") or "").strip(),
                        source=self.name,
                        source_kind=self.kind,
                    )
                )
            diagnostic.entries = len(entries)
            diagnostic.status = "OK" if entries else "Keine Einträge"
            return NewsFetchResult(entries=entries, diagnostic=diagnostic)
        except Exception as error:
            diagnostic.message = f"{type(error).__name__}: {error}"
            return NewsFetchResult(diagnostic=diagnostic)
        finally:
            diagnostic.duration_ms = round((time.perf_counter() - started) * 1000)


class GoogleNewsSearchProvider(RssNewsProvider):
    def __init__(
        self,
        *,
        query: str,
        locale: str = "de",
        display_name: str | None = None,
        http_client: HttpClient | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        language = "en" if locale == "en" else "de"
        country = "US" if language == "en" else "DE"
        url = (
            "https://news.google.com/rss/search?"
            f"q={quote_plus(query)}&hl={language}&gl={country}&ceid={country}:{language}"
        )
        super().__init__(
            name=display_name or f"Google News: {query}",
            url=url,
            kind="search_fallback",
            http_client=http_client,
            headers=headers,
        )
