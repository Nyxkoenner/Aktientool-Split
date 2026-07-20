from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from stock_explorer.domain.scenario_calibration import (
    HistoricalCalibration,
    assess_growth_assumption,
    assess_projection,
    calibrate_history,
)
from stock_explorer.domain.scenario_models import (
    CompanyScenarioSnapshot,
    ScenarioOutcome,
    ScenarioPreset,
    ScenarioShock,
    band_shock,
    classify_sector,
    run_sector_scenario,
    sector_adjusted_preset,
)


@dataclass(frozen=True)
class ScenarioAnalysis:
    snapshot: CompanyScenarioSnapshot
    sector_category: str
    preset: ScenarioPreset
    weak: ScenarioOutcome
    base: ScenarioOutcome
    strong: ScenarioOutcome
    calibration: HistoricalCalibration
    projection_assessment: str
    growth_assessment: str


def _number(value: Any, default: float | None = None) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if pd.notna(number) else default


def snapshot_from_row(row: pd.Series) -> CompanyScenarioSnapshot:
    price = _number(row.get("last_price"), 0.0) or 0.0
    pe = _number(row.get("pe_ratio"))
    eps = _number(row.get("trailing_eps"))
    if (eps is None or eps <= 0) and pe is not None and pe > 0 and price > 0:
        eps = price / pe
    revenue_growth = _number(row.get("revenue_growth"), 0.0) or 0.0
    operating_margin = _number(row.get("operating_margin"))
    net_debt_ebitda = _number(row.get("net_debt_ebitda"))
    beta = _number(row.get("beta"))
    dividend_yield = _number(row.get("dividend_yield"), 0.0) or 0.0
    return CompanyScenarioSnapshot(
        current_price=price,
        current_eps=eps,
        current_pe=pe,
        dividend_yield_pct=dividend_yield,
        revenue_growth_pct=revenue_growth,
        operating_margin_pct=operating_margin,
        net_debt_ebitda=net_debt_ebitda,
        beta=beta,
        sector=str(row.get("sector") or ""),
        currency=str(row.get("currency") or ""),
    )


def analyze_scenario(
    snapshot: CompanyScenarioSnapshot,
    preset_id: str,
    years: int,
    history: pd.DataFrame | pd.Series | None = None,
    custom_shock: ScenarioShock | None = None,
) -> ScenarioAnalysis:
    preset = sector_adjusted_preset(preset_id, snapshot.sector)
    if custom_shock is not None:
        preset = ScenarioPreset(
            preset_id="custom",
            shock=custom_shock,
            assumption_codes=preset.assumption_codes,
            risk_codes=preset.risk_codes,
        )
    base = run_sector_scenario(snapshot, preset.shock, years)
    weak = run_sector_scenario(snapshot, band_shock(preset.shock, "weak"), years)
    strong = run_sector_scenario(snapshot, band_shock(preset.shock, "strong"), years)
    calibration = calibrate_history(history, years)
    category = classify_sector(snapshot.sector)
    return ScenarioAnalysis(
        snapshot=snapshot,
        sector_category=category,
        preset=preset,
        weak=weak,
        base=base,
        strong=strong,
        calibration=calibration,
        projection_assessment=assess_projection(base.estimated_total_return_pct, calibration),
        growth_assessment=assess_growth_assumption(base.effective_annual_growth_pct, category),
    )
