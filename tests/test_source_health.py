from __future__ import annotations

import pandas as pd

from stock_explorer.services.source_health import enrich_diagnostics, source_health_score


def test_successful_source_has_high_health_score():
    score = source_health_score({"status": "OK", "http_status": 200, "entries": 20, "matches": 3})
    assert score >= 80


def test_failed_source_has_low_health_score():
    score = source_health_score({"status": "Fehler", "http_status": 403, "entries": 0, "matches": 0})
    assert score < 55


def test_enrich_diagnostics_adds_label():
    frame = enrich_diagnostics(
        pd.DataFrame([{"status": "OK", "http_status": 200, "entries": 2, "matches": 1}])
    )
    assert frame.iloc[0]["health_label"] == "stabil"
