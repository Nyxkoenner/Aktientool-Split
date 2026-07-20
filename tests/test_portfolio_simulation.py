import pandas as pd

from stock_explorer.domain.portfolio_simulation import simulate_buy_and_hold


def test_buy_and_hold_curve():
    index = pd.date_range("2024-01-01", periods=3)
    prices = pd.DataFrame({"A": [100, 110, 121], "B": [100, 100, 100]}, index=index)
    result = simulate_buy_and_hold(prices, {"A": 0.5, "B": 0.5}, initial_capital=1000)
    assert result.final_value == 1105
    assert result.max_drawdown_pct == 0
