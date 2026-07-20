from __future__ import annotations

import pandas as pd

from stock_explorer.domain.event_resolution import resolve_events


def test_official_duplicate_wins_over_provider():
    events = pd.DataFrame(
        [
            {
                "date": "2027-05-01",
                "ticker_yahoo": "AAA",
                "event_type": "earnings",
                "title": "Quarterly results",
                "source": "Yahoo",
                "verification_level": "data_provider",
                "verification_score": 65,
            },
            {
                "date": "2027-05-01",
                "ticker_yahoo": "AAA",
                "event_type": "earnings",
                "title": "Quarterly results",
                "source": "Company IR",
                "verification_level": "official_ir",
                "verification_score": 95,
            },
        ]
    )
    result = resolve_events(events)
    assert len(result) == 1
    assert result.iloc[0]["source"] == "Company IR"


def test_conflicting_future_dates_are_flagged():
    future = pd.Timestamp.now().normalize() + pd.Timedelta(days=60)
    events = pd.DataFrame(
        [
            {
                "date": future,
                "ticker_yahoo": "AAA",
                "event_type": "earnings",
                "title": "Results date",
                "source": "Company IR",
                "verification_level": "official_ir",
            },
            {
                "date": future + pd.Timedelta(days=5),
                "ticker_yahoo": "AAA",
                "event_type": "earnings",
                "title": "Expected results",
                "source": "Yahoo",
                "verification_level": "data_provider",
            },
        ]
    )
    result = resolve_events(events)
    assert set(result["event_status"]) == {"prüfen"}
    assert result["conflict_note"].str.contains("Abweichende").all()
