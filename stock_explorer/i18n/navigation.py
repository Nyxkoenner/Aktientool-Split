from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NavigationItem:
    page_id: str
    translation_key: str
    legacy_label: str


MAIN_NAVIGATION: tuple[NavigationItem, ...] = (
    NavigationItem("start", "nav.start", "Start"),
    NavigationItem("pilot_center", "nav.pilot_center", "Pilot & Feedback"),
    NavigationItem("analysis_hub", "nav.analysis_hub", "Aktie analysieren"),
    NavigationItem("overview", "nav.overview", "Überblick"),
    NavigationItem("data_status", "nav.data_status", "Datenstatus"),
    NavigationItem("fundamentals", "nav.fundamentals", "Fundamentaldaten"),
    NavigationItem("stock_profiles", "nav.stock_profiles", "Aktienprofile"),
    NavigationItem("analysis", "nav.analysis", "Einzelanalyse"),
    NavigationItem("sectors", "nav.sectors", "Sektoren"),
    NavigationItem("news", "nav.news", "News & Events"),
    NavigationItem("sources", "nav.sources", "Datenquellen"),
    NavigationItem("portfolio", "nav.portfolio", "Portfolio"),
    NavigationItem("portfolio_sim", "nav.portfolio_sim", "Portfolio-Simulation"),
    NavigationItem("scenarios", "nav.scenarios", "Szenarien"),
    NavigationItem("ai_lab", "nav.ai_lab", "KI-/RL-Labor"),
    NavigationItem("watchlist", "nav.watchlist", "Watchlist"),
    NavigationItem("value_scanner", "nav.value_scanner", "Value-Scanner"),
    NavigationItem("deep_value", "nav.deep_value", "Deep Value"),
    NavigationItem("backtesting", "nav.backtesting", "Backtesting"),
    NavigationItem("patterns", "nav.patterns", "Mustervergleich"),
    NavigationItem("learning", "nav.learning", "Lernmodul"),
    NavigationItem("company_profiles", "nav.company_profiles", "Unternehmensprofile"),
    NavigationItem("superinvestors", "nav.superinvestors", "Superinvestoren"),
    NavigationItem("research", "nav.research", "Research"),
)

_PAGE_BY_ID = {item.page_id: item for item in MAIN_NAVIGATION}
_PAGE_BY_LEGACY = {item.legacy_label: item.page_id for item in MAIN_NAVIGATION}
_FALLBACK_PAGE_ID = "overview"


def normalize_page_id(value: str | None) -> str:
    candidate = str(value or "").strip()
    if candidate in _PAGE_BY_ID:
        return candidate
    return _PAGE_BY_LEGACY.get(candidate, _FALLBACK_PAGE_ID)


def legacy_page_label(page_id: str) -> str:
    return _PAGE_BY_ID.get(normalize_page_id(page_id), _PAGE_BY_ID[_FALLBACK_PAGE_ID]).legacy_label


def translation_key_for_page(page_id: str) -> str:
    return _PAGE_BY_ID[normalize_page_id(page_id)].translation_key
