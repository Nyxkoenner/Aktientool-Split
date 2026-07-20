from __future__ import annotations

from typing import Any

import pandas as pd

from stock_explorer.providers.company_profiles import CompanyProfileProvider


class CompanyProfileService:
    def __init__(self, providers: list[CompanyProfileProvider]) -> None:
        self._providers = list(providers)

    @staticmethod
    def _is_empty(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, pd.DataFrame):
            return value.empty
        if isinstance(value, dict):
            return not value
        if isinstance(value, (list, tuple, set)):
            return not value
        return False

    def fetch_enrichment(self, ticker: str) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        warnings: list[str] = []
        provider_names: list[str] = []
        provider_status: list[dict[str, Any]] = []
        for provider in self._providers:
            result = provider.fetch_enrichment(ticker)
            provider_names.append(result.provider_name)
            warnings.extend(result.warnings)
            available_keys: list[str] = []
            for key, value in result.data.items():
                if key == "errors":
                    existing = list(merged.get("errors", []))
                    existing.extend(value if isinstance(value, list) else [value])
                    merged["errors"] = existing
                    continue
                if not self._is_empty(value):
                    available_keys.append(key)
                current = merged.get(key)
                if key not in merged or self._is_empty(current):
                    merged[key] = value
            provider_status.append(
                {
                    "provider": result.provider_name,
                    "available_fields": len(available_keys),
                    "warnings": " | ".join(result.warnings),
                }
            )
        merged["provider_names"] = provider_names
        merged["provider_warnings"] = warnings
        merged["provider_status"] = pd.DataFrame(provider_status)
        return merged
