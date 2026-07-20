from __future__ import annotations

import numpy as np
import pandas as pd

from stock_explorer.domain.rl_qlearning import (
    QLearningConfig,
    continue_q_learning,
    train_q_learning,
)


def _features(rows: int = 180) -> pd.DataFrame:
    index = pd.bdate_range("2024-01-01", periods=rows)
    returns = np.sin(np.arange(rows) / 13.0) / 100.0
    close = 100.0 * np.cumprod(1.0 + returns)
    return pd.DataFrame(
        {
            "close": close,
            "asset_return": returns,
            "return_20d": pd.Series(close, index=index).pct_change(20).fillna(0.0),
            "volatility_20d": 0.20 + np.cos(np.arange(rows) / 19.0) / 50.0,
            "sma50_to_sma200": np.sin(np.arange(rows) / 31.0) / 20.0,
            "drawdown": pd.Series(close, index=index) / pd.Series(close, index=index).cummax() - 1.0,
        },
        index=index,
    )


def test_continuation_keeps_discretizer_and_does_not_mutate_original() -> None:
    config = QLearningConfig(episodes=2, seed=7)
    model = train_q_learning(_features(), config)
    original_table = {state: values.copy() for state, values in model.q_table.items()}

    updated = continue_q_learning(model, _features().tail(12), episodes=3, seed=8)

    assert updated.discretizer == model.discretizer
    assert updated.config.episodes == 3
    assert updated.config.seed == 8
    assert all(np.array_equal(model.q_table[state], values) for state, values in original_table.items())
    assert updated is not model
