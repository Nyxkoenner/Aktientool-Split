from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from stock_explorer.domain.rl_qlearning import QLearningConfig
from stock_explorer.services.ai_model_store import (
    assess_model_compatibility,
    compare_model_policies,
    continue_model_artifact,
    delete_model_artifact,
    evaluate_model_on_new_data,
    list_model_artifacts,
    load_model_artifact,
    train_new_model_artifact,
)


def _features(rows: int = 180, start: str = "2024-01-01") -> pd.DataFrame:
    index = pd.bdate_range(start, periods=rows)
    returns = 0.0004 + np.sin(np.arange(rows) / 11.0) / 200.0
    close = 100.0 * np.cumprod(1.0 + returns)
    close_series = pd.Series(close, index=index)
    return pd.DataFrame(
        {
            "close": close,
            "asset_return": returns,
            "return_20d": close_series.pct_change(20).fillna(0.0),
            "volatility_20d": 0.18 + np.cos(np.arange(rows) / 17.0) / 60.0,
            "sma50_to_sma200": np.sin(np.arange(rows) / 29.0) / 18.0,
            "drawdown": close_series / close_series.cummax() - 1.0,
        },
        index=index,
    )


def _extended(base: pd.DataFrame, extra_rows: int = 8) -> pd.DataFrame:
    start = pd.Timestamp(base.index.max()) + pd.offsets.BDay(1)
    extra = _features(extra_rows, start=start.strftime("%Y-%m-%d"))
    scale = float(base["close"].iloc[-1]) / float(extra["close"].iloc[0])
    extra = extra.copy()
    extra["close"] *= scale
    return pd.concat([base, extra])


def test_model_roundtrip_and_listing(tmp_path: Path) -> None:
    config = QLearningConfig(episodes=2, seed=3)
    stored = train_new_model_artifact(_features(), ticker="TEST.DE", config=config, directory=tmp_path)

    loaded = load_model_artifact(stored.path)
    listed = list_model_artifacts(tmp_path, ticker="TEST.DE")

    assert loaded.metadata.model_id == stored.metadata.model_id
    assert loaded.metadata.ticker == "TEST.DE"
    assert loaded.metadata.q_states == len(loaded.model.q_table)
    assert [item.metadata.model_id for item in listed] == [stored.metadata.model_id]


def test_compatibility_detects_new_data_and_parameter_changes(tmp_path: Path) -> None:
    base = _features()
    config = QLearningConfig(episodes=2, seed=3)
    stored = train_new_model_artifact(base, ticker="TEST", config=config, directory=tmp_path)

    current = assess_model_compatibility(stored, base, ticker="TEST", config=config)
    update = assess_model_compatibility(
        stored, _extended(base, 6), ticker="TEST", config=replace(config, episodes=9, seed=99)
    )
    incompatible = assess_model_compatibility(
        stored,
        _extended(base, 6),
        ticker="TEST",
        config=replace(config, transaction_cost_bps=25.0),
    )

    assert current.compatible
    assert not current.can_continue
    assert "no_new_data" in current.reasons
    assert update.can_continue
    assert update.new_observations == 6
    assert not incompatible.compatible
    assert "config_mismatch" in incompatible.reasons


def test_incremental_version_has_parent_and_can_be_evaluated(tmp_path: Path) -> None:
    base = _features()
    extended = _extended(base, 7)
    config = QLearningConfig(episodes=2, seed=3)
    original = train_new_model_artifact(base, ticker="TEST", config=config, directory=tmp_path)

    evaluation = evaluate_model_on_new_data(original, extended)
    updated = continue_model_artifact(
        original,
        extended,
        ticker="TEST",
        config=config,
        directory=tmp_path,
        episodes=3,
        seed=4,
    )

    assert evaluation.out_of_sample
    assert evaluation.observations == 7
    assert updated.metadata.parent_model_id == original.metadata.model_id
    assert updated.metadata.last_training_mode == "incremental"
    assert updated.metadata.new_observations == 7
    assert updated.metadata.training_runs == 2
    assert updated.metadata.total_episodes == 5
    assert len(list_model_artifacts(tmp_path, ticker="TEST")) == 2


def test_policy_comparison_and_delete(tmp_path: Path) -> None:
    features = _features()
    first = train_new_model_artifact(
        features,
        ticker="TEST",
        config=QLearningConfig(episodes=1, seed=1),
        directory=tmp_path,
    )
    second = train_new_model_artifact(
        features,
        ticker="TEST",
        config=QLearningConfig(episodes=1, seed=2),
        directory=tmp_path,
    )

    comparison = compare_model_policies(first, second, features.tail(30))
    delete_model_artifact(first)

    assert comparison.observations == 30
    assert 0.0 <= comparison.agreement_pct <= 100.0
    assert not first.path.exists()
    assert len(list_model_artifacts(tmp_path, ticker="TEST")) == 1
