from __future__ import annotations

import numpy as np
import pandas as pd

from stock_explorer.domain.rl_qlearning import QLearningConfig
from stock_explorer.services.ai_lab_service import WalkForwardConfig, plan_ai_lab, run_ai_lab
from stock_explorer.services.runtime_control import ProgressUpdate, RunLimits


def _history(rows: int = 1500) -> pd.DataFrame:
    index = pd.bdate_range("2017-01-01", periods=rows)
    returns = 0.0002 + 0.005 * np.sin(np.arange(rows) / 29)
    prices = 100 * np.exp(np.cumsum(returns))
    return pd.DataFrame({"Close": prices}, index=index)


def test_ai_lab_reports_progress_and_returns_safe_partial_result() -> None:
    history = _history()
    walk_forward = WalkForwardConfig(
        training_years=2,
        test_months=6,
        step_months=6,
        min_training_days=350,
    )
    q_learning = QLearningConfig(episodes=2, seed=5)
    plan = plan_ai_lab(history, walk_forward=walk_forward, q_learning=q_learning)
    progress: list[ProgressUpdate] = []

    result = run_ai_lab(
        history,
        walk_forward=walk_forward,
        q_learning=q_learning,
        plan=plan,
        limits=RunLimits(max_folds=2),
        progress_callback=progress.append,
    )

    assert result.completed_folds == 2
    assert result.planned_folds > result.completed_folds
    assert result.completed is False
    assert result.stop_reason == "fold_limit"
    assert result.elapsed_seconds > 0
    assert progress[0].stage == "starting"
    assert progress[-1].stage == "stopped"
    assert sum(update.stage == "fold_complete" for update in progress) == 2
