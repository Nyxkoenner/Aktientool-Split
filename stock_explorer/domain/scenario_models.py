from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Final

SECTOR_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    "bank": ("bank", "banken", "specialty finance", "financial services"),
    "insurance": ("insurance", "versicherung"),
    "real_estate": ("real estate", "reit", "immobil"),
    "technology": ("technology", "software", "semiconductor", "it services", "technologie"),
    "industrial": (
        "industrial",
        "machinery",
        "aerospace",
        "automotive",
        "transportation",
        "industrie",
        "maschinenbau",
    ),
    "utility": ("utility", "utilities", "versorgung", "energy infrastructure"),
    "energy": ("energy", "oil", "gas", "energie"),
    "consumer": (
        "consumer",
        "retail",
        "food",
        "beverage",
        "tobacco",
        "leisure",
        "lebensmittel",
        "konsum",
    ),
    "healthcare": ("healthcare", "pharma", "biotech", "medical", "gesundheit"),
}


@dataclass(frozen=True)
class CompanyScenarioSnapshot:
    current_price: float
    current_eps: float | None
    current_pe: float | None
    dividend_yield_pct: float
    revenue_growth_pct: float
    operating_margin_pct: float | None
    net_debt_ebitda: float | None
    beta: float | None
    sector: str
    currency: str = ""


@dataclass(frozen=True)
class ScenarioShock:
    annual_growth_delta_pct: float = 0.0
    margin_change_pct: float = 0.0
    valuation_change_pct: float = 0.0
    dividend_change_pct: float = 0.0
    financing_earnings_impact_pct: float = 0.0
    sector_earnings_impact_pct: float = 0.0
    fx_earnings_impact_pct: float = 0.0


@dataclass(frozen=True)
class ScenarioOutcome:
    estimated_eps: float | None
    target_pe: float | None
    estimated_price: float | None
    estimated_dividends: float
    estimated_total_return_pct: float | None
    effective_annual_growth_pct: float
    effective_margin_change_pct: float


@dataclass(frozen=True)
class ScenarioPreset:
    preset_id: str
    shock: ScenarioShock
    assumption_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]


def classify_sector(sector: str | None) -> str:
    normalized = str(sector or "").strip().lower()
    for category, aliases in SECTOR_ALIASES.items():
        if any(alias in normalized for alias in aliases):
            return category
    return "generic"


def _base_preset(preset_id: str) -> ScenarioPreset:
    presets: dict[str, ScenarioPreset] = {
        "base": ScenarioPreset(
            preset_id="base",
            shock=ScenarioShock(),
            assumption_codes=("base_growth", "stable_margin", "stable_valuation"),
            risk_codes=("model_uncertainty",),
        ),
        "recession": ScenarioPreset(
            preset_id="recession",
            shock=ScenarioShock(
                annual_growth_delta_pct=-8.0,
                margin_change_pct=-12.0,
                valuation_change_pct=-20.0,
                dividend_change_pct=-15.0,
                sector_earnings_impact_pct=-5.0,
            ),
            assumption_codes=("demand_slowdown", "margin_pressure", "risk_premium_up"),
            risk_codes=("cyclical_downturn", "dividend_pressure", "valuation_compression"),
        ),
        "rate_hike": ScenarioPreset(
            preset_id="rate_hike",
            shock=ScenarioShock(
                annual_growth_delta_pct=-2.0,
                valuation_change_pct=-15.0,
                dividend_change_pct=-5.0,
                financing_earnings_impact_pct=-8.0,
            ),
            assumption_codes=("higher_funding_costs", "discount_rate_up"),
            risk_codes=("refinancing", "valuation_compression"),
        ),
        "inflation": ScenarioPreset(
            preset_id="inflation",
            shock=ScenarioShock(
                annual_growth_delta_pct=-2.0,
                margin_change_pct=-10.0,
                valuation_change_pct=-10.0,
                sector_earnings_impact_pct=-4.0,
            ),
            assumption_codes=("input_costs_up", "pricing_power_test"),
            risk_codes=("margin_pressure", "demand_slowdown"),
        ),
        "margin_pressure": ScenarioPreset(
            preset_id="margin_pressure",
            shock=ScenarioShock(
                annual_growth_delta_pct=-1.0,
                margin_change_pct=-20.0,
                valuation_change_pct=-10.0,
                dividend_change_pct=-10.0,
            ),
            assumption_codes=("cost_inflation", "limited_pricing_power"),
            risk_codes=("earnings_revision", "dividend_pressure"),
        ),
        "dividend_cut": ScenarioPreset(
            preset_id="dividend_cut",
            shock=ScenarioShock(
                valuation_change_pct=-8.0,
                dividend_change_pct=-50.0,
                sector_earnings_impact_pct=-5.0,
            ),
            assumption_codes=("payout_reset", "cash_preservation"),
            risk_codes=("income_loss", "confidence_loss"),
        ),
        "deleveraging": ScenarioPreset(
            preset_id="deleveraging",
            shock=ScenarioShock(
                annual_growth_delta_pct=-1.5,
                margin_change_pct=-2.0,
                valuation_change_pct=8.0,
                dividend_change_pct=-20.0,
                financing_earnings_impact_pct=8.0,
            ),
            assumption_codes=("cash_to_debt", "lower_interest_burden"),
            risk_codes=("slower_growth", "temporary_income_loss"),
        ),
        "valuation_normalization": ScenarioPreset(
            preset_id="valuation_normalization",
            shock=ScenarioShock(valuation_change_pct=-25.0),
            assumption_codes=("multiple_mean_reversion",),
            risk_codes=("valuation_compression",),
        ),
        "currency_shock": ScenarioPreset(
            preset_id="currency_shock",
            shock=ScenarioShock(
                annual_growth_delta_pct=-1.0,
                valuation_change_pct=-5.0,
                fx_earnings_impact_pct=-10.0,
            ),
            assumption_codes=("adverse_fx",),
            risk_codes=("translation_effect", "transaction_effect"),
        ),
        "custom": ScenarioPreset(
            preset_id="custom",
            shock=ScenarioShock(),
            assumption_codes=("custom_assumptions",),
            risk_codes=("model_uncertainty",),
        ),
    }
    return presets[preset_id]


def sector_adjusted_preset(preset_id: str, sector: str | None) -> ScenarioPreset:
    preset = _base_preset(preset_id)
    category = classify_sector(sector)
    shock = preset.shock
    assumptions = list(preset.assumption_codes)
    risks = list(preset.risk_codes)

    if preset_id == "recession":
        if category == "bank":
            shock = replace(shock, sector_earnings_impact_pct=-18.0, dividend_change_pct=-25.0)
            assumptions.append("credit_losses_up")
            risks.append("capital_pressure")
        elif category == "insurance":
            shock = replace(shock, sector_earnings_impact_pct=-10.0)
            assumptions.append("claims_and_markets")
        elif category == "real_estate":
            shock = replace(
                shock,
                annual_growth_delta_pct=-5.0,
                valuation_change_pct=-28.0,
                financing_earnings_impact_pct=-12.0,
                dividend_change_pct=-20.0,
            )
            assumptions.append("occupancy_and_refinancing")
        elif category == "technology":
            shock = replace(shock, annual_growth_delta_pct=-12.0, valuation_change_pct=-30.0)
            assumptions.append("growth_multiple_reset")
        elif category == "industrial":
            shock = replace(shock, annual_growth_delta_pct=-12.0, margin_change_pct=-15.0)
            assumptions.append("order_intake_down")
        elif category == "utility":
            shock = replace(shock, annual_growth_delta_pct=-2.0, margin_change_pct=-5.0)
        elif category == "consumer":
            shock = replace(shock, annual_growth_delta_pct=-10.0, margin_change_pct=-12.0)
            assumptions.append("consumer_spending_down")

    if preset_id == "rate_hike":
        if category == "bank":
            shock = replace(
                shock,
                valuation_change_pct=-5.0,
                financing_earnings_impact_pct=6.0,
                sector_earnings_impact_pct=-3.0,
            )
            assumptions.extend(("net_interest_margin_up", "credit_quality_watch"))
        elif category == "insurance":
            shock = replace(shock, financing_earnings_impact_pct=5.0, valuation_change_pct=-5.0)
            assumptions.append("investment_income_up")
        elif category == "real_estate":
            shock = replace(
                shock,
                annual_growth_delta_pct=-4.0,
                valuation_change_pct=-30.0,
                financing_earnings_impact_pct=-18.0,
                dividend_change_pct=-15.0,
            )
            assumptions.append("refinancing_pressure")
        elif category == "utility":
            shock = replace(shock, financing_earnings_impact_pct=-12.0, valuation_change_pct=-18.0)

    if preset_id == "inflation":
        if category == "energy":
            shock = replace(
                shock,
                annual_growth_delta_pct=8.0,
                margin_change_pct=12.0,
                valuation_change_pct=5.0,
                sector_earnings_impact_pct=8.0,
            )
            assumptions.append("commodity_price_tailwind")
        elif category == "industrial":
            shock = replace(shock, margin_change_pct=-15.0, sector_earnings_impact_pct=-6.0)
        elif category == "consumer":
            shock = replace(shock, annual_growth_delta_pct=-5.0, margin_change_pct=-14.0)
        elif category == "technology":
            shock = replace(shock, valuation_change_pct=-20.0, margin_change_pct=-6.0)

    if preset_id == "valuation_normalization" and category == "technology":
        shock = replace(shock, valuation_change_pct=-35.0)

    if preset_id == "deleveraging" and category in {"real_estate", "utility"}:
        shock = replace(shock, financing_earnings_impact_pct=12.0, valuation_change_pct=12.0)

    return ScenarioPreset(
        preset_id=preset.preset_id,
        shock=shock,
        assumption_codes=tuple(dict.fromkeys(assumptions)),
        risk_codes=tuple(dict.fromkeys(risks)),
    )


def run_sector_scenario(
    snapshot: CompanyScenarioSnapshot,
    shock: ScenarioShock,
    years: int,
) -> ScenarioOutcome:
    if snapshot.current_price <= 0:
        raise ValueError("current_price must be positive")
    if years <= 0:
        raise ValueError("years must be positive")

    base_growth = max(-70.0, min(snapshot.revenue_growth_pct, 100.0))
    effective_growth_pct = max(-80.0, min(base_growth + shock.annual_growth_delta_pct, 120.0))
    growth_factor = (1.0 + effective_growth_pct / 100.0) ** years
    margin_factor = max(0.05, 1.0 + shock.margin_change_pct / 100.0)
    financing_factor = max(0.05, 1.0 + shock.financing_earnings_impact_pct / 100.0)
    sector_factor = max(0.05, 1.0 + shock.sector_earnings_impact_pct / 100.0)
    fx_factor = max(0.05, 1.0 + shock.fx_earnings_impact_pct / 100.0)

    estimated_eps: float | None = None
    estimated_price: float | None = None
    target_pe: float | None = None
    if snapshot.current_eps is not None and snapshot.current_eps > 0:
        estimated_eps = (
            snapshot.current_eps
            * growth_factor
            * margin_factor
            * financing_factor
            * sector_factor
            * fx_factor
        )
        pe_anchor = (
            snapshot.current_pe if snapshot.current_pe is not None and snapshot.current_pe > 0 else 12.0
        )
        target_pe = max(2.0, min(pe_anchor * (1.0 + shock.valuation_change_pct / 100.0), 80.0))
        estimated_price = estimated_eps * target_pe

    dividend_factor = max(0.0, 1.0 + shock.dividend_change_pct / 100.0)
    estimated_dividends = (
        snapshot.current_price * (snapshot.dividend_yield_pct / 100.0) * dividend_factor * years
    )
    total_return: float | None = None
    if estimated_price is not None:
        total_return = ((estimated_price + estimated_dividends) / snapshot.current_price - 1.0) * 100.0

    return ScenarioOutcome(
        estimated_eps=estimated_eps,
        target_pe=target_pe,
        estimated_price=estimated_price,
        estimated_dividends=estimated_dividends,
        estimated_total_return_pct=total_return,
        effective_annual_growth_pct=effective_growth_pct,
        effective_margin_change_pct=shock.margin_change_pct,
    )


def band_shock(shock: ScenarioShock, direction: str) -> ScenarioShock:
    if direction not in {"weak", "strong"}:
        raise ValueError("direction must be 'weak' or 'strong'")
    sign = -1.0 if direction == "weak" else 1.0
    return replace(
        shock,
        annual_growth_delta_pct=shock.annual_growth_delta_pct + sign * 3.0,
        margin_change_pct=shock.margin_change_pct + sign * 5.0,
        valuation_change_pct=shock.valuation_change_pct + sign * 10.0,
        dividend_change_pct=shock.dividend_change_pct + sign * 10.0,
        financing_earnings_impact_pct=shock.financing_earnings_impact_pct + sign * 3.0,
        sector_earnings_impact_pct=shock.sector_earnings_impact_pct + sign * 5.0,
        fx_earnings_impact_pct=shock.fx_earnings_impact_pct + sign * 3.0,
    )
