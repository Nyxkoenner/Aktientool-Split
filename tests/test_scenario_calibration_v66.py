import numpy as np
import pandas as pd

from stock_explorer.domain.scenario_calibration import (
    assess_growth_assumption,
    assess_projection,
    calibrate_history,
)


def _history(rows: int = 900) -> pd.DataFrame:
    index = pd.date_range("2020-01-01", periods=rows, freq="B")
    returns = np.linspace(-0.001, 0.0015, rows)
    prices = 100.0 * pd.Series(1.0 + returns, index=index).cumprod()
    return pd.DataFrame({"Close": prices}, index=index)


def test_historical_calibration_returns_quantiles() -> None:
    result = calibrate_history(_history(), years=1)
    assert result.sample_count > 20
    assert result.weak_return_pct is not None
    assert result.median_return_pct is not None
    assert result.strong_return_pct is not None
    assert result.weak_return_pct <= result.median_return_pct <= result.strong_return_pct
    assert result.annualized_volatility_pct is not None
    assert result.max_drawdown_pct is not None


def test_projection_assessment_uses_historical_range() -> None:
    result = calibrate_history(_history(), years=1)
    assert assess_projection(-100.0, result) == "below"
    assert assess_projection(500.0, result) == "above"
    assert assess_projection(result.median_return_pct, result) == "within"


def test_growth_assessment_is_sector_specific() -> None:
    assert assess_growth_assumption(20.0, "technology") == "plausible"
    assert assess_growth_assumption(20.0, "utility") == "very_strong"
    assert assess_growth_assumption(-20.0, "industrial") == "very_weak"
