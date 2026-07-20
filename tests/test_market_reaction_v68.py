from __future__ import annotations

import pandas as pd

from stock_explorer.domain.market_reaction import compute_market_reactions


def test_market_reaction_and_excess_return() -> None:
    index = pd.date_range("2026-01-01", periods=40, freq="B")
    stock = pd.DataFrame({"Close": [100 + value for value in range(40)]}, index=index)
    benchmark = pd.DataFrame({"Close": [100 + value * 0.5 for value in range(40)]}, index=index)
    events = pd.DataFrame([{"cluster_id": "abc", "published": pd.Timestamp("2026-01-05"), "title": "Event"}])
    result = compute_market_reactions(events, stock, benchmark)
    assert result.iloc[0]["return_5d"] > 0
    assert result.iloc[0]["excess_return_5d"] > 0
    assert pd.notna(result.iloc[0]["reaction_trade_date"])
