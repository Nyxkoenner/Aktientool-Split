import numpy as np
import pandas as pd

from stock_explorer.domain.ai_features import build_feature_frame
from stock_explorer.domain.rl_qlearning import QLearningConfig, evaluate_q_learning, train_q_learning


def _features() -> pd.DataFrame:
    index = pd.bdate_range("2017-01-01", periods=1400)
    regime = np.where(np.arange(len(index)) < 700, 0.0004, -0.00005)
    prices = 100 * np.exp(np.cumsum(regime + 0.008 * np.sin(np.arange(len(index)) / 17)))
    return build_feature_frame(pd.DataFrame({"Close": prices}, index=index)).frame


def test_q_learning_is_reproducible_and_generates_valid_positions() -> None:
    features = _features()
    train = features.iloc[:800]
    test = features.iloc[800:]
    config = QLearningConfig(episodes=40, seed=7, transaction_cost_bps=5)
    model_a = train_q_learning(train, config)
    model_b = train_q_learning(train, config)
    evaluation_a = evaluate_q_learning(model_a, test)
    evaluation_b = evaluate_q_learning(model_b, test)
    pd.testing.assert_series_equal(evaluation_a.result.positions, evaluation_b.result.positions)
    assert set(evaluation_a.result.positions.unique()).issubset({0.0, 1.0})
    assert sum(evaluation_a.action_counts.values()) == len(test)
    assert evaluation_a.q_states > 0
