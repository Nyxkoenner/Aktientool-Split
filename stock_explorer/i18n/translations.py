from __future__ import annotations

TRANSLATIONS = {
    "de": {
        "app.title": "Aktien Explorer",
        "nav.overview": "Überblick",
        "nav.scenarios": "Szenarien",
        "nav.portfolio_sim": "Portfolio-Simulation",
        "nav.ai_lab": "KI-Labor",
        "common.no_data": "Keine Daten verfügbar.",
    },
    "en": {
        "app.title": "Stock Explorer",
        "nav.overview": "Overview",
        "nav.scenarios": "Scenarios",
        "nav.portfolio_sim": "Portfolio Simulation",
        "nav.ai_lab": "AI Lab",
        "common.no_data": "No data available.",
    },
}


def translate(key: str, language: str = "de", **values: object) -> str:
    table = TRANSLATIONS.get(language, TRANSLATIONS["de"])
    text = table.get(key, TRANSLATIONS["de"].get(key, key))
    return text.format(**values)
