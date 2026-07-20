from __future__ import annotations

from stock_explorer.providers.sec_companyfacts import build_official_financial_trend


def _fact(values):
    return {"units": {"USD": values}}


def test_build_official_financial_trend_calculates_free_cashflow():
    payload = {
        "facts": {
            "us-gaap": {
                "Revenues": _fact(
                    [{"end": "2025-12-31", "filed": "2026-02-01", "form": "10-K", "fp": "FY", "val": 1000}]
                ),
                "NetIncomeLoss": _fact(
                    [{"end": "2025-12-31", "filed": "2026-02-01", "form": "10-K", "fp": "FY", "val": 100}]
                ),
                "NetCashProvidedByUsedInOperatingActivities": _fact(
                    [{"end": "2025-12-31", "filed": "2026-02-01", "form": "10-K", "fp": "FY", "val": 180}]
                ),
                "PaymentsToAcquirePropertyPlantAndEquipment": _fact(
                    [{"end": "2025-12-31", "filed": "2026-02-01", "form": "10-K", "fp": "FY", "val": 50}]
                ),
            }
        }
    }
    result = build_official_financial_trend(payload)
    assert result.iloc[0]["revenue"] == 1000
    assert result.iloc[0]["free_cashflow"] == 130
