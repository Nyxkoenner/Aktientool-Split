from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd
import yfinance as yf

from .models import ProfileFetchResult


class CompanyProfileProvider(ABC):
    name: str = "Unbekannt"

    @abstractmethod
    def fetch_enrichment(self, ticker: str) -> ProfileFetchResult:
        raise NotImplementedError


def _safe_table(ticker_object: Any, method_name: str, attribute_name: str) -> pd.DataFrame:
    try:
        method = getattr(ticker_object, method_name, None)
        if callable(method):
            candidate = method()
            if isinstance(candidate, pd.DataFrame):
                return candidate.copy()
            if isinstance(candidate, dict):
                return pd.DataFrame(candidate)
    except Exception:
        pass
    try:
        candidate = getattr(ticker_object, attribute_name, None)
        if isinstance(candidate, pd.DataFrame):
            return candidate.copy()
        if isinstance(candidate, dict):
            return pd.DataFrame(candidate)
    except Exception:
        pass
    return pd.DataFrame()


def _safe_dict(ticker_object: Any, method_name: str, attribute_name: str) -> dict[str, Any]:
    try:
        method = getattr(ticker_object, method_name, None)
        if callable(method):
            candidate = method()
            if isinstance(candidate, dict):
                return candidate.copy()
    except Exception:
        pass
    try:
        candidate = getattr(ticker_object, attribute_name, None)
        if isinstance(candidate, dict):
            return candidate.copy()
    except Exception:
        pass
    return {}


class YahooCompanyProfileProvider(CompanyProfileProvider):
    name = "Yahoo Finance Profile"

    def fetch_enrichment(self, ticker: str) -> ProfileFetchResult:
        symbol = str(ticker or "").strip().upper()
        result: dict[str, Any] = {
            "major_holders": pd.DataFrame(),
            "institutional_holders": pd.DataFrame(),
            "mutualfund_holders": pd.DataFrame(),
            "insider_roster": pd.DataFrame(),
            "insider_transactions": pd.DataFrame(),
            "insider_purchases": pd.DataFrame(),
            "recommendations": pd.DataFrame(),
            "upgrades_downgrades": pd.DataFrame(),
            "revenue_estimate": pd.DataFrame(),
            "earnings_estimate": pd.DataFrame(),
            "growth_estimates": pd.DataFrame(),
            "sustainability": pd.DataFrame(),
            "analyst_targets": {},
            "errors": [],
        }
        if not symbol:
            return ProfileFetchResult(result, self.name, ["Ticker fehlt."])
        try:
            obj = yf.Ticker(symbol)
        except Exception as error:
            message = f"Ticker konnte nicht initialisiert werden: {error}"
            result["errors"].append(message)
            return ProfileFetchResult(result, self.name, [message])

        table_specs = [
            ("major_holders", "get_major_holders", "major_holders"),
            ("institutional_holders", "get_institutional_holders", "institutional_holders"),
            ("mutualfund_holders", "get_mutualfund_holders", "mutualfund_holders"),
            ("insider_roster", "get_insider_roster_holders", "insider_roster_holders"),
            ("insider_transactions", "get_insider_transactions", "insider_transactions"),
            ("insider_purchases", "get_insider_purchases", "insider_purchases"),
            ("recommendations", "get_recommendations_summary", "recommendations_summary"),
            ("upgrades_downgrades", "get_upgrades_downgrades", "upgrades_downgrades"),
            ("revenue_estimate", "get_revenue_estimate", "revenue_estimate"),
            ("earnings_estimate", "get_earnings_estimate", "earnings_estimate"),
            ("growth_estimates", "get_growth_estimates", "growth_estimates"),
            ("sustainability", "get_sustainability", "sustainability"),
        ]
        for key, method_name, attribute_name in table_specs:
            result[key] = _safe_table(obj, method_name, attribute_name)
        result["analyst_targets"] = _safe_dict(
            obj,
            "get_analyst_price_targets",
            "analyst_price_targets",
        )
        return ProfileFetchResult(result, self.name)
