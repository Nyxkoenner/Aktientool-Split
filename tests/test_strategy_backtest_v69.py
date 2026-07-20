import numpy as np
import pandas as pd

from stock_explorer.domain.ai_features import build_feature_frame
from stock_explorer.domain.strategy_backtest import baseline_positions, simulate_positions


def _features() -> pd.DataFrame:
    index = pd.bdate_range("2018-01-01", periods=1100)
    prices = 100 * np.exp(np.linspace(0, 0.7, len(index)) + 0.08 * np.sin(np.arange(len(index)) / 30))
    return build_feature_frame(pd.DataFrame({"Close": prices}, index=index)).frame


def test_baselines_and_costs() -> None:
    features = _features()
    positions = baseline_positions(features)
    assert set(positions) == {"buy_hold", "momentum", "recovery", "combined"}
    without_costs = simulate_positions(
        features, positions["momentum"], name="momentum", transaction_cost_bps=0
    )
    with_costs = simulate_positions(features, positions["momentum"], name="momentum", transaction_cost_bps=25)
    assert with_costs.metrics.total_return_pct <= without_costs.metrics.total_return_pct
    assert with_costs.metrics.trades >= 1
    assert 0 <= with_costs.metrics.exposure_pct <= 100
