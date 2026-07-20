from __future__ import annotations

import pandas as pd

from stock_explorer.services.runtime_control import (
    ProgressUpdate,
    estimate_walk_forward_workload,
    runtime_profile,
)


def test_runtime_profiles_are_bounded_and_increase_in_effort() -> None:
    quick = runtime_profile("quick")
    standard = runtime_profile("standard")
    intensive = runtime_profile("intensive")

    assert quick.episodes < standard.episodes < intensive.episodes
    assert quick.max_minutes < standard.max_minutes < intensive.max_minutes
    assert quick.max_folds < standard.max_folds < intensive.max_folds


def test_workload_estimate_counts_training_steps_and_risk() -> None:
    index = pd.bdate_range("2020-01-01", periods=1000)
    windows = (
        (index[0], index[499], index[500], index[599]),
        (index[0], index[699], index[700], index[799]),
    )

    estimate = estimate_walk_forward_workload(index, windows, episodes=20)

    assert estimate.folds == 2
    assert estimate.training_steps == ((500 - 1) + (700 - 1)) * 20
    assert estimate.estimated_seconds_low <= estimate.estimated_seconds_high
    assert estimate.risk_level in {"low", "medium", "high"}


def test_progress_fraction_is_safely_bounded() -> None:
    assert ProgressUpdate(2, 4, "training", 1.0).fraction == 0.5
    assert ProgressUpdate(9, 4, "training", 1.0).fraction == 1.0
    assert ProgressUpdate(0, 0, "starting", 0.0).fraction == 0.0
