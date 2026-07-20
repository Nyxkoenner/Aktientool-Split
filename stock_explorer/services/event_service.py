from __future__ import annotations

import pandas as pd

from stock_explorer.domain.event_resolution import resolve_events
from stock_explorer.providers.events import EVENT_COLUMNS, EventProvider, empty_events


class EventService:
    def __init__(self, providers: list[EventProvider]) -> None:
        self._providers = list(providers)

    def fetch(
        self,
        ticker: str,
        company_name: str,
        *,
        days_back: int = 730,
        days_forward: int = 365,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        event_frames: list[pd.DataFrame] = []
        diagnostic_frames: list[pd.DataFrame] = []
        for provider in self._providers:
            result = provider.fetch(ticker, company_name, days_back, days_forward)
            if result.events is not None and not result.events.empty:
                event_frames.append(result.events)
            if result.diagnostics is not None and not result.diagnostics.empty:
                diagnostic_frames.append(result.diagnostics)
        events = pd.concat(event_frames, ignore_index=True) if event_frames else empty_events()
        if not events.empty:
            events = resolve_events(events)
        diagnostics = pd.concat(diagnostic_frames, ignore_index=True) if diagnostic_frames else pd.DataFrame()
        return events.reindex(columns=EVENT_COLUMNS), diagnostics

    @property
    def provider_names(self) -> list[str]:
        return [provider.name for provider in self._providers]
