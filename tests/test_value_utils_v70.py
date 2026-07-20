from __future__ import annotations

from datetime import date

import pandas as pd

from stock_explorer.domain.value_utils import (
    clean_ticker,
    deduplicate_dataframe_columns,
    display_text,
    format_number,
    safe_float,
    safe_session_date,
    to_percent,
)


def test_numeric_and_ticker_helpers() -> None:
    assert safe_float("12.5") == 12.5
    assert safe_float("x") is None
    assert to_percent(0.075) == 7.5
    assert to_percent(7.5) == 7.5
    assert clean_ticker(" $abc.de[1] ") == "ABC.DE"
    assert format_number(1234.5, 1) == "1.234,5"


def test_dataframe_and_display_helpers() -> None:
    frame = pd.DataFrame([[1, 2]], columns=["score", "score"])
    result = deduplicate_dataframe_columns(frame)

    assert result.columns.tolist() == ["score"]
    assert result.iloc[0, 0] == 2
    assert display_text(["A", "B"]) == "A | B"


def test_safe_session_date_rejects_nat_and_out_of_range() -> None:
    fallback = date(2025, 1, 1)

    assert safe_session_date(None, fallback) == fallback
    assert safe_session_date("2025-02-01", fallback) == date(2025, 2, 1)
    assert safe_session_date("2024-01-01", fallback, min_date=fallback) == fallback
