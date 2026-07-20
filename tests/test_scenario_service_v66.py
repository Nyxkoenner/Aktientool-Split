import pandas as pd

from stock_explorer.domain.scenario_models import ScenarioShock
from stock_explorer.services.scenario_service import analyze_scenario, snapshot_from_row


def test_snapshot_uses_price_and_pe_as_eps_fallback() -> None:
    row = pd.Series(
        {
            "last_price": 120.0,
            "pe_ratio": 15.0,
            "revenue_growth": 5.0,
            "dividend_yield": 2.0,
            "sector": "Software",
            "currency": "EUR",
        }
    )
    snapshot = snapshot_from_row(row)
    assert snapshot.current_eps == 8.0
    assert snapshot.current_pe == 15.0


def test_analysis_builds_three_bands_and_calibration() -> None:
    row = pd.Series(
        {
            "last_price": 100.0,
            "pe_ratio": 10.0,
            "revenue_growth": 3.0,
            "operating_margin": 12.0,
            "dividend_yield": 4.0,
            "sector": "Industrials",
            "currency": "EUR",
        }
    )
    history = pd.DataFrame(
        {"Close": range(100, 1000)},
        index=pd.date_range("2020-01-01", periods=900, freq="B"),
    )
    analysis = analyze_scenario(snapshot_from_row(row), "recession", 1, history)
    assert analysis.weak.estimated_total_return_pct is not None
    assert analysis.base.estimated_total_return_pct is not None
    assert analysis.strong.estimated_total_return_pct is not None
    assert analysis.weak.estimated_total_return_pct < analysis.strong.estimated_total_return_pct
    assert analysis.calibration.sample_count > 20


def test_custom_shock_is_used() -> None:
    row = pd.Series(
        {
            "last_price": 100.0,
            "pe_ratio": 10.0,
            "revenue_growth": 0.0,
            "dividend_yield": 0.0,
            "sector": "Generic",
        }
    )
    custom = ScenarioShock(annual_growth_delta_pct=10.0, valuation_change_pct=20.0)
    analysis = analyze_scenario(snapshot_from_row(row), "custom", 1, custom_shock=custom)
    assert analysis.preset.shock == custom
    assert analysis.base.estimated_price is not None
    assert analysis.base.estimated_price > 100.0
