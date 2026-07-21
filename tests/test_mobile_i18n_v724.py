from stock_explorer.i18n.translations import missing_translation_keys, translate


def test_mobile_display_translations_exist_in_both_languages() -> None:
    assert translate("ux.display.compact", "de") == "Kompakt / Smartphone"
    assert translate("ux.display.compact", "en") == "Compact / smartphone"
    assert translate("ux.display.help", "de") != "ux.display.help"
    assert translate("ux.display.help", "en") != "ux.display.help"
    assert missing_translation_keys().get("en", set()) == set()
