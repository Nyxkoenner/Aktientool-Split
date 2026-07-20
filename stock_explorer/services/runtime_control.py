from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Sequence

import pandas as pd

WalkForwardWindow = tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]


@dataclass(frozen=True)
class RuntimeProfile:
    profile_id: str
    history_years: int
    training_years: int
    test_months: int
    step_months: int
    episodes: int
    max_folds: int
    max_minutes: int


@dataclass(frozen=True)
class RunLimits:
    max_seconds: float | None = None
    max_folds: int | None = None


@dataclass(frozen=True)
class ProgressUpdate:
    completed_folds: int
    total_folds: int
    stage: str
    elapsed_seconds: float
    fold: int | None = None

    @property
    def fraction(self) -> float:
        if self.total_folds <= 0:
            return 0.0
        return min(max(self.completed_folds / self.total_folds, 0.0), 1.0)


@dataclass(frozen=True)
class WorkloadEstimate:
    observations: int
    folds: int
    episodes: int
    training_steps: int
    estimated_seconds_low: float
    estimated_seconds_high: float
    risk_level: str


RUNTIME_PROFILES: Final[dict[str, RuntimeProfile]] = {
    "quick": RuntimeProfile(
        profile_id="quick",
        history_years=10,
        training_years=3,
        test_months=12,
        step_months=12,
        episodes=50,
        max_folds=8,
        max_minutes=2,
    ),
    "standard": RuntimeProfile(
        profile_id="standard",
        history_years=20,
        training_years=3,
        test_months=6,
        step_months=6,
        episodes=150,
        max_folds=24,
        max_minutes=10,
    ),
    "intensive": RuntimeProfile(
        profile_id="intensive",
        history_years=0,
        training_years=4,
        test_months=6,
        step_months=6,
        episodes=300,
        max_folds=60,
        max_minutes=30,
    ),
}


def runtime_profile(profile_id: str) -> RuntimeProfile:
    try:
        return RUNTIME_PROFILES[profile_id]
    except KeyError as error:
        raise ValueError(f"Unknown runtime profile: {profile_id}") from error


def estimate_walk_forward_workload(
    index: pd.DatetimeIndex,
    windows: Sequence[WalkForwardWindow],
    *,
    episodes: int,
    steps_per_second_low: float = 9_000.0,
    steps_per_second_high: float = 18_000.0,
) -> WorkloadEstimate:
    clean_index = pd.DatetimeIndex(index)
    episode_count = max(int(episodes), 1)
    training_steps = 0
    for train_start, train_end, _, _ in windows:
        rows = int(((clean_index >= train_start) & (clean_index <= train_end)).sum())
        training_steps += max(rows - 1, 0) * episode_count

    low_speed = max(float(steps_per_second_low), 1.0)
    high_speed = max(float(steps_per_second_high), low_speed)
    estimated_low = training_steps / high_speed
    estimated_high = training_steps / low_speed
    if estimated_high < 60:
        risk_level = "low"
    elif estimated_high < 600:
        risk_level = "medium"
    else:
        risk_level = "high"
    return WorkloadEstimate(
        observations=len(clean_index),
        folds=len(windows),
        episodes=episode_count,
        training_steps=training_steps,
        estimated_seconds_low=estimated_low,
        estimated_seconds_high=estimated_high,
        risk_level=risk_level,
    )


__all__ = [
    "ProgressUpdate",
    "RUNTIME_PROFILES",
    "RunLimits",
    "RuntimeProfile",
    "WalkForwardWindow",
    "WorkloadEstimate",
    "estimate_walk_forward_workload",
    "runtime_profile",
]
