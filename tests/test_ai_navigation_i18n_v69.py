from stock_explorer.i18n.navigation import MAIN_NAVIGATION, normalize_page_id
from stock_explorer.i18n.translations import missing_translation_keys, translate


def test_ai_lab_navigation_and_translations() -> None:
    page_ids = [item.page_id for item in MAIN_NAVIGATION]
    assert "ai_lab" in page_ids
    assert normalize_page_id("KI-/RL-Labor") == "ai_lab"
    assert translate("nav.ai_lab", "de") == "KI-/RL-Labor"
    assert translate("nav.ai_lab", "en") == "AI / RL lab"
    assert missing_translation_keys().get("en", set()) == set()
