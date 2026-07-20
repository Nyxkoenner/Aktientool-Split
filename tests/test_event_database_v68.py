from __future__ import annotations

import pandas as pd

from stock_explorer.services.event_database import EventDatabase


def test_event_database_deduplicates_clusters(tmp_path) -> None:
    database = EventDatabase(tmp_path / "events")
    events = pd.DataFrame(
        [{"cluster_id": "same", "published": "2026-01-01", "title": "First", "summary": "x" * 1000}]
    )
    articles = pd.DataFrame(
        [
            {
                "published": "2026-01-01",
                "title": "First",
                "summary": "y" * 1000,
                "link": "https://example.com/1",
            }
        ]
    )
    database.save("TEST", events, articles)
    database.save("TEST", events.assign(title="Updated"), articles)
    snapshot = database.load("TEST")
    assert len(snapshot.events) == 1
    assert snapshot.events.iloc[0]["title"] == "Updated"
    assert len(str(snapshot.events.iloc[0]["summary"])) == 800
