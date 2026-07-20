from __future__ import annotations

import pandas as pd

from stock_explorer.application import ScannerThresholds, SidebarSelection, selected_tickers


def test_sidebar_selection_limits_and_resets_index() -> None:
    frame = pd.DataFrame(
        {
            "ticker_yahoo": ["AAA", "BBB", "CCC"],
            "name": ["A", "B", "C"],
            "sector": ["X", "X", "Y"],
        },
        index=[10, 20, 30],
    )
    selection = SidebarSelection(
        index_name="Test",
        filtered_constituents=frame,
        max_stocks=2,
        profile_name="Balanced",
        thresholds=ScannerThresholds(25.0, 90.0, 65.0, 5.0),
        reload_clicked=False,
    )

    selected = selection.selected_constituents()

    assert selected["ticker_yahoo"].tolist() == ["AAA", "BBB"]
    assert selected.index.tolist() == [0, 1]


def test_selected_tickers_uses_cleaner_and_preserves_order() -> None:
    frame = pd.DataFrame({"ticker_yahoo": [" a.de ", "$b"]})

    result = selected_tickers(frame, lambda value: str(value).strip().upper().lstrip("$"))

    assert result == ("A.DE", "B")
