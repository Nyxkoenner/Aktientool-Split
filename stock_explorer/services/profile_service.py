from __future__ import annotations

from typing import Any

from stock_explorer.providers.company_profiles import CompanyProfileProvider


class CompanyProfileService:
    def __init__(self, providers: list[CompanyProfileProvider]) -> None:
        self._providers = list(providers)

    def fetch_enrichment(self, ticker: str) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        warnings: list[str] = []
        provider_names: list[str] = []
        for provider in self._providers:
            result = provider.fetch_enrichment(ticker)
            provider_names.append(result.provider_name)
            warnings.extend(result.warnings)
            for key, value in result.data.items():
                if key == "errors":
                    existing = list(merged.get("errors", []))
                    existing.extend(value if isinstance(value, list) else [value])
                    merged["errors"] = existing
                    continue
                current = merged.get(key)
                is_empty = current is None or getattr(current, "empty", False)
                if key not in merged or is_empty:
                    merged[key] = value
        merged["provider_names"] = provider_names
        merged["provider_warnings"] = warnings
        return merged
