from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ScenarioInput:
    current_price: float
    current_eps: Optional[float]
    revenue_growth: float = 0.0
    margin_change_pct: float = 0.0
    target_pe: Optional[float] = None
    dividend_yield_pct: float = 0.0
    years: int = 1


@dataclass(frozen=True)
class ScenarioResult:
    estimated_eps: Optional[float]
    estimated_price: Optional[float]
    estimated_dividends: float
    estimated_total_return_pct: Optional[float]


def run_scenario(values: ScenarioInput) -> ScenarioResult:
    if values.current_price <= 0 or values.years <= 0:
        raise ValueError("Preis und Jahre müssen positiv sein.")
    estimated_eps = None
    estimated_price = None
    if values.current_eps is not None and values.target_pe is not None:
        growth_factor = (1.0 + values.revenue_growth) ** values.years
        margin_factor = max(0.0, 1.0 + values.margin_change_pct / 100.0)
        estimated_eps = values.current_eps * growth_factor * margin_factor
        estimated_price = estimated_eps * values.target_pe
    dividends = values.current_price * (values.dividend_yield_pct / 100.0) * values.years
    total_return = None
    if estimated_price is not None:
        total_return = ((estimated_price + dividends) / values.current_price - 1.0) * 100.0
    return ScenarioResult(estimated_eps, estimated_price, dividends, total_return)
