from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .strategy_backtest import StrategyResult, simulate_positions

ACTION_SELL = 0
ACTION_HOLD = 1
ACTION_BUY = 2
ACTION_NAMES = {ACTION_SELL: "sell", ACTION_HOLD: "hold", ACTION_BUY: "buy"}


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

    def encode(self, row: pd.Series, position: int) -> tuple[int, int, int, int, int]:
        trend = int(np.digitize(float(row.get("sma50_to_sma200", 0.0)), [-0.02, 0.02]))
        momentum = int(np.digitize(float(row.get("return_20d", 0.0)), [-0.05, 0.0, 0.05]))
        volatility = int(
            np.digitize(float(row.get("volatility_20d", 0.0)), [self.volatility_low, self.volatility_high])
        )
        drawdown = int(np.digitize(float(row.get("drawdown", 0.0)), [-0.30, -0.10]))
        return trend, momentum, volatility, drawdown, int(position)


@dataclass
class QLearningModel:
    q_table: dict[tuple[int, int, int, int, int], np.ndarray]
    discretizer: StateDiscretizer
    config: QLearningConfig

    def q_values(self, state: tuple[int, int, int, int, int]) -> np.ndarray:
        if state not in self.q_table:
            self.q_table[state] = np.zeros(3, dtype=float)
        return self.q_table[state]

    def greedy_action(self, state: tuple[int, int, int, int, int]) -> int:
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


def train_q_learning(features: pd.DataFrame, config: QLearningConfig) -> QLearningModel:
    if len(features) < 120:
        raise ValueError("Für das Q-Learning werden mindestens 120 Feature-Zeilen benötigt.")
    discretizer = StateDiscretizer.fit(features)
    model = QLearningModel({}, discretizer, config)
    rng = np.random.default_rng(config.seed)
    episodes = max(int(config.episodes), 1)

    for episode in range(episodes):
        position = 0
        fraction = episode / max(episodes - 1, 1)
        epsilon = config.epsilon_start + fraction * (config.epsilon_end - config.epsilon_start)
        for index in range(len(features) - 1):
            row = features.iloc[index]
            state = discretizer.encode(row, position)
            if rng.random() < epsilon:
                action = int(rng.integers(0, 3))
            else:
                action = model.greedy_action(state)
            next_position = _target_position(action, position)
            next_return = float(features["asset_return"].iloc[index + 1])
            turnover = abs(next_position - position)
            transaction_cost = turnover * max(config.transaction_cost_bps, 0.0) / 10_000.0
            downside = max(-(next_position * next_return), 0.0)
            reward = next_position * next_return - transaction_cost - config.downside_penalty * downside**2
            next_state = discretizer.encode(features.iloc[index + 1], next_position)
            current_values = model.q_values(state)
            future = float(model.q_values(next_state).max())
            current_values[action] += config.learning_rate * (
                reward + config.discount_factor * future - current_values[action]
            )
            position = next_position
    return model


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
