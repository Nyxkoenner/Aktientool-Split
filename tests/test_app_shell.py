from stock_explorer.i18n.navigation import (
    MAIN_NAVIGATION,
    legacy_page_label,
    normalize_page_id,
)


def test_navigation_ids_are_unique() -> None:
    page_ids = [item.page_id for item in MAIN_NAVIGATION]
    assert len(page_ids) == len(set(page_ids))


def test_legacy_navigation_values_are_migrated() -> None:
    assert normalize_page_id("Einzelanalyse") == "analysis"
    assert normalize_page_id("News & Events") == "news"
    assert normalize_page_id("analysis") == "analysis"
    assert normalize_page_id("not-known") == "overview"
    assert legacy_page_label("portfolio_sim") == "Portfolio-Simulation"
