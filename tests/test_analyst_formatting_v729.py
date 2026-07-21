from __future__ import annotations

import pandas as pd

from stock_explorer.domain.analyst_formatting import (
    analyst_table_unit_caption,
    format_analyst_table,
    format_currency_amount,
    normalize_currency,
)


def test_currency_amount_uses_compact_units_and_currency() -> None:
    assert format_currency_amount(40_475_854_000, "EUR") == "40,5 Mrd. EUR"
    assert format_currency_amount(415.01, "EUR", compact=False) == "415,01 EUR"
    assert format_currency_amount(12.345, "EUR", compact=False, per_share=True) == "12,35 EUR/Aktie"


def test_revenue_estimates_include_amount_units_and_percentages() -> None:
    raw = pd.DataFrame(
        {
            "period": ["0q"],
            "avg": [40_475_854_000],
            "low": [39_000_000_000],
            "high": [42_000_000_000],
            "numberOfAnalysts": [4],
            "yearAgoRevenue": [41_600_000_000],
            "growth": [-0.0273],
            "currency": ["eur"],
        }
    )

    formatted = format_analyst_table(raw, "revenue", "EUR")

    assert formatted.loc[0, "Durchschnitt"] == "40,5 Mrd. EUR"
    assert formatted.loc[0, "Umsatz Vorjahr"] == "41,6 Mrd. EUR"
    assert formatted.loc[0, "Wachstum"] == "-2,7 %"
    assert formatted.loc[0, "Analysten"] == "4"
    assert formatted.loc[0, "Währung"] == "EUR"


def test_earnings_estimates_are_marked_per_share() -> None:
    raw = pd.DataFrame(
        {
            "period": ["+1y"],
            "avg": [28.4],
            "low": [26.0],
            "high": [31.2],
            "yearAgoEps": [25.0],
            "growth": [0.136],
        }
    )

    formatted = format_analyst_table(raw, "earnings", "EUR")

    assert formatted.loc[0, "Durchschnitt"] == "28,40 EUR/Aktie"
    assert formatted.loc[0, "Wachstum"] == "+13,6 %"


def test_growth_table_formats_all_comparison_columns_as_percentages() -> None:
    raw = pd.DataFrame(
        {
            "period": ["+5y"],
            "stock": [0.081],
            "industry": [0.052],
            "sector": [0.047],
            "index": [0.061],
        }
    )

    formatted = format_analyst_table(raw, "growth")

    assert formatted.loc[0, "Aktie"] == "+8,1 %"
    assert formatted.loc[0, "Branche"] == "+5,2 %"
    assert formatted.loc[0, "Sektor"] == "+4,7 %"
    assert formatted.loc[0, "Index"] == "+6,1 %"


def test_currency_and_captions_do_not_guess_missing_codes() -> None:
    assert normalize_currency("", None, "usd") == "USD"
    assert normalize_currency("Euro") == ""
    assert "EUR" in analyst_table_unit_caption("revenue", "EUR")
