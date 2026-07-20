from __future__ import annotations

import hashlib
import io
import os
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup
from pypdf import PdfReader

from .http import HttpClient, RequestsHttpClient
from .models import ProviderDiagnostic
from .sec import SecProvider


@dataclass(slots=True)
class AnnualReportDocument:
    ticker: str
    filename: str
    source: str
    source_url: str
    content_type: str
    text: str
    retrieved_at: str
    page_count: int | None
    sha256: str

    def to_dict(self, *, include_text: bool = True) -> dict[str, Any]:
        payload = asdict(self)
        if not include_text:
            payload.pop("text", None)
        return payload


@dataclass(slots=True)
class AnnualReportFetchResult:
    document: AnnualReportDocument | None
    diagnostic: ProviderDiagnostic


class AnnualReportProvider(ABC):
    name: str = "Annual Report"

    @abstractmethod
    def fetch_latest(self, ticker: str) -> AnnualReportFetchResult:
        raise NotImplementedError


def _clean_ticker(value: Any) -> str:
    return str(value or "").strip().upper().replace("$", "")


def _hash_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _html_to_text(payload: bytes) -> str:
    soup = BeautifulSoup(payload, "lxml")
    for node in soup(["script", "style", "noscript", "svg"]):
        node.decompose()
    return soup.get_text("\n", strip=True)


def _pdf_to_text(payload: bytes) -> tuple[str, int]:
    reader = PdfReader(io.BytesIO(payload))
    pages: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append(f"\n[PAGE {page_number}]\n{text}")
    return "\n".join(pages).strip(), len(reader.pages)


def document_from_bytes(
    ticker: str,
    filename: str,
    payload: bytes,
    *,
    source: str = "Upload",
    source_url: str = "",
    content_type: str = "",
) -> AnnualReportDocument:
    name = Path(filename or "report").name
    suffix = Path(name).suffix.lower()
    detected_type = content_type.lower().split(";", 1)[0].strip()
    page_count: int | None = None
    if suffix == ".pdf" or detected_type == "application/pdf":
        text, page_count = _pdf_to_text(payload)
        detected_type = "application/pdf"
    elif suffix in {".html", ".htm"} or "html" in detected_type:
        text = _html_to_text(payload)
        detected_type = "text/html"
    else:
        text = payload.decode("utf-8", errors="replace")
        detected_type = detected_type or "text/plain"
    return AnnualReportDocument(
        ticker=_clean_ticker(ticker),
        filename=name,
        source=source,
        source_url=source_url,
        content_type=detected_type,
        text=text,
        retrieved_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        page_count=page_count,
        sha256=_hash_bytes(payload),
    )


class SecAnnualReportProvider(AnnualReportProvider):
    name = "SEC Annual Report"
    _FORMS = ("10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A")

    def __init__(
        self,
        sec_provider: SecProvider,
        *,
        http_client: HttpClient | None = None,
        contact_email: str | None = None,
    ) -> None:
        self._sec = sec_provider
        self._http = http_client or RequestsHttpClient()
        email = contact_email or os.getenv("SEC_CONTACT_EMAIL", "contact@example.com")
        self._headers = {
            "User-Agent": f"AktienExplorer/6.7 {email}",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/pdf,text/plain,*/*",
        }

    def fetch_latest(self, ticker: str) -> AnnualReportFetchResult:
        symbol = _clean_ticker(ticker)
        diagnostic = ProviderDiagnostic(
            source=self.name,
            kind="official_annual_report",
            status="Nicht verfügbar",
            url="https://www.sec.gov/edgar/search/",
        )
        started = time.perf_counter()
        try:
            filings, filing_diagnostic = self._sec.recent_filings(symbol, days_back=3650)
            if filing_diagnostic.message and filings.empty:
                diagnostic.message = filing_diagnostic.message
                diagnostic.http_status = filing_diagnostic.http_status
                return AnnualReportFetchResult(None, diagnostic)
            if filings.empty or "form" not in filings.columns:
                diagnostic.message = "Kein Jahresbericht in den SEC-Filings gefunden."
                return AnnualReportFetchResult(None, diagnostic)
            frame = filings.copy()
            frame["form"] = frame["form"].astype(str).str.upper()
            frame["filing_date"] = pd.to_datetime(frame.get("filing_date"), errors="coerce")
            frame = frame[frame["form"].isin(self._FORMS)].sort_values("filing_date", ascending=False)
            if frame.empty:
                diagnostic.message = "Kein 10-K-, 20-F- oder 40-F-Bericht gefunden."
                return AnnualReportFetchResult(None, diagnostic)
            row = frame.iloc[0]
            url = str(row.get("link") or "")
            if not url:
                diagnostic.message = "SEC-Filing enthält keinen Dokumentlink."
                return AnnualReportFetchResult(None, diagnostic)
            diagnostic.url = url
            response = self._http.get(url, headers=self._headers, timeout=45)
            diagnostic.http_status = response.status_code
            content_type = next(
                (value for key, value in response.headers.items() if key.lower() == "content-type"),
                "",
            )
            filename = str(row.get("document") or Path(url).name or f"{symbol}_annual_report.html")
            document = document_from_bytes(
                symbol,
                filename,
                response.content,
                source=f"SEC {row.get('form', '')}".strip(),
                source_url=url,
                content_type=content_type,
            )
            diagnostic.content_type = document.content_type
            diagnostic.entries = 1
            diagnostic.matches = 1
            diagnostic.status = "OK" if document.text.strip() else "Kein Text"
            if not document.text.strip():
                diagnostic.message = "Dokument geladen, aber kein Text extrahiert."
            return AnnualReportFetchResult(document, diagnostic)
        except Exception as error:
            diagnostic.status = "Fehler"
            diagnostic.message = f"{type(error).__name__}: {error}"
            return AnnualReportFetchResult(None, diagnostic)
        finally:
            diagnostic.duration_ms = round((time.perf_counter() - started) * 1000)
