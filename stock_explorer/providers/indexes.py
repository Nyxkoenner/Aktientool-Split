from __future__ import annotations

from abc import ABC, abstractmethod
from io import StringIO
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from .http import HttpClient, RequestsHttpClient
from .models import IndexLoadResult


class IndexProvider(ABC):
    name: str = "Unbekannt"

    @abstractmethod
    def load(self, index_name: str) -> IndexLoadResult:
        raise NotImplementedError


def _clean_ticker(value: Any) -> str:
    return str(value or "").strip().upper().replace("$", "")


def validate_constituents(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"name", "ticker_yahoo", "sector"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Indexdatei enthält nicht alle benötigten Spalten: {sorted(missing)}")
    result = frame[["name", "ticker_yahoo", "sector"]].copy()
    result["name"] = result["name"].astype(str).str.strip()
    result["ticker_yahoo"] = result["ticker_yahoo"].map(_clean_ticker)
    result["sector"] = result["sector"].fillna("Unbekannt").astype(str).str.strip()
    result = result[result["ticker_yahoo"].ne("")]
    return result.drop_duplicates(subset=["ticker_yahoo"]).reset_index(drop=True)


class CompositeIndexProvider(IndexProvider):
    """CSV -> integrierte Liste -> S&P-Onlinecache.

    Deutsche Indexlisten werden absichtlich nicht automatisch von Wikipedia
    abgerufen. Das vermeidet Rate-Limits und macht den App-Start reproduzierbar.
    """

    name = "CSV / Offline / S&P-Fallback"

    def __init__(
        self,
        *,
        local_paths: Mapping[str, Path],
        static_constituents: Mapping[str, Sequence[Mapping[str, Any]]],
        expected_counts: Mapping[str, int],
        cache_dir: Path,
        static_as_of: str,
        http_client: HttpClient | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._local_paths = dict(local_paths)
        self._static = {key: list(value) for key, value in static_constituents.items()}
        self._expected = dict(expected_counts)
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._static_as_of = static_as_of
        self._http = http_client or RequestsHttpClient()
        self._headers = headers or {}

    def _local(self, index_name: str) -> pd.DataFrame | None:
        path = self._local_paths.get(index_name)
        if path is None or not path.exists():
            return None
        try:
            frame = validate_constituents(pd.read_csv(path))
        except Exception:
            return None
        expected = self._expected.get(index_name, 0)
        minimum = expected if index_name in self._static else max(1, int(expected * 0.8))
        return frame if len(frame) >= minimum else None

    def source_description(self, index_name: str) -> str:
        local = self._local(index_name)
        if local is not None:
            return f"Lokale CSV: {self._local_paths[index_name]}"
        if index_name in self._static:
            return f"Integrierte Offline-Liste · Stand {self._static_as_of}"
        return "Online-Quelle mit lokalem Cache"

    def _load_sp500(self) -> IndexLoadResult:
        cache_path = self._cache_dir / "sp500_constituents.csv"
        if cache_path.exists():
            try:
                cached = validate_constituents(pd.read_csv(cache_path))
                if len(cached) >= 400:
                    return IndexLoadResult(cached, f"Lokaler Cache: {cache_path}")
            except Exception:
                pass

        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = self._http.get(url, headers=self._headers, timeout=25)
        tables = pd.read_html(StringIO(response.text))
        for table in tables:
            columns = [
                " ".join(map(str, item)) if isinstance(item, tuple) else str(item) for item in table.columns
            ]
            table = table.copy()
            table.columns = columns
            name_col = next((col for col in columns if col in {"Security", "Company", "Name"}), None)
            ticker_col = next((col for col in columns if col in {"Symbol", "Ticker", "Ticker symbol"}), None)
            sector_col = next((col for col in columns if col in {"GICS Sector", "Sector"}), None)
            if not (name_col and ticker_col and sector_col):
                continue
            frame = table[[name_col, ticker_col, sector_col]].copy()
            frame.columns = ["name", "ticker_yahoo", "sector"]
            frame["ticker_yahoo"] = frame["ticker_yahoo"].astype(str).str.replace(".", "-", regex=False)
            frame = validate_constituents(frame)
            if len(frame) < 400:
                continue
            try:
                frame.to_csv(cache_path, index=False)
            except Exception:
                pass
            return IndexLoadResult(frame, url)
        raise RuntimeError("Keine passende S&P-500-Tabelle gefunden.")

    def load(self, index_name: str) -> IndexLoadResult:
        local = self._local(index_name)
        if local is not None:
            return IndexLoadResult(local, f"Lokale CSV: {self._local_paths[index_name]}")

        if index_name in self._static:
            frame = validate_constituents(pd.DataFrame(self._static[index_name]))
            expected = self._expected.get(index_name)
            if expected is not None and len(frame) != expected:
                raise RuntimeError(
                    f"Interne {index_name}-Liste ist unvollständig: {len(frame)} statt {expected} Werte."
                )
            return IndexLoadResult(
                frame,
                f"Integrierte Offline-Liste · Stand {self._static_as_of}",
                as_of=self._static_as_of,
            )

        if index_name == "S&P 500":
            return self._load_sp500()

        raise ValueError(f"Unbekannter Index: {index_name}")
