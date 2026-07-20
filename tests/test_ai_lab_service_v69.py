from pathlib import Path

import numpy as np
import pandas as pd

from stock_explorer.domain.rl_qlearning import QLearningConfig
from stock_explorer.services.ai_lab_service import (
    WalkForwardConfig,
    run_ai_lab,
    save_ai_lab_run,
    walk_forward_windows,
)


def _history(rows: int = 1900) -> pd.DataFrame:
    index = pd.bdate_range("2015-01-01", periods=rows)
    returns = 0.00025 + 0.006 * np.sin(np.arange(rows) / 31)
    prices = 100 * np.exp(np.cumsum(returns))
    return pd.DataFrame({"Close": prices}, index=index)


def test_walk_forward_rejects_overlapping_test_windows() -> None:
    index = pd.bdate_range("2015-01-01", periods=1500)
    try:
        walk_forward_windows(index, WalkForwardConfig(training_years=2, test_months=12, step_months=6))
    except ValueError as error:
        assert "overlapping" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_ai_lab_runs_out_of_sample_and_saves_summary(tmp_path: Path) -> None:
    result = run_ai_lab(
        _history(),
        walk_forward=WalkForwardConfig(training_years=2, test_months=6, step_months=6, min_training_days=350),
        q_learning=QLearningConfig(episodes=20, seed=11),
        current_scores={"value": 70.0, "safety": 55.0},
    )
    assert len(result.folds) >= 2
    assert set(result.strategies) == {"buy_hold", "momentum", "recovery", "combined", "q_learning"}
    assert result.out_of_sample_start > result.features.start
    path = save_ai_lab_run(result, ticker="TEST", directory=tmp_path, parameters={"episodes": 20})
    assert path.exists()
    assert '"ticker": "TEST"' in path.read_text(encoding="utf-8")
