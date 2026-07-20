from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

import pandas as pd

from stock_explorer.providers.models import NewsFetchResult
from stock_explorer.providers.news import NewsProvider


class NewsService:
    def __init__(self, providers: Sequence[NewsProvider]) -> None:
        self._providers = list(providers)

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

    @property
    def provider_names(self) -> list[str]:
        return [provider.name for provider in self._providers]


def filter_since(frame: pd.DataFrame, cutoff: datetime) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame(columns=getattr(frame, "columns", None))
    result = frame.copy()
    result["published"] = pd.to_datetime(result["published"], errors="coerce")
    return result[result["published"] >= pd.Timestamp(cutoff).tz_localize(None)].copy()
