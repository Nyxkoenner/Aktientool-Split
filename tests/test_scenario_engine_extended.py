import pytest

from stock_explorer.domain.scenario_engine import ScenarioInput, run_scenario


def test_scenario_includes_dividends() -> None:
    result = run_scenario(ScenarioInput(100.0, 5.0, 0.05, 0.0, 20.0, 4.0, 2))
    assert result.estimated_price == pytest.approx(110.25)
    assert result.estimated_dividends == pytest.approx(8.0)
    assert result.estimated_total_return_pct == pytest.approx(18.25)


def test_scenario_rejects_invalid_horizon() -> None:
    with pytest.raises(ValueError):
        run_scenario(ScenarioInput(100.0, 5.0, years=0))
