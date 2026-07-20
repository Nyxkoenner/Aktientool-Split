from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from stock_explorer.services.event_service import EventService
from stock_explorer.services.index_service import IndexService
from stock_explorer.services.news_service import NewsService
from stock_explorer.services.profile_service import CompanyProfileService

from .base import MarketDataProvider
from .company_profiles import YahooCompanyProfileProvider
from .events import ManualCsvEventProvider, SecFilingEventProvider, YahooCalendarEventProvider
from .fx import FxProvider, YahooFxProvider
from .http import HttpClient
from .indexes import CompositeIndexProvider
from .news import GoogleNewsSearchProvider, RssNewsProvider
from .sec import SecEdgarProvider, SecProvider
from .yahoo import YahooMarketDataProvider


def _configured(name: str, default: str) -> str:
    return os.environ.get(name, default).strip().lower()


def get_market_provider(name: str | None = None) -> MarketDataProvider:
    provider_name = (name or _configured("AKTIEN_EXPLORER_MARKET_PROVIDER", "yahoo")).strip().lower()
    if provider_name == "yahoo":
        return YahooMarketDataProvider()
    raise ValueError(f"Unbekannter Marktdatenanbieter: {provider_name}. Aktuell verfügbar: yahoo")


def get_fx_provider(name: str | None = None) -> FxProvider:
    provider_name = (name or _configured("AKTIEN_EXPLORER_FX_PROVIDER", "yahoo")).strip().lower()
    if provider_name == "yahoo":
        return YahooFxProvider()
    raise ValueError(f"Unbekannter FX-Anbieter: {provider_name}. Aktuell verfügbar: yahoo")


def get_sec_provider(
    name: str | None = None,
    *,
    http_client: HttpClient | None = None,
) -> SecProvider:
    provider_name = (name or _configured("AKTIEN_EXPLORER_SEC_PROVIDER", "sec_edgar")).strip().lower()
    if provider_name in {"sec", "sec_edgar", "edgar"}:
        return SecEdgarProvider(http_client=http_client)
    raise ValueError(f"Unbekannter SEC-Anbieter: {provider_name}. Aktuell verfügbar: sec_edgar")


def get_profile_service(name: str | None = None) -> CompanyProfileService:
    provider_name = (name or _configured("AKTIEN_EXPLORER_PROFILE_PROVIDER", "yahoo")).strip().lower()
    if provider_name == "yahoo":
        return CompanyProfileService([YahooCompanyProfileProvider()])
    raise ValueError(f"Unbekannter Profilanbieter: {provider_name}. Aktuell verfügbar: yahoo")


def get_index_service(
    *,
    local_paths: Mapping[str, Path],
    static_constituents: Mapping[str, Sequence[Mapping[str, Any]]],
    expected_counts: Mapping[str, int],
    cache_dir: Path,
    static_as_of: str,
    headers: dict[str, str] | None = None,
    http_client: HttpClient | None = None,
) -> IndexService:
    provider = CompositeIndexProvider(
        local_paths=local_paths,
        static_constituents=static_constituents,
        expected_counts=expected_counts,
        cache_dir=cache_dir,
        static_as_of=static_as_of,
        headers=headers,
        http_client=http_client,
    )
    return IndexService(provider)


def get_news_service(
    *,
    global_sources: list[dict[str, str]],
    headers: dict[str, str] | None = None,
    google_query: str | None = None,
    locale: str = "de",
    http_client: HttpClient | None = None,
) -> NewsService:
    providers = [
        RssNewsProvider(
            name=source["name"],
            url=source["url"],
            kind=source.get("kind", "global"),
            headers=headers,
            http_client=http_client,
        )
        for source in global_sources
    ]
    if google_query:
        providers.append(
            GoogleNewsSearchProvider(
                query=google_query,
                locale=locale,
                display_name=f"Google News Suche: {google_query.strip(chr(34))}",
                headers=headers,
                http_client=http_client,
            )
        )
    return NewsService(providers)


def get_event_service(
    *,
    manual_events_path: Path,
    sec_provider: SecProvider | None = None,
) -> EventService:
    sec = sec_provider or get_sec_provider()
    return EventService(
        [
            ManualCsvEventProvider(manual_events_path),
            YahooCalendarEventProvider(),
            SecFilingEventProvider(sec),
        ]
    )
