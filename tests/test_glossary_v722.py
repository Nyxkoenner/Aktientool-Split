from stock_explorer.content.glossary import GLOSSARY, glossary_entry, search_glossary


def test_glossary_has_unique_bilingual_entries_and_https_resources() -> None:
    assert len(GLOSSARY) >= 10
    assert len(GLOSSARY) == len(set(GLOSSARY))

    for key, entry in GLOSSARY.items():
        assert entry.key == key
        assert entry.title("de")
        assert entry.title("en")
        assert entry.explanation("de")
        assert entry.explanation("en")
        for resource in entry.resources:
            assert resource.url("de").startswith("https://")
            assert resource.url("en").startswith("https://")


def test_glossary_search_is_language_aware() -> None:
    german = search_glossary("KGV", "de")
    english = search_glossary("price", "en")

    assert glossary_entry("pe_ratio") in german
    assert glossary_entry("pe_ratio") in english
    assert search_glossary("begriff-der-nicht-existiert", "de") == ()
