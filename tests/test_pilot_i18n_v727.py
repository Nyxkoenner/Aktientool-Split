from stock_explorer.i18n import TRANSLATIONS, missing_translation_keys

REQUIRED_KEYS = {
    "nav.pilot_center",
    "pilot.banner",
    "pilot.onboarding.title",
    "pilot.center.title",
    "pilot.demo.title",
    "pilot.tasks.title",
    "pilot.feedback.title",
    "pilot.admin.title",
}


def test_pilot_translations_exist_in_both_languages() -> None:
    for language in ("de", "en"):
        assert REQUIRED_KEYS.issubset(TRANSLATIONS[language])
    assert missing_translation_keys() == {"en": set()}
