from __future__ import annotations

from typing import Any

import pandas as pd

from .company_profiles import CompanyProfileProvider
from .models import ProfileFetchResult
from .sec import SecProvider

CONCEPTS: dict[str, tuple[str, ...]] = {
    "revenue": (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    ),
    "net_income": ("NetIncomeLoss", "ProfitLoss"),
    "operating_cashflow": ("NetCashProvidedByUsedInOperatingActivities",),
    "capex": (
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsForProceedsFromOtherPropertyPlantAndEquipment",
    ),
    "assets": ("Assets",),
    "liabilities": ("Liabilities",),
    "debt_current": (
        "ShortTermBorrowings",
        "LongTermDebtCurrent",
        "ShortTermDebtCurrent",
    ),
    "debt_noncurrent": ("LongTermDebtNoncurrent", "LongTermDebt"),
    "dividends_paid": (
        "PaymentsOfDividends",
        "PaymentsOfDividendsCommonStock",
        "PaymentsOfOrdinaryDividends",
    ),
}


def _concept_units(payload: dict[str, Any], names: tuple[str, ...]) -> list[dict[str, Any]]:
    gaap = payload.get("facts", {}).get("us-gaap", {})
    if not isinstance(gaap, dict):
        return []
    for name in names:
        concept = gaap.get(name)
        if not isinstance(concept, dict):
            continue
        units = concept.get("units", {})
        if not isinstance(units, dict):
            continue
        for unit_name in ("USD", "USD/shares", "shares"):
            values = units.get(unit_name)
            if isinstance(values, list) and values:
                return [item for item in values if isinstance(item, dict)]
        for values in units.values():
            if isinstance(values, list) and values:
                return [item for item in values if isinstance(item, dict)]
    return []


def _annual_values(payload: dict[str, Any], names: tuple[str, ...]) -> pd.DataFrame:
    rows = _concept_units(payload, names)
    if not rows:
        return pd.DataFrame(columns=["fiscal_date", "value", "filed", "form"])
    frame = pd.DataFrame(rows)
    for column in ["end", "filed"]:
        frame[column] = pd.to_datetime(frame.get(column), errors="coerce")
    frame["val"] = pd.to_numeric(frame.get("val"), errors="coerce")
    form = frame.get("form", pd.Series("", index=frame.index)).astype(str).str.upper()
    fp = frame.get("fp", pd.Series("", index=frame.index)).astype(str).str.upper()
    frame = frame[form.isin({"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"})]
    if "fp" in frame.columns:
        frame = frame[fp.isin({"FY", ""})]
    frame = frame.dropna(subset=["end", "val"])
    if frame.empty:
        return pd.DataFrame(columns=["fiscal_date", "value", "filed", "form"])
    frame = frame.sort_values(["end", "filed"]).drop_duplicates("end", keep="last")
    return frame.rename(columns={"end": "fiscal_date", "val": "value"})[
        ["fiscal_date", "value", "filed", "form"]
    ]


def build_official_financial_trend(payload: dict[str, Any]) -> pd.DataFrame:
    merged: pd.DataFrame | None = None
    for output_name, concepts in CONCEPTS.items():
        values = _annual_values(payload, concepts).rename(columns={"value": output_name})
        values = values[["fiscal_date", output_name]]
        if merged is None:
            merged = values
        else:
            merged = merged.merge(values, on="fiscal_date", how="outer")
    if merged is None or merged.empty:
        return pd.DataFrame()

    merged = merged.sort_values("fiscal_date").reset_index(drop=True)
    for column in CONCEPTS:
        if column not in merged.columns:
            merged[column] = pd.NA
        merged[column] = pd.to_numeric(merged[column], errors="coerce")
    merged["free_cashflow"] = merged["operating_cashflow"] - merged["capex"].abs()
    merged["total_debt"] = merged[["debt_current", "debt_noncurrent"]].fillna(0).sum(axis=1)
    merged["source"] = "SEC Company Facts"
    return merged


class SecCompanyFactsProfileProvider(CompanyProfileProvider):
    name = "SEC Company Facts"

    def __init__(self, sec_provider: SecProvider) -> None:
        self._sec = sec_provider

    def fetch_enrichment(self, ticker: str) -> ProfileFetchResult:
        payload, diagnostic = self._sec.company_facts(ticker)
        warnings: list[str] = []
        if diagnostic.message:
            warnings.append(diagnostic.message)
        trend = build_official_financial_trend(payload) if payload else pd.DataFrame()
        data: dict[str, Any] = {
            "official_financials": trend,
            "official_profile_source": self.name,
            "official_profile_diagnostic": diagnostic.to_dict(),
            "sec_entity_name": str(payload.get("entityName", "")) if payload else "",
            "sec_cik": str(payload.get("cik", "")) if payload else "",
        }
        return ProfileFetchResult(data=data, provider_name=self.name, warnings=warnings)
