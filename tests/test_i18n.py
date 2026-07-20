from stock_explorer.i18n import (
    format_date,
    format_number,
    format_percent,
    missing_translation_keys,
    normalize_language,
    translate,
)


def test_translation_catalog_is_complete() -> None:
    assert missing_translation_keys() == {"en": set()}


def test_language_normalization_and_fallback() -> None:
    assert normalize_language("EN") == "en"
    assert normalize_language("unknown") == "de"
    assert translate("app.title", "en") == "Stock Explorer"
    assert translate("does.not.exist", "en") == "does.not.exist"


def test_locale_formatting() -> None:
    assert format_number(1234.56, 2, "de") == "1.234,56"
    assert format_number(1234.56, 2, "en") == "1,234.56"
    assert format_percent(12.5, 1, "de", signed=True) == "+12,5 %"
    assert format_date("2026-07-20", "de") == "20.07.2026"
    assert format_date("2026-07-20", "en") == "2026-07-20"
