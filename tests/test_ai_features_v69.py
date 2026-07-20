import numpy as np
import pandas as pd

from stock_explorer.domain.ai_features import build_feature_frame, extract_close_series


def _history(rows: int = 900) -> pd.DataFrame:
    index = pd.bdate_range("2020-01-01", periods=rows)
    prices = 100 * np.exp(np.linspace(0, 0.45, rows) + 0.03 * np.sin(np.arange(rows) / 15))
    return pd.DataFrame({"Close": prices}, index=index)


def test_extract_close_and_features_are_backward_looking() -> None:
    history = _history()
    close = extract_close_series(history)
    assert close.name == "close"
    features = build_feature_frame(history, current_scores={"value": 75.0})
    assert len(features.frame) > 600
    assert "sma50_to_sma200" in features.frame
    assert "context_value" in features.frame
    assert features.frame["context_value"].iloc[-1] == 75.0
    assert not any(column == "value" for column in features.frame.columns)


def test_short_history_is_rejected() -> None:
    try:
        extract_close_series(_history(100))
    except ValueError as error:
        assert "260" in str(error)
    else:
        raise AssertionError("Expected ValueError")
