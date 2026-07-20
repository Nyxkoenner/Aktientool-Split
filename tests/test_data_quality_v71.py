from __future__ import annotations

import numpy as np
import pandas as pd

from stock_explorer.domain.data_quality import assess_price_history


def test_complete_recent_business_day_history_is_good() -> None:
    index = pd.bdate_range("2021-01-01", periods=900)
    history = pd.DataFrame({"Close": 100 + np.arange(len(index)) * 0.1}, index=index)

    report = assess_price_history(history, as_of=index[-1])

    assert report.level == "good"
    assert report.score >= 85
    assert report.observations == 900
    assert report.missing_business_days == 0


def test_quality_report_detects_invalid_prices_duplicates_and_staleness() -> None:
    index = pd.DatetimeIndex(["2020-01-01", "2020-01-02", "2020-01-02", "2020-01-06"])
    history = pd.Series([100.0, -1.0, 101.0, float("nan")], index=index)

    report = assess_price_history(history, as_of="2021-01-01")

    assert report.level == "poor"
    assert report.duplicate_rows >= 2
    assert report.nonpositive_rows == 1
    assert "stale" in report.issues
    assert "short_history" in report.issues
