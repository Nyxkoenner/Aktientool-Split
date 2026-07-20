from __future__ import annotations

import numpy as np
import pandas as pd

try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError:  # optional dependency
    gym = None
    spaces = None


if gym is not None:

    class TradingEnvironment(gym.Env):
        """Research-only environment: 0=hold, 1=buy/all-in, 2=sell/all-out."""

        metadata: dict[str, list[str]] = {"render_modes": []}

        def __init__(self, prices: pd.Series, initial_cash: float = 10_000.0):
            super().__init__()
            clean = pd.to_numeric(prices, errors="coerce").dropna()
            if len(clean) < 3:
                raise ValueError("Mindestens drei Kurspunkte erforderlich.")
            self.prices = clean.to_numpy(dtype=np.float32)
            self.initial_cash = float(initial_cash)
            self.action_space = spaces.Discrete(3)
            self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(4,), dtype=np.float32)
            self.reset()

        def _observation(self):
            price = self.prices[self.step_index]
            previous = self.prices[max(0, self.step_index - 1)]
            ret = price / previous - 1.0 if previous else 0.0
            equity = self.cash + self.shares * price
            return np.array(
                [price, ret, self.cash / self.initial_cash, equity / self.initial_cash], dtype=np.float32
            )

        def reset(self, seed=None, options=None):
            super().reset(seed=seed)
            self.step_index = 1
            self.cash = self.initial_cash
            self.shares = 0.0
            return self._observation(), {}

        def step(self, action):
            price = float(self.prices[self.step_index])
            before = self.cash + self.shares * price
            if action == 1 and self.cash > 0:
                self.shares += self.cash / price
                self.cash = 0.0
            elif action == 2 and self.shares > 0:
                self.cash += self.shares * price
                self.shares = 0.0
            self.step_index += 1
            terminated = self.step_index >= len(self.prices) - 1
            next_price = float(self.prices[self.step_index])
            after = self.cash + self.shares * next_price
            reward = np.log(max(after, 1e-9) / max(before, 1e-9))
            return self._observation(), float(reward), terminated, False, {"equity": after}
else:

    class TradingEnvironment:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Für das KI-Labor bitte 'pip install gymnasium stable-baselines3' ausführen.")
