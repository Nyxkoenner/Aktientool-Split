from __future__ import annotations

import pandas as pd

from stock_explorer.providers.company_profiles import CompanyProfileProvider
from stock_explorer.providers.models import ProfileFetchResult
from stock_explorer.services.profile_service import CompanyProfileService


class EmptyProvider(CompanyProfileProvider):
    name = "empty"

    def fetch_enrichment(self, ticker: str) -> ProfileFetchResult:
        return ProfileFetchResult(
            {"institutional_holders": pd.DataFrame(), "errors": []},
            self.name,
        )


class FilledProvider(CompanyProfileProvider):
    name = "filled"

    def fetch_enrichment(self, ticker: str) -> ProfileFetchResult:
        return ProfileFetchResult(
            {
                "institutional_holders": pd.DataFrame([{"holder": "Fund A"}]),
                "analyst_targets": {"mean": 100},
                "errors": [],
            },
            self.name,
        )


def test_profile_service_uses_first_non_empty_value():
    result = CompanyProfileService([EmptyProvider(), FilledProvider()]).fetch_enrichment("AAA")

    assert len(result["institutional_holders"]) == 1
    assert result["analyst_targets"]["mean"] == 100
    assert result["provider_names"] == ["empty", "filled"]
