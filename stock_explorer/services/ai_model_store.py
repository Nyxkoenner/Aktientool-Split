from __future__ import annotations

import gzip
import hashlib
import json
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from stock_explorer.domain.rl_qlearning import (
    QLearningConfig,
    QLearningEvaluation,
    QLearningModel,
    StateDiscretizer,
    continue_q_learning,
    evaluate_q_learning,
    train_q_learning,
)

MODEL_SCHEMA_VERSION = 1
FEATURE_SCHEMA_VERSION = "price_state_v1"


@dataclass(frozen=True)
class ModelMetadata:
    schema_version: int
    feature_schema: str
    model_id: str
    ticker: str
    created_at_utc: str
    updated_at_utc: str
    parent_model_id: str | None
    data_start: str
    data_end: str
    observations: int
    data_fingerprint: str
    training_runs: int
    total_episodes: int
    last_training_mode: str
    new_observations: int
    q_states: int
    config: Mapping[str, float | int]

    @property
    def data_end_timestamp(self) -> pd.Timestamp:
        return pd.Timestamp(self.data_end)


@dataclass(frozen=True)
class StoredModel:
    metadata: ModelMetadata
    model: QLearningModel
    path: Path


@dataclass(frozen=True)
class ModelCompatibility:
    compatible: bool
    can_continue: bool
    can_evaluate: bool
    new_observations: int
    latest_data_end: pd.Timestamp
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ModelEvaluation:
    evaluation: QLearningEvaluation
    start: pd.Timestamp
    end: pd.Timestamp
    observations: int
    out_of_sample: bool


@dataclass(frozen=True)
class PolicyComparison:
    observations: int
    agreement_pct: float
    first_buy_pct: float
    second_buy_pct: float


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_ticker(ticker: str) -> str:
    cleaned = "".join(character if character.isalnum() else "_" for character in ticker.upper())
    return cleaned.strip("_") or "UNKNOWN"


def _normalise_frame(features: pd.DataFrame) -> pd.DataFrame:
    if features.empty:
        raise ValueError("Leere Feature-Daten.")
    frame = features.copy()
    frame.index = pd.to_datetime(frame.index, errors="coerce")
    frame = frame.loc[~frame.index.isna()].sort_index()
    frame = frame.loc[~frame.index.duplicated(keep="last")]
    if frame.empty:
        raise ValueError("Keine gültigen Feature-Zeitpunkte.")
    return frame


def data_fingerprint(features: pd.DataFrame) -> str:
    frame = _normalise_frame(features)
    close = pd.to_numeric(frame.get("close"), errors="coerce").fillna(0.0)
    digest = hashlib.sha256()
    for timestamp, value in close.items():
        digest.update(pd.Timestamp(timestamp).isoformat().encode("utf-8"))
        digest.update(f"|{float(value):.10f}\n".encode("utf-8"))
    return digest.hexdigest()


def _config_payload(config: QLearningConfig) -> dict[str, float | int]:
    return {key: value for key, value in asdict(config).items()}


def _compatibility_signature(config: QLearningConfig | Mapping[str, Any]) -> dict[str, float]:
    payload = asdict(config) if isinstance(config, QLearningConfig) else dict(config)
    keys = (
        "learning_rate",
        "discount_factor",
        "epsilon_start",
        "epsilon_end",
        "transaction_cost_bps",
        "downside_penalty",
    )
    return {key: float(payload[key]) for key in keys}


def _metadata_from_payload(payload: Mapping[str, Any]) -> ModelMetadata:
    return ModelMetadata(
        schema_version=int(payload["schema_version"]),
        feature_schema=str(payload["feature_schema"]),
        model_id=str(payload["model_id"]),
        ticker=str(payload["ticker"]),
        created_at_utc=str(payload["created_at_utc"]),
        updated_at_utc=str(payload["updated_at_utc"]),
        parent_model_id=str(payload["parent_model_id"]) if payload.get("parent_model_id") else None,
        data_start=str(payload["data_start"]),
        data_end=str(payload["data_end"]),
        observations=int(payload["observations"]),
        data_fingerprint=str(payload["data_fingerprint"]),
        training_runs=int(payload["training_runs"]),
        total_episodes=int(payload["total_episodes"]),
        last_training_mode=str(payload["last_training_mode"]),
        new_observations=int(payload.get("new_observations", 0)),
        q_states=int(payload["q_states"]),
        config={key: value for key, value in dict(payload["config"]).items()},
    )


def _model_payload(model: QLearningModel) -> dict[str, Any]:
    rows = [
        {
            "state": list(state),
            "values": [float(value) for value in values.tolist()],
        }
        for state, values in sorted(model.q_table.items())
    ]
    return {
        "discretizer": asdict(model.discretizer),
        "config": _config_payload(model.config),
        "q_table": rows,
    }


def _model_from_payload(payload: Mapping[str, Any]) -> QLearningModel:
    config = QLearningConfig(**dict(payload["config"]))
    discretizer = StateDiscretizer(**dict(payload["discretizer"]))
    q_table: dict[tuple[int, int, int, int, int], np.ndarray] = {}
    for row in payload["q_table"]:
        state_values = tuple(int(value) for value in row["state"])
        if len(state_values) != 5:
            raise ValueError("Ungültiger Modellzustand.")
        state = (
            state_values[0],
            state_values[1],
            state_values[2],
            state_values[3],
            state_values[4],
        )
        q_table[state] = np.asarray(row["values"], dtype=float)
    return QLearningModel(q_table=q_table, discretizer=discretizer, config=config)


def _artifact_path(directory: Path, ticker: str, model_id: str, updated_at: str) -> Path:
    timestamp = updated_at.replace("-", "").replace(":", "").replace("+00:00", "Z")
    return directory / _safe_ticker(ticker) / f"{timestamp}_{model_id}.json.gz"


def save_model_artifact(directory: Path, metadata: ModelMetadata, model: QLearningModel) -> Path:
    path = _artifact_path(directory, metadata.ticker, metadata.model_id, metadata.updated_at_utc)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"metadata": asdict(metadata), "model": _model_payload(model)}
    temporary = path.with_suffix(path.suffix + ".tmp")
    with gzip.open(temporary, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))
    os.replace(temporary, path)
    return path


def load_model_artifact(path: Path) -> StoredModel:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    metadata = _metadata_from_payload(payload["metadata"])
    if metadata.schema_version != MODEL_SCHEMA_VERSION:
        raise ValueError(f"Nicht unterstützte Modellschema-Version: {metadata.schema_version}")
    model = _model_from_payload(payload["model"])
    return StoredModel(metadata=metadata, model=model, path=path)


def list_model_artifacts(directory: Path, *, ticker: str | None = None) -> list[StoredModel]:
    candidates = (
        (directory / _safe_ticker(ticker)).glob("*.json.gz") if ticker else directory.glob("*/*.json.gz")
    )
    models: list[StoredModel] = []
    for path in candidates:
        try:
            models.append(load_model_artifact(path))
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            continue
    return sorted(models, key=lambda item: item.metadata.updated_at_utc, reverse=True)


def delete_model_artifact(stored: StoredModel) -> None:
    stored.path.unlink(missing_ok=True)
    try:
        stored.path.parent.rmdir()
    except OSError:
        pass


def train_new_model_artifact(
    features: pd.DataFrame,
    *,
    ticker: str,
    config: QLearningConfig,
    directory: Path,
    progress_callback: Any | None = None,
) -> StoredModel:
    frame = _normalise_frame(features)
    model = train_q_learning(frame, config, progress_callback=progress_callback)
    now = _utc_now()
    model_id = uuid.uuid4().hex[:12]
    metadata = ModelMetadata(
        schema_version=MODEL_SCHEMA_VERSION,
        feature_schema=FEATURE_SCHEMA_VERSION,
        model_id=model_id,
        ticker=ticker,
        created_at_utc=now,
        updated_at_utc=now,
        parent_model_id=None,
        data_start=pd.Timestamp(frame.index.min()).isoformat(),
        data_end=pd.Timestamp(frame.index.max()).isoformat(),
        observations=len(frame),
        data_fingerprint=data_fingerprint(frame),
        training_runs=1,
        total_episodes=max(int(config.episodes), 1),
        last_training_mode="full",
        new_observations=len(frame),
        q_states=len(model.q_table),
        config=_config_payload(config),
    )
    path = save_model_artifact(directory, metadata, model)
    return StoredModel(metadata=metadata, model=model, path=path)


def assess_model_compatibility(
    stored: StoredModel,
    features: pd.DataFrame,
    *,
    ticker: str,
    config: QLearningConfig,
) -> ModelCompatibility:
    frame = _normalise_frame(features)
    reasons: list[str] = []
    if stored.metadata.ticker.upper() != ticker.upper():
        reasons.append("ticker_mismatch")
    if stored.metadata.schema_version != MODEL_SCHEMA_VERSION:
        reasons.append("schema_mismatch")
    if stored.metadata.feature_schema != FEATURE_SCHEMA_VERSION:
        reasons.append("feature_schema_mismatch")
    if _compatibility_signature(stored.metadata.config) != _compatibility_signature(config):
        reasons.append("config_mismatch")

    previous_end = stored.metadata.data_end_timestamp
    overlap = bool((frame.index <= previous_end).any())
    if not overlap:
        reasons.append("no_overlap")
    new_observations = int((frame.index > previous_end).sum())
    if new_observations == 0:
        reasons.append("no_new_data")

    blocking = {
        "ticker_mismatch",
        "schema_mismatch",
        "feature_schema_mismatch",
        "config_mismatch",
        "no_overlap",
    }
    compatible = not any(reason in blocking for reason in reasons)
    return ModelCompatibility(
        compatible=compatible,
        can_continue=compatible and new_observations > 0,
        can_evaluate=compatible and new_observations > 0,
        new_observations=new_observations,
        latest_data_end=pd.Timestamp(frame.index.max()),
        reasons=tuple(reasons),
    )


def _incremental_frame(stored: StoredModel, features: pd.DataFrame) -> pd.DataFrame:
    frame = _normalise_frame(features)
    previous_end = stored.metadata.data_end_timestamp
    known = frame.loc[frame.index <= previous_end].tail(1)
    unseen = frame.loc[frame.index > previous_end]
    if known.empty or unseen.empty:
        raise ValueError("Für das Nachtraining fehlen neue Daten oder ein überlappender Ausgangspunkt.")
    return pd.concat([known, unseen]).loc[lambda item: ~item.index.duplicated(keep="last")]


def continue_model_artifact(
    stored: StoredModel,
    features: pd.DataFrame,
    *,
    ticker: str,
    config: QLearningConfig,
    directory: Path,
    episodes: int,
    seed: int,
    progress_callback: Any | None = None,
) -> StoredModel:
    compatibility = assess_model_compatibility(stored, features, ticker=ticker, config=config)
    if not compatibility.can_continue:
        raise ValueError("Das gespeicherte Modell ist nicht kompatibel oder es gibt keine neuen Daten.")
    frame = _normalise_frame(features)
    incremental = _incremental_frame(stored, frame)
    model = continue_q_learning(
        stored.model,
        incremental,
        episodes=episodes,
        seed=seed,
        progress_callback=progress_callback,
    )
    now = _utc_now()
    model_id = uuid.uuid4().hex[:12]
    metadata = ModelMetadata(
        schema_version=MODEL_SCHEMA_VERSION,
        feature_schema=FEATURE_SCHEMA_VERSION,
        model_id=model_id,
        ticker=ticker,
        created_at_utc=now,
        updated_at_utc=now,
        parent_model_id=stored.metadata.model_id,
        data_start=stored.metadata.data_start,
        data_end=pd.Timestamp(frame.index.max()).isoformat(),
        observations=stored.metadata.observations + compatibility.new_observations,
        data_fingerprint=hashlib.sha256(
            (stored.metadata.data_fingerprint + data_fingerprint(incremental.iloc[1:])).encode("utf-8")
        ).hexdigest(),
        training_runs=stored.metadata.training_runs + 1,
        total_episodes=stored.metadata.total_episodes + max(int(episodes), 1),
        last_training_mode="incremental",
        new_observations=compatibility.new_observations,
        q_states=len(model.q_table),
        config=_config_payload(model.config),
    )
    path = save_model_artifact(directory, metadata, model)
    return StoredModel(metadata=metadata, model=model, path=path)


def evaluate_model_on_new_data(stored: StoredModel, features: pd.DataFrame) -> ModelEvaluation:
    incremental = _incremental_frame(stored, features)
    unseen = incremental.iloc[1:]
    result = evaluate_q_learning(stored.model, unseen, name="stored_q_learning_unseen")
    return ModelEvaluation(
        evaluation=result,
        start=pd.Timestamp(unseen.index.min()),
        end=pd.Timestamp(unseen.index.max()),
        observations=len(unseen),
        out_of_sample=True,
    )


def compare_model_policies(
    first: StoredModel,
    second: StoredModel,
    features: pd.DataFrame,
) -> PolicyComparison:
    frame = _normalise_frame(features)
    if frame.empty:
        raise ValueError("Keine Daten für den Modellvergleich.")

    def actions(model: QLearningModel) -> list[int]:
        position = 0
        result: list[int] = []
        for _, row in frame.iterrows():
            action = model.greedy_action(model.discretizer.encode(row, position))
            result.append(action)
            if action == 0:
                position = 0
            elif action == 2:
                position = 1
        return result

    first_actions = np.asarray(actions(first.model), dtype=int)
    second_actions = np.asarray(actions(second.model), dtype=int)
    return PolicyComparison(
        observations=len(frame),
        agreement_pct=float((first_actions == second_actions).mean() * 100.0),
        first_buy_pct=float((first_actions == 2).mean() * 100.0),
        second_buy_pct=float((second_actions == 2).mean() * 100.0),
    )


__all__ = [
    "FEATURE_SCHEMA_VERSION",
    "MODEL_SCHEMA_VERSION",
    "ModelCompatibility",
    "ModelEvaluation",
    "ModelMetadata",
    "PolicyComparison",
    "StoredModel",
    "assess_model_compatibility",
    "compare_model_policies",
    "continue_model_artifact",
    "data_fingerprint",
    "delete_model_artifact",
    "evaluate_model_on_new_data",
    "list_model_artifacts",
    "load_model_artifact",
    "save_model_artifact",
    "train_new_model_artifact",
]
