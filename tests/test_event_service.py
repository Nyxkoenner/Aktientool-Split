from __future__ import annotations

from pathlib import Path

import pandas as pd

from stock_explorer.providers.events import ManualCsvEventProvider
from stock_explorer.services.event_service import EventService


def test_manual_event_provider_filters_ticker(tmp_path: Path):
    path = tmp_path / "manual_events.csv"
    pd.DataFrame(
        [
            {
                "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                "ticker_yahoo": "AAA.DE",
                "event_type": "earnings",
                "title": "Quartalszahlen",
                "source": "IR",
            },
            {
                "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                "ticker_yahoo": "BBB.DE",
                "event_type": "dividend",
                "title": "Dividende",
                "source": "IR",
            },
        ]
    ).to_csv(path, index=False)

    service = EventService([ManualCsvEventProvider(path)])
    events, diagnostics = service.fetch("AAA.DE", "Alpha", days_back=30, days_forward=30)

    assert len(events) == 1
    assert events.iloc[0]["ticker_yahoo"] == "AAA.DE"
    assert diagnostics.iloc[0]["status"] == "OK"
