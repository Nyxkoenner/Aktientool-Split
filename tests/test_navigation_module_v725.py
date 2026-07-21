from stock_explorer.ui.navigation_model import (
    NAVIGATION_GROUPS,
    all_grouped_pages,
    default_page_for_group,
    navigation_group_for_page,
)


def test_navigation_model_is_importable_and_complete() -> None:
    assert len(NAVIGATION_GROUPS) == 5
    assert default_page_for_group("stocks") == "analysis_hub"
    assert navigation_group_for_page("ai_lab") == "research"
    assert "start" in all_grouped_pages()
    assert "portfolio_sim" in all_grouped_pages()
