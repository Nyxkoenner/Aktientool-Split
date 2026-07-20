from __future__ import annotations

import pandas as pd

from stock_explorer.services.universe_session import UniverseSessionStore


def test_universe_store_refresh_save_snapshot_and_clear() -> None:
    state: dict[str, object] = {}
    store = UniverseSessionStore(state)
    selected = pd.DataFrame({"ticker_yahoo": ["AAA"]})
    metrics = pd.DataFrame({"ticker_yahoo": ["AAA"], "last_price": [10.0]})
    histories = {"AAA": pd.DataFrame({"Close": [10.0]})}

    assert store.needs_refresh(("AAA",), reload_clicked=False)

    store.save(
        raw_metrics=metrics,
        histories=histories,
        selected_tickers=("AAA",),
        errors=["Hinweis"],
        selected_constituents=selected,
        last_refresh="01.01.2026 10:00",
    )

    assert not store.needs_refresh(("AAA",), reload_clicked=False)
    assert store.needs_refresh(("AAA",), reload_clicked=True)
    snapshot = store.snapshot(pd.DataFrame())
    assert snapshot.raw_metrics is metrics
    assert snapshot.histories is histories
    assert snapshot.errors == ["Hinweis"]
    assert snapshot.loaded_tickers == ("AAA",)

    store.clear()
    assert state == {}


def test_universe_store_uses_fallback_for_invalid_state_values() -> None:
    fallback = pd.DataFrame({"ticker_yahoo": ["BBB"]})
    state: dict[str, object] = {
        "metrics_raw": "invalid",
        "histories": [],
        "load_errors": "invalid",
        "selected_constituents_snapshot": "invalid",
    }

    snapshot = UniverseSessionStore(state).snapshot(fallback)

    assert snapshot.raw_metrics is None
    assert snapshot.histories == {}
    assert snapshot.errors == []
    assert snapshot.selected_constituents is fallback
