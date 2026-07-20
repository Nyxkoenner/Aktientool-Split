from stock_explorer.domain.scenario_models import (
    CompanyScenarioSnapshot,
    ScenarioShock,
    classify_sector,
    run_sector_scenario,
    sector_adjusted_preset,
)


def _snapshot(sector: str = "Industrials") -> CompanyScenarioSnapshot:
    return CompanyScenarioSnapshot(
        current_price=100.0,
        current_eps=5.0,
        current_pe=20.0,
        dividend_yield_pct=3.0,
        revenue_growth_pct=4.0,
        operating_margin_pct=12.0,
        net_debt_ebitda=2.0,
        beta=1.0,
        sector=sector,
        currency="EUR",
    )


def test_sector_classification() -> None:
    assert classify_sector("Software") == "technology"
    assert classify_sector("Real Estate") == "real_estate"
    assert classify_sector("Insurance") == "insurance"
    assert classify_sector("Unknown") == "generic"


def test_rate_hike_differs_for_banks_and_real_estate() -> None:
    bank = sector_adjusted_preset("rate_hike", "Banking")
    real_estate = sector_adjusted_preset("rate_hike", "Real Estate")
    assert bank.shock.financing_earnings_impact_pct > 0
    assert real_estate.shock.financing_earnings_impact_pct < 0
    assert real_estate.shock.valuation_change_pct < bank.shock.valuation_change_pct


def test_sector_scenario_combines_price_and_dividend_return() -> None:
    result = run_sector_scenario(
        _snapshot(),
        ScenarioShock(annual_growth_delta_pct=1.0, valuation_change_pct=-10.0),
        years=2,
    )
    assert result.estimated_eps is not None
    assert result.estimated_price is not None
    assert result.estimated_dividends == 6.0
    expected_return = ((result.estimated_price + 6.0) / 100.0 - 1.0) * 100.0
    assert result.estimated_total_return_pct == expected_return


def test_invalid_horizon_is_rejected() -> None:
    try:
        run_sector_scenario(_snapshot(), ScenarioShock(), years=0)
    except ValueError as error:
        assert "years" in str(error)
    else:
        raise AssertionError("Expected ValueError")
