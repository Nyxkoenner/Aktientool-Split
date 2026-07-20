import pandas as pd

from stock_explorer.domain.portfolio_simulation import simulate_buy_and_hold


def test_costs_and_dividends_are_reported() -> None:
    index = pd.date_range("2024-01-01", periods=260, freq="B")
    prices = pd.DataFrame({"AAA": range(100, 360), "BBB": range(200, 460)}, index=index)
    result = simulate_buy_and_hold(
        prices,
        {"AAA": 0.5, "BBB": 0.5},
        10_000,
        "Q",
        10,
        {"AAA": 2.0, "BBB": 4.0},
    )
    assert result.final_value > 0
    assert result.transaction_costs > 0
    assert result.dividends_received > 0
