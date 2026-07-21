"""Hierarchisches Navigationsmodell für die reduzierte V7.2.3-Oberfläche."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class NavigationGroup:
    """Eine Hauptnavigation mit den darin sichtbaren Fachseiten."""

    group_id: str
    translation_key: str
    pages: tuple[str, ...]
    default_page: str

    def __post_init__(self) -> None:
        if not self.pages:
            raise ValueError("Eine Navigationsgruppe benötigt mindestens eine Seite.")
        if self.default_page not in self.pages:
            raise ValueError("Die Standardseite muss Teil der Navigationsgruppe sein.")


NAVIGATION_GROUPS: Final[tuple[NavigationGroup, ...]] = (
    NavigationGroup(
        group_id="start",
        translation_key="ux.nav.group.start",
        pages=("start",),
        default_page="start",
    ),
    NavigationGroup(
        group_id="stocks",
        translation_key="ux.nav.group.stocks",
        pages=(
            "analysis_hub",
            "overview",
            "fundamentals",
            "stock_profiles",
            "analysis",
            "sectors",
            "scenarios",
            "company_profiles",
        ),
        default_page="analysis_hub",
    ),
    NavigationGroup(
        group_id="portfolio",
        translation_key="ux.nav.group.portfolio",
        pages=("portfolio", "portfolio_sim"),
        default_page="portfolio",
    ),
    NavigationGroup(
        group_id="events",
        translation_key="ux.nav.group.events",
        pages=("watchlist", "news", "sources"),
        default_page="watchlist",
    ),
    NavigationGroup(
        group_id="research",
        translation_key="ux.nav.group.research",
        pages=(
            "research",
            "value_scanner",
            "deep_value",
            "backtesting",
            "patterns",
            "ai_lab",
            "learning",
            "superinvestors",
            "data_status",
        ),
        default_page="research",
    ),
)

_GROUP_BY_ID: Final = {group.group_id: group for group in NAVIGATION_GROUPS}
_GROUP_BY_PAGE: Final = {page_id: group.group_id for group in NAVIGATION_GROUPS for page_id in group.pages}

NAVIGATION_REQUEST_KEY: Final = "navigation_request"
ACTIVE_PAGE_KEY: Final = "main_navigation"
GROUP_WIDGET_KEY: Final = "main_navigation_group"
PAGE_WIDGET_PREFIX: Final = "main_navigation_page_"


def navigation_group(group_id: str) -> NavigationGroup:
    """Liefert eine Gruppe und fällt bei unbekannten IDs auf Start zurück."""
    return _GROUP_BY_ID.get(str(group_id), NAVIGATION_GROUPS[0])


def navigation_group_for_page(page_id: str) -> str:
    """Ordnet eine Fachseite ihrer Hauptnavigation zu."""
    return _GROUP_BY_PAGE.get(str(page_id), NAVIGATION_GROUPS[0].group_id)


def default_page_for_group(group_id: str) -> str:
    return navigation_group(group_id).default_page


def all_grouped_pages() -> tuple[str, ...]:
    """Liefert alle Seiten genau in der sichtbaren Navigationsreihenfolge."""
    return tuple(page_id for group in NAVIGATION_GROUPS for page_id in group.pages)


def page_widget_key(group_id: str) -> str:
    return f"{PAGE_WIDGET_PREFIX}{navigation_group(group_id).group_id}"


__all__ = [
    "ACTIVE_PAGE_KEY",
    "GROUP_WIDGET_KEY",
    "NAVIGATION_GROUPS",
    "NAVIGATION_REQUEST_KEY",
    "NavigationGroup",
    "all_grouped_pages",
    "default_page_for_group",
    "navigation_group",
    "navigation_group_for_page",
    "page_widget_key",
]
