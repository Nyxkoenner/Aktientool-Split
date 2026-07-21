from pathlib import Path

from stock_explorer.i18n.navigation import normalize_page_id, translation_key_for_page
from stock_explorer.ui.navigation_model import all_grouped_pages, navigation_group_for_page


def test_pilot_center_is_a_first_class_navigation_page() -> None:
    assert normalize_page_id("pilot_center") == "pilot_center"
    assert translation_key_for_page("pilot_center") == "nav.pilot_center"
    assert navigation_group_for_page("pilot_center") == "start"
    assert "pilot_center" in all_grouped_pages()


def test_runtime_allows_pilot_center_without_loaded_market_data() -> None:
    source = Path("stock_explorer/app_runtime.py").read_text(encoding="utf-8")

    assert 'if active_page in {"start", "pilot_center"}:' in source
    assert 'if active_page == "pilot_center":' in source
    assert '"pilot_center": lambda: render_pilot_center(' in source
