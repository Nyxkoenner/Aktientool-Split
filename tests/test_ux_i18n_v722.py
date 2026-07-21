from stock_explorer.i18n import missing_translation_keys, t


def test_ux_translations_exist_in_both_languages() -> None:
    assert not missing_translation_keys().get("en")
    assert t("ux.knowledge.beginner", "de") == "Einsteiger"
    assert t("ux.knowledge.beginner", "en") == "Beginner"
    assert "nykoenner" not in t("ux.feedback.privacy", "de")
