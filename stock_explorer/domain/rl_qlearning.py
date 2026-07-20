from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from .strategy_backtest import StrategyResult, simulate_positions

ACTION_SELL = 0
ACTION_HOLD = 1
ACTION_BUY = 2
ACTION_NAMES = {ACTION_SELL: "sell", ACTION_HOLD: "hold", ACTION_BUY: "buy"}
State = tuple[int, int, int, int, int]
TrainingProgress = Callable[[int, int], None]


@dataclass(frozen=True)
class QLearningConfig:
    episodes: int = 300
    learning_rate: float = 0.12
    discount_factor: float = 0.95
    epsilon_start: float = 0.35
    epsilon_end: float = 0.03
    transaction_cost_bps: float = 10.0
    downside_penalty: float = 0.25
    seed: int = 42


@dataclass(frozen=True)
class StateDiscretizer:
    volatility_low: float
    volatility_high: float

    @classmethod
    def fit(cls, features: pd.DataFrame) -> StateDiscretizer:
        volatility = pd.to_numeric(features["volatility_20d"], errors="coerce").dropna()
        if volatility.empty:
            return cls(0.20, 0.40)
        low = float(volatility.quantile(0.33))
        high = float(volatility.quantile(0.67))
        if high <= low:
            high = low + 1e-6
        return cls(low, high)

    def encode(self, row: pd.Series, position: int) -> State:
        trend = int(np.digitize(float(row.get("sma50_to_sma200", 0.0)), [-0.02, 0.02]))
        momentum = int(np.digitize(float(row.get("return_20d", 0.0)), [-0.05, 0.0, 0.05]))
        volatility = int(
            np.digitize(
                float(row.get("volatility_20d", 0.0)),
                [self.volatility_low, self.volatility_high],
            )
        )
        drawdown = int(np.digitize(float(row.get("drawdown", 0.0)), [-0.30, -0.10]))
        return trend, momentum, volatility, drawdown, int(position)


@dataclass
class QLearningModel:
    q_table: dict[State, np.ndarray]
    discretizer: StateDiscretizer
    config: QLearningConfig

    def q_values(self, state: State) -> np.ndarray:
        if state not in self.q_table:
            self.q_table[state] = np.zeros(3, dtype=float)
        return self.q_table[state]

    def greedy_action(self, state: State) -> int:
        values = self.q_values(state)
        best = np.flatnonzero(np.isclose(values, values.max()))
        if ACTION_HOLD in best:
            return ACTION_HOLD
        return int(best[0])


@dataclass(frozen=True)
class QLearningEvaluation:
    result: StrategyResult
    action_counts: dict[str, int]
    q_states: int


def _target_position(action: int, current_position: int) -> int:
    if action == ACTION_SELL:
        return 0
    if action == ACTION_BUY:
        return 1
    return current_position


def clone_q_learning_model(model: QLearningModel, *, config: QLearningConfig | None = None) -> QLearningModel:
    return QLearningModel(
        q_table={state: values.astype(float, copy=True) for state, values in model.q_table.items()},
        discretizer=model.discretizer,
        config=config or model.config,
    )


def _train_existing_model(
    model: QLearningModel,
    features: pd.DataFrame,
    config: QLearningConfig,
    *,
    progress_callback: TrainingProgress | None = None,
) -> QLearningModel:
    if len(features) < 2:
        raise ValueError("Für das Training werden mindestens zwei Feature-Zeilen benötigt.")
    trained = clone_q_learning_model(model, config=config)
    rng = np.random.default_rng(config.seed)
    episodes = max(int(config.episodes), 1)
    progress_step = max(episodes // 100, 1)

    for episode in range(episodes):
        position = 0
        fraction = episode / max(episodes - 1, 1)
        epsilon = config.epsilon_start + fraction * (config.epsilon_end - config.epsilon_start)
        for index in range(len(features) - 1):
            row = features.iloc[index]
            state = trained.discretizer.encode(row, position)
            if rng.random() < epsilon:
                action = int(rng.integers(0, 3))
            else:
                action = trained.greedy_action(state)
            next_position = _target_position(action, position)
            next_return = float(features["asset_return"].iloc[index + 1])
            turnover = abs(next_position - position)
            transaction_cost = turnover * max(config.transaction_cost_bps, 0.0) / 10_000.0
            downside = max(-(next_position * next_return), 0.0)
            reward = next_position * next_return - transaction_cost - config.downside_penalty * downside**2
            next_state = trained.discretizer.encode(features.iloc[index + 1], next_position)
            current_values = trained.q_values(state)
            future = float(trained.q_values(next_state).max())
            current_values[action] += config.learning_rate * (
                reward + config.discount_factor * future - current_values[action]
            )
            position = next_position
        completed = episode + 1
        if progress_callback is not None and (completed == episodes or completed % progress_step == 0):
            progress_callback(completed, episodes)
    return trained


def train_q_learning(
    features: pd.DataFrame,
    config: QLearningConfig,
    *,
    progress_callback: TrainingProgress | None = None,
) -> QLearningModel:
    if len(features) < 120:
        raise ValueError("Für das Q-Learning werden mindestens 120 Feature-Zeilen benötigt.")
    model = QLearningModel({}, StateDiscretizer.fit(features), config)
    return _train_existing_model(model, features, config, progress_callback=progress_callback)


def continue_q_learning(
    model: QLearningModel,
    features: pd.DataFrame,
    *,
    episodes: int | None = None,
    seed: int | None = None,
    progress_callback: TrainingProgress | None = None,
) -> QLearningModel:
    """Continue a stored model without refitting its state discretizer.

    The caller should pass the last already-known observation followed by genuinely
    new observations. Keeping the original discretizer makes model versions
    comparable and prevents state definitions from silently changing.
    """
    config = replace(
        model.config,
        episodes=max(int(episodes if episodes is not None else model.config.episodes), 1),
        seed=int(seed if seed is not None else model.config.seed),
    )
    return _train_existing_model(
        model,
        features,
        config,
        progress_callback=progress_callback,
    )


def evaluate_q_learning(
    model: QLearningModel,
    features: pd.DataFrame,
    *,
    name: str = "q_learning",
) -> QLearningEvaluation:
    if features.empty:
        raise ValueError("Leere Testdaten.")
    position = 0
    positions = pd.Series(0.0, index=features.index, name="position")
    action_counts = {label: 0 for label in ACTION_NAMES.values()}
    for timestamp, row in features.iterrows():
        state = model.discretizer.encode(row, position)
        action = model.greedy_action(state)
        action_counts[ACTION_NAMES[action]] += 1
        position = _target_position(action, position)
        positions.loc[timestamp] = float(position)
    result = simulate_positions(
        features,
        positions,
        name=name,
        transaction_cost_bps=model.config.transaction_cost_bps,
    )
    return QLearningEvaluation(result=result, action_counts=action_counts, q_states=len(model.q_table))


__all__ = [
    "ACTION_BUY",
    "ACTION_HOLD",
    "ACTION_NAMES",
    "ACTION_SELL",
    "QLearningConfig",
    "QLearningEvaluation",
    "QLearningModel",
    "State",
    "StateDiscretizer",
    "clone_q_learning_model",
    "continue_q_learning",
    "evaluate_q_learning",
    "train_q_learning",
]
