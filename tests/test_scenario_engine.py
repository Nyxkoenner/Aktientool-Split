import pytest

from stock_explorer.domain.scenario_engine import ScenarioInput, run_scenario


def test_scenario_total_return():
    result = run_scenario(
        ScenarioInput(
            current_price=100,
            current_eps=5,
            revenue_growth=0.10,
            margin_change_pct=0,
            target_pe=22,
            dividend_yield_pct=2,
            years=1,
        )
    )
    assert result.estimated_price == pytest.approx(121.0)
    assert result.estimated_total_return_pct == pytest.approx(23.0)
