from stock_explorer.i18n.translations import TRANSLATIONS, missing_translation_keys


def test_ai_model_translations_exist_in_both_languages() -> None:
    required = {
        "ai.model.title",
        "ai.model.train_full",
        "ai.model.continue",
        "ai.model.evaluate",
        "ai.model.delete",
        "ai.model.disclaimer",
    }
    assert required.issubset(TRANSLATIONS["de"])
    assert required.issubset(TRANSLATIONS["en"])
    assert not missing_translation_keys().get("en")
