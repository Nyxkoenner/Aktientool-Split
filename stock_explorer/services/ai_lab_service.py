from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

import pandas as pd

from stock_explorer.domain.ai_features import FeatureSet, build_feature_frame
from stock_explorer.domain.rl_qlearning import (
    QLearningConfig,
    QLearningEvaluation,
    evaluate_q_learning,
    train_q_learning,
)
from stock_explorer.domain.strategy_backtest import (
    StrategyResult,
    baseline_positions,
    simulate_positions,
)


@dataclass(frozen=True)
class WalkForwardConfig:
    training_years: int = 3
    test_months: int = 6
    step_months: int = 6
    min_training_days: int = 500


@dataclass(frozen=True)
class FoldSummary:
    fold: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    train_rows: int
    test_rows: int
    q_learning_return_pct: float
    buy_hold_return_pct: float
    momentum_return_pct: float


@dataclass(frozen=True)
class AILabResult:
    features: FeatureSet
    strategies: Mapping[str, StrategyResult]
    folds: tuple[FoldSummary, ...]
    q_action_counts: Mapping[str, int]
    q_states: int
    out_of_sample_start: pd.Timestamp
    out_of_sample_end: pd.Timestamp


def walk_forward_windows(
    index: pd.DatetimeIndex, config: WalkForwardConfig
) -> list[tuple[pd.Timestamp, ...]]:
    if config.step_months < config.test_months:
        raise ValueError(
            "step_months must be at least as large as test_months to avoid overlapping test windows"
        )
    clean = pd.DatetimeIndex(index).sort_values().unique()
    if len(clean) < config.min_training_days + 40:
        return []
    first = pd.Timestamp(clean.min())
    last = pd.Timestamp(clean.max())
    test_start = first + pd.DateOffset(years=max(config.training_years, 1))
    windows: list[tuple[pd.Timestamp, ...]] = []
    while test_start < last:
        train_end = test_start - pd.Timedelta(days=1)
        test_end = min(
            test_start + pd.DateOffset(months=max(config.test_months, 1)) - pd.Timedelta(days=1), last
        )
        train_mask = (clean >= first) & (clean <= train_end)
        test_mask = (clean >= test_start) & (clean <= test_end)
        if int(train_mask.sum()) >= config.min_training_days and int(test_mask.sum()) >= 20:
            windows.append((first, train_end, test_start, test_end))
        test_start = test_start + pd.DateOffset(months=max(config.step_months, 1))
    return windows


def run_ai_lab(
    history: pd.DataFrame | pd.Series,
    *,
    walk_forward: WalkForwardConfig,
    q_learning: QLearningConfig,
    current_scores: Mapping[str, float | int | None] | None = None,
) -> AILabResult:
    features = build_feature_frame(history, current_scores=current_scores)
    windows = walk_forward_windows(pd.DatetimeIndex(features.frame.index), walk_forward)
    if not windows:
        raise ValueError(
            "Für die gewählte Trainings-/Testkonfiguration gibt es keine gültigen Walk-forward-Fenster."
        )

    position_parts: dict[str, list[pd.Series]] = {
        "buy_hold": [],
        "momentum": [],
        "recovery": [],
        "combined": [],
        "q_learning": [],
    }
    folds: list[FoldSummary] = []
    aggregate_actions = {"sell": 0, "hold": 0, "buy": 0}
    total_q_states = 0

    for fold_number, (train_start, train_end, test_start, test_end) in enumerate(windows, start=1):
        train = features.frame.loc[train_start:train_end]
        test = features.frame.loc[test_start:test_end]
        model = train_q_learning(train, q_learning)
        q_evaluation: QLearningEvaluation = evaluate_q_learning(model, test)
        baseline = baseline_positions(test)
        fold_results = {
            key: simulate_positions(
                test,
                positions,
                name=key,
                transaction_cost_bps=q_learning.transaction_cost_bps,
            )
            for key, positions in baseline.items()
        }
        for key, positions in baseline.items():
            position_parts[key].append(positions)
        position_parts["q_learning"].append(q_evaluation.result.positions)
        for key, count in q_evaluation.action_counts.items():
            aggregate_actions[key] += count
        total_q_states += q_evaluation.q_states
        folds.append(
            FoldSummary(
                fold=fold_number,
                train_start=train.index.min(),
                train_end=train.index.max(),
                test_start=test.index.min(),
                test_end=test.index.max(),
                train_rows=len(train),
                test_rows=len(test),
                q_learning_return_pct=q_evaluation.result.metrics.total_return_pct,
                buy_hold_return_pct=fold_results["buy_hold"].metrics.total_return_pct,
                momentum_return_pct=fold_results["momentum"].metrics.total_return_pct,
            )
        )

    stitched_positions = {
        name: pd.concat(parts).sort_index().loc[lambda series: ~series.index.duplicated(keep="last")]
        for name, parts in position_parts.items()
    }
    out_of_sample_index = stitched_positions["q_learning"].index
    out_of_sample = features.frame.loc[out_of_sample_index]
    strategies = {
        name: simulate_positions(
            out_of_sample,
            positions,
            name=name,
            transaction_cost_bps=q_learning.transaction_cost_bps,
        )
        for name, positions in stitched_positions.items()
    }
    return AILabResult(
        features=features,
        strategies=strategies,
        folds=tuple(folds),
        q_action_counts=aggregate_actions,
        q_states=total_q_states,
        out_of_sample_start=pd.Timestamp(out_of_sample_index.min()),
        out_of_sample_end=pd.Timestamp(out_of_sample_index.max()),
    )


def save_ai_lab_run(
    result: AILabResult,
    *,
    ticker: str,
    directory: Path,
    parameters: Mapping[str, object],
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_ticker = "".join(character if character.isalnum() else "_" for character in ticker.upper())
    path = directory / f"{safe_ticker}_{timestamp}.json"
    payload = {
        "ticker": ticker,
        "created_at_utc": timestamp,
        "out_of_sample_start": result.out_of_sample_start.isoformat(),
        "out_of_sample_end": result.out_of_sample_end.isoformat(),
        "parameters": dict(parameters),
        "q_action_counts": dict(result.q_action_counts),
        "q_states": result.q_states,
        "folds": [
            {
                **asdict(fold),
                "train_start": fold.train_start.isoformat(),
                "train_end": fold.train_end.isoformat(),
                "test_start": fold.test_start.isoformat(),
                "test_end": fold.test_end.isoformat(),
            }
            for fold in result.folds
        ],
        "strategies": {name: asdict(strategy.metrics) for name, strategy in result.strategies.items()},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
