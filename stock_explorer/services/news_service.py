from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime

import pandas as pd

from stock_explorer.domain.news_analysis import NewsAnalyzer
from stock_explorer.providers.models import NewsFetchResult
from stock_explorer.providers.news import NewsProvider


class NewsService:
    def __init__(
        self,
        providers: Sequence[NewsProvider],
        *,
        analyzer: NewsAnalyzer | None = None,
    ) -> None:
        self._providers = list(providers)
        self._analyzer = analyzer or NewsAnalyzer()

    def fetch_raw(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        rows: list[dict[str, object]] = []
        diagnostics: list[dict[str, object]] = []
        for provider in self._providers:
            result: NewsFetchResult = provider.fetch()
            if result.diagnostic is not None:
                diagnostics.append(result.diagnostic.to_dict())
            rows.extend(entry.to_dict() for entry in result.entries)
        news = pd.DataFrame(rows)
        if not news.empty:
            news["published"] = pd.to_datetime(news["published"], errors="coerce", utc=True)
            news = news.dropna(subset=["published", "title"])
            news["published"] = news["published"].dt.tz_convert(None)
            news = news.sort_values("published", ascending=False).reset_index(drop=True)
        diagnostic_frame = pd.DataFrame(diagnostics)
        return news, diagnostic_frame

    def fetch_company_news(
        self,
        *,
        ticker: str,
        company_name: str,
        cutoff: datetime,
        extra_aliases: Iterable[str] = (),
        max_items: int = 80,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        raw_news, diagnostics = self.fetch_raw()
        if not raw_news.empty:
            raw_news = filter_since(raw_news, cutoff)
        enriched = self._analyzer.enrich(
            raw_news,
            ticker=ticker,
            company_name=company_name,
            extra_aliases=extra_aliases,
            max_items=max_items,
        )

        diagnostics = diagnostics.copy()
        for column in ["matches", "uncertain_matches"]:
            if column not in diagnostics.columns:
                diagnostics[column] = 0
        if not diagnostics.empty:
            for source in diagnostics.get("source", pd.Series(dtype=str)).astype(str).unique():
                source_rows = enriched[enriched.get("source", pd.Series(dtype=str)).astype(str).eq(source)]
                relevant = int(source_rows.get("is_relevant", pd.Series(dtype=bool)).fillna(False).sum())
                uncertain = int(len(source_rows) - relevant)
                mask = diagnostics["source"].astype(str).eq(source)
                diagnostics.loc[mask, "matches"] = relevant
                diagnostics.loc[mask, "uncertain_matches"] = uncertain
                if relevant == 0 and uncertain > 0:
                    diagnostics.loc[mask, "status"] = "Nur unsichere Treffer"
                    diagnostics.loc[mask, "message"] = (
                        "Treffer mit schwachem Firmenbezug werden standardmäßig ausgeblendet."
                    )
                elif relevant == 0 and diagnostics.loc[mask, "status"].eq("OK").any():
                    diagnostics.loc[mask, "status"] = "Keine Firmen-Treffer"
        return enriched, diagnostics

    @property
    def provider_names(self) -> list[str]:
        return [provider.name for provider in self._providers]


def filter_since(frame: pd.DataFrame, cutoff: datetime) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame(columns=getattr(frame, "columns", None))
    result = frame.copy()
    result["published"] = pd.to_datetime(result["published"], errors="coerce")
    cutoff_timestamp = pd.Timestamp(cutoff)
    if cutoff_timestamp.tzinfo is not None:
        cutoff_timestamp = cutoff_timestamp.tz_localize(None)
    return result[result["published"] >= cutoff_timestamp].copy()
