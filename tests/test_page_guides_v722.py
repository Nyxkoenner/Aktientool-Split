from stock_explorer.content.page_guides import page_guide
from stock_explorer.domain.ux_preferences import KnowledgeLevel
from stock_explorer.i18n.navigation import MAIN_NAVIGATION


def test_every_navigation_page_receives_guidance() -> None:
    for item in MAIN_NAVIGATION:
        guide = page_guide(item.page_id)
        assert guide.title("de")
        assert guide.title("en")
        assert guide.summary("de", KnowledgeLevel.BEGINNER)
        assert guide.summary("en", KnowledgeLevel.EXPERT)
