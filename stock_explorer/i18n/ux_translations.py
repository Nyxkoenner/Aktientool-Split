"""Übersetzungen für die UX-Grundlagen ab V7.2.2."""

from __future__ import annotations

from typing import Final

UX_TRANSLATIONS: Final[dict[str, dict[str, str]]] = {
    "de": {
        "ux.knowledge.label": "Wissensmodus",
        "ux.knowledge.help": (
            "Der Wissensmodus verändert Erklärungen und Hilfen, nicht die zugrunde liegenden Berechnungen."
        ),
        "ux.knowledge.beginner": "Einsteiger",
        "ux.knowledge.intermediate": "Fortgeschritten",
        "ux.knowledge.expert": "Experte",
        "ux.knowledge.caption.beginner": "Mehr Führung, weniger Fachsprache und konkrete nächste Schritte.",
        "ux.knowledge.caption.intermediate": "Kennzahlen, Vergleiche und kompakte Methodikhinweise.",
        "ux.knowledge.caption.expert": "Mehr Fokus auf Annahmen, Datenqualität und Modellgrenzen.",
        "ux.glossary.title": "Börsenlexikon",
        "ux.glossary.caption": "Begriffe direkt im Tool nachschlagen. Externe Links öffnen fremde Webseiten.",
        "ux.glossary.search": "Begriff suchen",
        "ux.glossary.placeholder": "z. B. KGV, Drawdown oder Cashflow",
        "ux.glossary.no_results": "Kein passender Begriff gefunden.",
        "ux.glossary.more": "Erklärung öffnen",
        "ux.glossary.why": "Warum ist das wichtig?",
        "ux.glossary.limits": "Grenzen der Kennzahl",
        "ux.guide.steps": "Empfohlene Reihenfolge",
        "ux.guide.terms": "Passende Begriffe",
        "ux.guide.external_notice": (
            "Externe Artikel dienen nur der Vertiefung. Inhalte und Verfügbarkeit liegen beim jeweiligen Anbieter."
        ),
        "ux.trust.summary": (
            "Datenstand: {timestamp} · Hauptquelle: {provider} · Abdeckung: {coverage} · Datenqualität: {quality}"
        ),
        "ux.trust.details": "Daten, Quellen und Annahmen",
        "ux.trust.source_line": "**Quelle:** {provider}  \n**Datenstand:** {timestamp}",
        "ux.trust.context_line": (
            "**Abdeckung:** {coverage}  \n**Basiswährung:** {currency}  \n**Scanner-Profil:** {profile}"
        ),
        "ux.trust.model_notice": (
            "Scores, Szenarien, Backtests und KI-Ergebnisse sind berechnete Modelle. Sie können Datenlücken, "
            "Sondereffekte und strukturelle Veränderungen nicht vollständig abbilden."
        ),
        "ux.trust.quality.high": "hoch",
        "ux.trust.quality.medium": "mittel",
        "ux.trust.quality.low": "eingeschränkt",
        "ux.trust.quality.unknown": "unbekannt",
        "ux.feedback.title": "Feedback geben",
        "ux.feedback.caption": (
            "Das lokale E-Mail-Programm wird mit einer vorbereiteten Nachricht an {recipient} geöffnet. "
            "Die Nachricht wird erst nach deiner Bestätigung versendet."
        ),
        "ux.feedback.category": "Kategorie",
        "ux.feedback.category.bug": "Fehler",
        "ux.feedback.category.idea": "Verbesserungsidee",
        "ux.feedback.category.question": "Verständnisfrage",
        "ux.feedback.category.data": "Datenproblem",
        "ux.feedback.message": "Nachricht",
        "ux.feedback.placeholder": "Was ist passiert oder was sollte verbessert werden?",
        "ux.feedback.open_email": "Feedback-E-Mail öffnen",
        "ux.feedback.privacy": (
            "Automatisch ergänzt werden nur App-Version, aktueller Bereich, Sprache und Wissensmodus. "
            "Portfolio-, Dokument- und Modelldaten werden nicht angehängt."
        ),
    },
    "en": {
        "ux.knowledge.label": "Knowledge mode",
        "ux.knowledge.help": (
            "Knowledge mode changes explanations and guidance, not the underlying calculations."
        ),
        "ux.knowledge.beginner": "Beginner",
        "ux.knowledge.intermediate": "Intermediate",
        "ux.knowledge.expert": "Expert",
        "ux.knowledge.caption.beginner": "More guidance, less jargon and clear next steps.",
        "ux.knowledge.caption.intermediate": "Metrics, comparisons and compact methodology notes.",
        "ux.knowledge.caption.expert": "More focus on assumptions, data quality and model limitations.",
        "ux.glossary.title": "Investment glossary",
        "ux.glossary.caption": "Look up terms inside the tool. External links open third-party websites.",
        "ux.glossary.search": "Search term",
        "ux.glossary.placeholder": "e.g. P/E, drawdown or cash flow",
        "ux.glossary.no_results": "No matching term found.",
        "ux.glossary.more": "Open explanation",
        "ux.glossary.why": "Why does it matter?",
        "ux.glossary.limits": "Limitations",
        "ux.guide.steps": "Suggested sequence",
        "ux.guide.terms": "Related terms",
        "ux.guide.external_notice": (
            "External articles are for further learning only. Content and availability are controlled by their providers."
        ),
        "ux.trust.summary": (
            "Data date: {timestamp} · Main source: {provider} · Coverage: {coverage} · Data quality: {quality}"
        ),
        "ux.trust.details": "Data, sources and assumptions",
        "ux.trust.source_line": "**Source:** {provider}  \n**Data date:** {timestamp}",
        "ux.trust.context_line": (
            "**Coverage:** {coverage}  \n**Base currency:** {currency}  \n**Scanner profile:** {profile}"
        ),
        "ux.trust.model_notice": (
            "Scores, scenarios, backtests and AI results are calculated models. They cannot fully capture data gaps, "
            "one-off effects or structural changes."
        ),
        "ux.trust.quality.high": "high",
        "ux.trust.quality.medium": "medium",
        "ux.trust.quality.low": "limited",
        "ux.trust.quality.unknown": "unknown",
        "ux.feedback.title": "Send feedback",
        "ux.feedback.caption": (
            "Your local email application opens with a prepared message to {recipient}. "
            "The message is sent only after you confirm it."
        ),
        "ux.feedback.category": "Category",
        "ux.feedback.category.bug": "Bug",
        "ux.feedback.category.idea": "Improvement idea",
        "ux.feedback.category.question": "Question",
        "ux.feedback.category.data": "Data issue",
        "ux.feedback.message": "Message",
        "ux.feedback.placeholder": "What happened or what should be improved?",
        "ux.feedback.open_email": "Open feedback email",
        "ux.feedback.privacy": (
            "Only app version, current section, language and knowledge mode are added automatically. "
            "Portfolio, document and model data are not attached."
        ),
    },
}


__all__ = ["UX_TRANSLATIONS"]
