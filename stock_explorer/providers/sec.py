from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import pandas as pd

from .http import HttpClient, RequestsHttpClient
from .models import ProviderDiagnostic


class SecProvider(ABC):
    name: str = "SEC"

    @abstractmethod
    def company_map(self) -> tuple[dict[str, dict[str, Any]], str]:
        raise NotImplementedError

    @abstractmethod
    def recent_filings(self, ticker: str, days_back: int = 730) -> tuple[pd.DataFrame, ProviderDiagnostic]:
        raise NotImplementedError

    @abstractmethod
    def company_facts(self, ticker: str) -> tuple[dict[str, Any], ProviderDiagnostic]:
        raise NotImplementedError


def _clean_ticker(value: Any) -> str:
    return str(value or "").strip().upper().replace("$", "")


class SecEdgarProvider(SecProvider):
    name = "SEC EDGAR"

    def __init__(
        self,
        *,
        http_client: HttpClient | None = None,
        contact_email: str | None = None,
    ) -> None:
        self._http = http_client or RequestsHttpClient()
        email = contact_email or os.getenv("SEC_CONTACT_EMAIL", "contact@example.com")
        self._headers = {
            "User-Agent": f"AktienExplorer/6.2 {email}",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json,text/plain,*/*",
        }
        self._company_map_cache: dict[str, dict[str, Any]] | None = None

    def company_map(self) -> tuple[dict[str, dict[str, Any]], str]:
        if self._company_map_cache is not None:
            return self._company_map_cache.copy(), ""
        url = "https://www.sec.gov/files/company_tickers.json"
        try:
            response = self._http.get(url, headers=self._headers, timeout=25)
            payload = response.json()
            mapping: dict[str, dict[str, Any]] = {}
            iterable = payload.values() if isinstance(payload, dict) else payload
            for item in iterable:
                if not isinstance(item, dict):
                    continue
                ticker = _clean_ticker(item.get("ticker"))
                cik = item.get("cik_str")
                if ticker and cik is not None:
                    mapping[ticker] = {
                        "cik": int(cik),
                        "title": str(item.get("title", "")),
                    }
            self._company_map_cache = mapping
            return mapping.copy(), ""
        except Exception as error:
            return {}, f"{type(error).__name__}: {error}"

    def recent_filings(self, ticker: str, days_back: int = 730) -> tuple[pd.DataFrame, ProviderDiagnostic]:
        symbol = _clean_ticker(ticker)
        diagnostic = ProviderDiagnostic(
            source=self.name,
            kind="official_regulator",
            status="Nicht verfügbar",
            url="https://data.sec.gov/",
        )
        if not symbol or "." in symbol:
            diagnostic.message = "Nur SEC-gemappte US-Ticker und ADRs ohne Börsensuffix."
            return pd.DataFrame(), diagnostic

        started = time.perf_counter()
        try:
            company_map, error = self.company_map()
            if error:
                raise RuntimeError(error)
            match = company_map.get(symbol)
            if not match:
                diagnostic.message = f"Kein SEC-CIK für {symbol} gefunden."
                return pd.DataFrame(), diagnostic

            cik = int(match["cik"])
            url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
            diagnostic.url = url
            response = self._http.get(url, headers=self._headers, timeout=25)
            diagnostic.http_status = response.status_code
            payload = response.json()
            recent = payload.get("filings", {}).get("recent", {})
            forms = list(recent.get("form", []))
            dates = list(recent.get("filingDate", []))
            accessions = list(recent.get("accessionNumber", []))
            docs = list(recent.get("primaryDocument", []))
            descriptions = list(recent.get("primaryDocDescription", []))
            diagnostic.entries = len(forms)
            cutoff = pd.Timestamp.now().normalize() - pd.Timedelta(days=int(days_back))
            rows: list[dict[str, Any]] = []
            for position, form in enumerate(forms):
                filing_date = dates[position] if position < len(dates) else None
                parsed_date = pd.to_datetime(filing_date, errors="coerce")
                if pd.isna(parsed_date) or pd.Timestamp(parsed_date).normalize() < cutoff:
                    continue
                accession = accessions[position] if position < len(accessions) else ""
                document = docs[position] if position < len(docs) else ""
                description = descriptions[position] if position < len(descriptions) else ""
                accession_compact = str(accession).replace("-", "")
                filing_link = (
                    f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_compact}/{document}"
                    if accession_compact and document
                    else url
                )
                rows.append(
                    {
                        "filing_date": pd.Timestamp(parsed_date).tz_localize(None),
                        "ticker": symbol,
                        "cik": cik,
                        "form": str(form),
                        "accession": str(accession),
                        "document": str(document),
                        "description": str(description),
                        "link": filing_link,
                        "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                )
            frame = pd.DataFrame(rows)
            diagnostic.matches = len(frame)
            diagnostic.status = "OK" if not frame.empty else "Keine relevanten Filings"
            return frame, diagnostic
        except Exception as error:
            diagnostic.status = "Fehler"
            diagnostic.message = f"{type(error).__name__}: {error}"
            return pd.DataFrame(), diagnostic
        finally:
            diagnostic.duration_ms = round((time.perf_counter() - started) * 1000)

    def company_facts(self, ticker: str) -> tuple[dict[str, Any], ProviderDiagnostic]:
        symbol = _clean_ticker(ticker)
        diagnostic = ProviderDiagnostic(
            source=self.name,
            kind="official_company_facts",
            status="Nicht verfügbar",
            url="https://data.sec.gov/api/xbrl/companyfacts/",
        )
        if not symbol or "." in symbol:
            diagnostic.message = "Nur SEC-gemappte US-Ticker und ADRs ohne Börsensuffix."
            return {}, diagnostic

        started = time.perf_counter()
        try:
            company_map, error = self.company_map()
            if error:
                raise RuntimeError(error)
            match = company_map.get(symbol)
            if not match:
                diagnostic.message = f"Kein SEC-CIK für {symbol} gefunden."
                return {}, diagnostic
            cik = int(match["cik"])
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
            diagnostic.url = url
            response = self._http.get(url, headers=self._headers, timeout=30)
            diagnostic.http_status = response.status_code
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("SEC Company Facts enthält kein JSON-Objekt.")
            diagnostic.entries = len(payload.get("facts", {}).get("us-gaap", {}))
            diagnostic.matches = diagnostic.entries
            diagnostic.status = "OK" if diagnostic.entries else "Keine Company Facts"
            return payload, diagnostic
        except Exception as error:
            diagnostic.status = "Fehler"
            diagnostic.message = f"{type(error).__name__}: {error}"
            return {}, diagnostic
        finally:
            diagnostic.duration_ms = round((time.perf_counter() - started) * 1000)
