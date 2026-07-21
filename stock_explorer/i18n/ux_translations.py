"""Übersetzungen für die UX-Grundlagen ab V7.2.2."""

from __future__ import annotations

from typing import Final

UX_TRANSLATIONS: Final[dict[str, dict[str, str]]] = {
    "de": {
        "ux.nav.main_label": "Hauptbereich auswählen",
        "ux.nav.subpage_label": "Unterbereich",
        "ux.nav.group.start": "Start",
        "ux.nav.group.stocks": "Aktie analysieren",
        "ux.nav.group.portfolio": "Portfolio",
        "ux.nav.group.events": "Watchlist & Ereignisse",
        "ux.nav.group.research": "Research & Werkzeuge",
        "ux.home.title": "Was möchtest du heute untersuchen?",
        "ux.home.intro.beginner": (
            "Wähle einen Arbeitsweg. Das Tool führt dich Schritt für Schritt und erklärt wichtige Begriffe direkt an der passenden Stelle."
        ),
        "ux.home.intro.intermediate": (
            "Starte mit einer Aktienanalyse, prüfe dein Portfolio oder arbeite neue Ereignisse aus deiner Watchlist ab."
        ),
        "ux.home.intro.expert": (
            "Nutze den geführten Einstieg oder wechsle direkt in Research, Backtesting und Modellwerkzeuge."
        ),
        "ux.home.metric.companies": "Geladene Unternehmen",
        "ux.home.metric.sectors": "Abgedeckte Sektoren",
        "ux.home.metric.scored": "Unternehmen mit Score",
        "ux.home.choose_path": "Arbeitsweg auswählen",
        "ux.home.stock.title": "Eine Aktie verstehen",
        "ux.home.stock.description": (
            "Geschäftsmodell, Qualität, Risiken, Ereignisse und Szenarien in einer sinnvollen Reihenfolge prüfen."
        ),
        "ux.home.portfolio.title": "Mein Portfolio prüfen",
        "ux.home.portfolio.description": (
            "Gewichtungen, Konzentrationen, historische Entwicklung und Transaktionen untersuchen."
        ),
        "ux.home.events.title": "Neue Ereignisse bewerten",
        "ux.home.events.description": (
            "Watchlist, Meldungen, Quellenqualität und mögliche Marktreaktionen strukturiert prüfen."
        ),
        "ux.home.open": "Öffnen",
        "ux.home.load_hint": (
            "Lade links ein Aktienuniversum, sobald du Kennzahlen und konkrete Unternehmen analysieren möchtest."
        ),
        "ux.home.beginner_tip": (
            "Empfehlung für den Einstieg: Beginne mit „Eine Aktie verstehen“ und arbeite die fünf Schritte nacheinander ab."
        ),
        "ux.home.expert_tip": (
            "Alle bisherigen Fachseiten bleiben über die fünf Hauptbereiche erreichbar; nur die erste Navigationsebene wurde reduziert."
        ),
        "ux.flow.title": "Geführte Aktienanalyse",
        "ux.flow.intro.beginner": (
            "Wähle ein Unternehmen und bearbeite die fünf Schritte. Markiere einen Schritt erst als abgeschlossen, wenn du die Aussage selbst verstanden und geprüft hast."
        ),
        "ux.flow.intro.intermediate": (
            "Der Analysepfad verbindet qualitative und quantitative Prüfung. Die Reihenfolge hilft, Bewertung nicht vor Geschäftsmodell und Risiko zu stellen."
        ),
        "ux.flow.intro.expert": (
            "Der Pfad dient als reproduzierbare Research-Checkliste. Details, Rohdaten und Modelle bleiben in den jeweiligen Fachseiten verfügbar."
        ),
        "ux.flow.select_company": "Unternehmen für den Analysepfad",
        "ux.flow.metric.company": "Unternehmen",
        "ux.flow.metric.sector": "Sektor",
        "ux.flow.metric.quality": "Qualitäts-Score",
        "ux.flow.metric.value": "Value-Score",
        "ux.flow.progress": "{completed} von {total} Schritten bewusst bestätigt",
        "ux.flow.step.business": "Geschäftsmodell verstehen",
        "ux.flow.step.business.description": (
            "Prüfe Produkte, Segmente, Regionen, Wettbewerbsvorteile und die wichtigsten Abhängigkeiten."
        ),
        "ux.flow.step.quality": "Qualität und Fundamentaldaten prüfen",
        "ux.flow.step.quality.description": (
            "Ordne Wachstum, Margen, Cashflow, Bilanz und Ausschüttungen gemeinsam ein."
        ),
        "ux.flow.step.risk": "Risiken und Kursverhalten untersuchen",
        "ux.flow.step.risk.description": (
            "Prüfe Volatilität, Drawdowns, Verschuldung und mögliche Gegenargumente zur Investmentthese."
        ),
        "ux.flow.step.events": "News und Ereignisse bewerten",
        "ux.flow.step.events.description": (
            "Trenne Nachrichtenton, Geschäftsfolgen und mögliche Aktienwirkung und kontrolliere die Quelle."
        ),
        "ux.flow.step.scenario": "Szenarien durchspielen",
        "ux.flow.step.scenario.description": (
            "Teste mindestens ein schwaches, ein neutrales und ein starkes Annahmenpaket."
        ),
        "ux.flow.open_step": "Schritt öffnen",
        "ux.flow.mark_done": "Diesen Schritt als geprüft markieren",
        "ux.flow.next_recommended": "Nächster empfohlener Schritt: {step}",
        "ux.flow.complete": (
            "Alle fünf Schritte sind bestätigt. Prüfe deine Notizen und dokumentiere auch die stärksten Gegenargumente."
        ),
        "ux.flow.disclaimer": (
            "Die Checkliste dokumentiert deinen Arbeitsfortschritt. Sie ist keine Qualitätszertifizierung und keine Anlageempfehlung."
        ),
        "ux.flow.footer": "Geführter Analysepfad",
        "ux.flow.previous": "Zurück: {step}",
        "ux.flow.next": "Weiter: {step}",
        "ux.flow.back_to_hub": "Zur Analyseübersicht",
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
        "ux.nav.main_label": "Select main section",
        "ux.nav.subpage_label": "Subsection",
        "ux.nav.group.start": "Start",
        "ux.nav.group.stocks": "Analyse a stock",
        "ux.nav.group.portfolio": "Portfolio",
        "ux.nav.group.events": "Watchlist & events",
        "ux.nav.group.research": "Research & tools",
        "ux.home.title": "What would you like to investigate today?",
        "ux.home.intro.beginner": (
            "Choose a workflow. The tool guides you step by step and explains important terms where they are needed."
        ),
        "ux.home.intro.intermediate": (
            "Start a stock analysis, review your portfolio or work through new events from your watchlist."
        ),
        "ux.home.intro.expert": (
            "Use the guided entry point or move directly to research, backtesting and model tools."
        ),
        "ux.home.metric.companies": "Loaded companies",
        "ux.home.metric.sectors": "Covered sectors",
        "ux.home.metric.scored": "Companies with scores",
        "ux.home.choose_path": "Choose a workflow",
        "ux.home.stock.title": "Understand a stock",
        "ux.home.stock.description": (
            "Review the business model, quality, risks, events and scenarios in a sensible order."
        ),
        "ux.home.portfolio.title": "Review my portfolio",
        "ux.home.portfolio.description": (
            "Inspect weights, concentration, historical performance and transactions."
        ),
        "ux.home.events.title": "Assess new events",
        "ux.home.events.description": (
            "Review watchlist items, news, source quality and possible market reactions in a structured way."
        ),
        "ux.home.open": "Open",
        "ux.home.load_hint": (
            "Load a stock universe in the sidebar when you are ready to analyse metrics and specific companies."
        ),
        "ux.home.beginner_tip": (
            "Recommended starting point: choose “Understand a stock” and work through the five steps in order."
        ),
        "ux.home.expert_tip": (
            "All existing specialist pages remain available through the five main sections; only the first navigation level was reduced."
        ),
        "ux.flow.title": "Guided stock analysis",
        "ux.flow.intro.beginner": (
            "Choose a company and complete the five steps. Mark a step complete only after you have understood and checked the conclusion yourself."
        ),
        "ux.flow.intro.intermediate": (
            "The workflow combines qualitative and quantitative review. Its order helps prevent valuation from coming before business model and risk."
        ),
        "ux.flow.intro.expert": (
            "The workflow acts as a reproducible research checklist. Details, raw data and models remain available on the specialist pages."
        ),
        "ux.flow.select_company": "Company for the analysis workflow",
        "ux.flow.metric.company": "Company",
        "ux.flow.metric.sector": "Sector",
        "ux.flow.metric.quality": "Quality score",
        "ux.flow.metric.value": "Value score",
        "ux.flow.progress": "{completed} of {total} steps explicitly confirmed",
        "ux.flow.step.business": "Understand the business model",
        "ux.flow.step.business.description": (
            "Review products, segments, regions, competitive advantages and major dependencies."
        ),
        "ux.flow.step.quality": "Review quality and fundamentals",
        "ux.flow.step.quality.description": (
            "Assess growth, margins, cash flow, balance sheet and distributions together."
        ),
        "ux.flow.step.risk": "Inspect risks and price behaviour",
        "ux.flow.step.risk.description": (
            "Review volatility, drawdowns, debt and possible counterarguments to the investment thesis."
        ),
        "ux.flow.step.events": "Assess news and events",
        "ux.flow.step.events.description": (
            "Separate headline tone, business consequences and possible stock impact, and verify the source."
        ),
        "ux.flow.step.scenario": "Run scenarios",
        "ux.flow.step.scenario.description": (
            "Test at least one downside, one neutral and one upside set of assumptions."
        ),
        "ux.flow.open_step": "Open step",
        "ux.flow.mark_done": "Mark this step as reviewed",
        "ux.flow.next_recommended": "Next suggested step: {step}",
        "ux.flow.complete": (
            "All five steps are confirmed. Review your notes and document the strongest counterarguments as well."
        ),
        "ux.flow.disclaimer": (
            "The checklist records your workflow progress. It is not a quality certification or investment recommendation."
        ),
        "ux.flow.footer": "Guided analysis workflow",
        "ux.flow.previous": "Back: {step}",
        "ux.flow.next": "Next: {step}",
        "ux.flow.back_to_hub": "Back to analysis overview",
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

UX_TRANSLATIONS["de"].update(
    {
        "ux.display.label": "Darstellung",
        "ux.display.help": (
            "Auto passt die Oberfläche per Bildschirmbreite an. Kompakt erzwingt eine schmale, "
            "touchfreundliche Ansicht. Desktop behält die breite Darstellung bei."
        ),
        "ux.display.auto": "Automatisch",
        "ux.display.compact": "Kompakt / Smartphone",
        "ux.display.desktop": "Desktop",
        "ux.display.caption.auto": "Passt Spalten, Navigation und Tabellen automatisch an kleine Bildschirme an.",
        "ux.display.caption.compact": "Einspaltige Navigation, größere Touch-Ziele und gestapelte Karten.",
        "ux.display.caption.desktop": "Breite Tabellen, mehrspaltige Karten und horizontale Hauptnavigation.",
    }
)

UX_TRANSLATIONS["en"].update(
    {
        "ux.display.label": "Display",
        "ux.display.help": (
            "Auto adapts the interface to the screen width. Compact forces a narrow, touch-friendly "
            "layout. Desktop keeps the wide presentation."
        ),
        "ux.display.auto": "Automatic",
        "ux.display.compact": "Compact / smartphone",
        "ux.display.desktop": "Desktop",
        "ux.display.caption.auto": "Automatically adapts columns, navigation and tables on small screens.",
        "ux.display.caption.compact": "Single-column navigation, larger touch targets and stacked cards.",
        "ux.display.caption.desktop": "Wide tables, multi-column cards and horizontal main navigation.",
    }
)

UX_TRANSLATIONS["de"].update(
    {
        "nav.pilot_center": "Pilot & Feedback",
        "ux.feedback.structured": "Strukturiertes Pilot-Feedback öffnen",
        "pilot.banner": (
            "Geschlossener UX-Pilot · Version {version}. Funktionen, Datenqualität und Verständlichkeit "
            "werden noch gemeinsam mit Testnutzern geprüft."
        ),
        "pilot.onboarding.title": "Willkommen im Pilot des Aktien Explorers",
        "pilot.onboarding.intro": (
            "Wähle eine passende Erklärungstiefe und Darstellung. Diese Auswahl verändert nur die Oberfläche, "
            "nicht die Berechnungen."
        ),
        "pilot.onboarding.knowledge": "Wie viel Börsenerfahrung hast du?",
        "pilot.onboarding.display": "Welche Darstellung möchtest du verwenden?",
        "pilot.onboarding.consent": "Anonyme Seitenwechsel für den lokalen Pilot speichern",
        "pilot.onboarding.consent_help": (
            "Gespeichert werden nur eine zufällige Sitzungs-ID, Seiten-ID, App-Version und UI-Einstellungen. "
            "Keine Portfolio-, Dokument-, Modell- oder Freitextdaten."
        ),
        "pilot.onboarding.start": "Pilot starten",
        "pilot.onboarding.skip": "Einführung überspringen",
        "pilot.onboarding.done": "Die Pilot-Einstellungen wurden für diese Sitzung übernommen.",
        "pilot.center.title": "Pilot-Zentrale",
        "pilot.center.intro": (
            "Hier findest du eine kurze Demo, Aufgaben für Testnutzer und ein optionales Feedbackformular, "
            "das eine vorbereitete E-Mail an den Entwickler öffnet."
        ),
        "pilot.center.telemetry": "Anonyme Pilot-Telemetrie für diese Sitzung erlauben",
        "pilot.center.telemetry_help": (
            "Du kannst die Einwilligung jederzeit ausschalten. Bereits lokal gespeicherte Einträge werden dadurch nicht automatisch gelöscht."
        ),
        "pilot.center.telemetry_caption": (
            "Erfasst werden nur Seitenwechsel mit zufälliger Sitzungs-ID und UI-Kontext – keine Portfolio-, Dokument- oder Freitextdaten."
        ),
        "pilot.center.tab.demo": "Demo",
        "pilot.center.tab.tasks": "Testaufgaben",
        "pilot.center.tab.feedback": "Feedback",
        "pilot.center.tab.admin": "Pilot-Auswertung",
        "pilot.demo.title": "Beispielanalyse in zwei Minuten",
        "pilot.demo.fictional": "Fiktive Beispieldaten – keine reale Aktie und keine Anlageempfehlung.",
        "pilot.demo.company": "Muster Industrie AG",
        "pilot.demo.quality": "Qualität",
        "pilot.demo.pe": "KGV",
        "pilot.demo.drawdown": "Abstand zum Hoch",
        "pilot.demo.scenario": "Negativszenario",
        "pilot.demo.interpretation": (
            "**Einordnung:** Die Musterfirma wirkt qualitativ solide und nicht extrem bewertet. Der Kurs liegt "
            "unter seinem Hoch; ein negatives Szenario zeigt trotzdem ein spürbares Verlustrisiko. Eine "
            "Entscheidung braucht zusätzlich Geschäftsmodell, Bilanz, Risiken und Quellenprüfung."
        ),
        "pilot.demo.warning": (
            "Ein Score, ein KGV oder ein KI-Ergebnis reicht nie allein aus. Achte auf Datenstand, Annahmen und "
            "Gegenargumente."
        ),
        "pilot.demo.real_analysis": "Mit echten Marktdaten zur geführten Analyse",
        "pilot.demo.load_data": (
            "Lade links zuerst einen kleinen Indexausschnitt. Danach kannst du von hier direkt in die geführte "
            "Analyse wechseln."
        ),
        "pilot.tasks.title": "Aufgaben für den UX-Pilot",
        "pilot.tasks.intro": (
            "Bearbeite die Aufgaben möglichst ohne zusätzliche Hilfe. Markiere nur, was du wirklich abgeschlossen hast."
        ),
        "pilot.tasks.choose_company": "Eine bisher wenig bekannte Aktie auswählen",
        "pilot.tasks.understand_business": "Geschäftsmodell und wichtigste Umsatztreiber erklären",
        "pilot.tasks.review_risks": "Mindestens drei Risiken oder Gegenargumente finden",
        "pilot.tasks.run_scenario": "Ein negatives und ein neutrales Szenario durchspielen",
        "pilot.tasks.use_watchlist": "Watchlist oder Portfolio-Bereich öffnen und verstehen",
        "pilot.tasks.send_feedback": "Mindestens ein konkretes Feedback vorbereiten oder per E-Mail senden",
        "pilot.tasks.progress": "{completed} von {total} Pilotaufgaben abgeschlossen",
        "pilot.tasks.complete": "Danke – alle Pilotaufgaben wurden in dieser Sitzung abgeschlossen.",
        "pilot.feedback.title": "Strukturiertes Pilot-Feedback",
        "pilot.feedback.intro": (
            "Deine Eingaben werden nicht lokal gespeichert und nicht automatisch versendet. Du kannst daraus "
            "optional eine vorbereitete E-Mail an nykoenner@gmail.com öffnen."
        ),
        "pilot.feedback.category": "Kategorie",
        "pilot.feedback.category.bug": "Fehler",
        "pilot.feedback.category.idea": "Verbesserungsidee",
        "pilot.feedback.category.question": "Verständnisfrage",
        "pilot.feedback.category.data": "Datenproblem",
        "pilot.feedback.category.usability": "Bedienung / Nutzerfreundlichkeit",
        "pilot.feedback.rating": "Wie hilfreich war die aktuelle Erfahrung?",
        "pilot.feedback.message": "Dein Feedback",
        "pilot.feedback.placeholder": "Was war unklar, langsam, hilfreich oder fehlerhaft?",
        "pilot.feedback.email": "Kontakt-E-Mail im Nachrichtentext (optional)",
        "pilot.feedback.storage_consent": "Nicht verwendet",
        "pilot.feedback.save": "E-Mail vorbereiten",
        "pilot.feedback.consent_required": "Nicht verwendet",
        "pilot.feedback.saved": "Die E-Mail wurde vorbereitet.",
        "pilot.feedback.email_copy": "E-Mail öffnen",
        "pilot.feedback.prepare_email": "E-Mail vorbereiten",
        "pilot.feedback.message_required": "Bitte gib mindestens drei Zeichen Feedback ein.",
        "pilot.feedback.prepared": "Die E-Mail wurde vorbereitet. Sie wird erst nach deinem Klick im E-Mail-Programm versendet.",
        "pilot.feedback.open_email": "E-Mail an nykoenner@gmail.com öffnen",
        "pilot.feedback.email_optional": "Optional: Öffne die vorbereitete E-Mail an {recipient}. Ohne diesen Klick wird nichts übermittelt.",
        "pilot.feedback.privacy": (
            "Es wird nichts automatisch gespeichert oder versendet. Beim Öffnen der E-Mail werden nur die sichtbaren "
            "Feedbackangaben sowie App-Version, Bereich, Sprache und Wissensmodus eingefügt."
        ),
        "pilot.admin.title": "Lokale Pilot-Auswertung",
        "pilot.admin.not_configured": (
            "Für die Auswertung ist noch kein lokaler Admin-PIN konfiguriert. Setze vor dem App-Start die "
            "Umgebungsvariable PILOT_ADMIN_PIN oder den Secret-Wert pilot_admin_pin."
        ),
        "pilot.admin.pin": "Admin-PIN",
        "pilot.admin.unlock": "Auswertung entsperren",
        "pilot.admin.wrong_pin": "Der PIN ist nicht korrekt.",
        "pilot.admin.feedback_count": "Feedbacks",
        "pilot.admin.event_count": "Seitenereignisse",
        "pilot.admin.rating": "Ø Bewertung",
        "pilot.admin.download": "Feedback als CSV herunterladen",
        "pilot.admin.no_feedback": "Noch kein strukturiertes Feedback gespeichert.",
        "pilot.admin.page": "Bereich",
        "pilot.admin.views": "Aufrufe",
    }
)

UX_TRANSLATIONS["en"].update(
    {
        "nav.pilot_center": "Pilot & feedback",
        "ux.feedback.structured": "Open structured pilot feedback",
        "pilot.banner": (
            "Closed UX pilot · Version {version}. Features, data quality and clarity are still being evaluated "
            "with test users."
        ),
        "pilot.onboarding.title": "Welcome to the Aktien Explorer pilot",
        "pilot.onboarding.intro": (
            "Choose a suitable explanation depth and display mode. This changes the interface only, not the calculations."
        ),
        "pilot.onboarding.knowledge": "How much investing experience do you have?",
        "pilot.onboarding.display": "Which display mode would you like to use?",
        "pilot.onboarding.consent": "Store anonymous page changes for the local pilot",
        "pilot.onboarding.consent_help": (
            "Only a random session ID, page ID, app version and interface settings are stored. No portfolio, "
            "document, model or free-text data."
        ),
        "pilot.onboarding.start": "Start pilot",
        "pilot.onboarding.skip": "Skip introduction",
        "pilot.onboarding.done": "The pilot settings have been applied for this session.",
        "pilot.center.title": "Pilot centre",
        "pilot.center.intro": (
            "This area contains a short demo, tester tasks and optional feedback that opens a prepared email to the developer."
        ),
        "pilot.center.telemetry": "Allow anonymous pilot telemetry for this session",
        "pilot.center.telemetry_help": (
            "You can revoke consent at any time. Previously stored local entries are not deleted automatically."
        ),
        "pilot.center.telemetry_caption": (
            "Only page changes with a random session ID and interface context are recorded – no portfolio, document or free-text data."
        ),
        "pilot.center.tab.demo": "Demo",
        "pilot.center.tab.tasks": "Test tasks",
        "pilot.center.tab.feedback": "Feedback",
        "pilot.center.tab.admin": "Pilot summary",
        "pilot.demo.title": "Two-minute example analysis",
        "pilot.demo.fictional": "Fictional example data – not a real stock and not investment advice.",
        "pilot.demo.company": "Sample Industries plc",
        "pilot.demo.quality": "Quality",
        "pilot.demo.pe": "P/E",
        "pilot.demo.drawdown": "Below high",
        "pilot.demo.scenario": "Downside scenario",
        "pilot.demo.interpretation": (
            "**Interpretation:** The sample company appears reasonably solid and not extremely valued. The share "
            "price is below its high, while the downside scenario still shows meaningful loss potential. A decision "
            "also requires a review of the business, balance sheet, risks and sources."
        ),
        "pilot.demo.warning": (
            "A score, P/E ratio or AI result is never sufficient on its own. Check data dates, assumptions and counterarguments."
        ),
        "pilot.demo.real_analysis": "Continue to guided analysis with real market data",
        "pilot.demo.load_data": (
            "Load a small index sample in the sidebar first. You can then continue directly to the guided analysis."
        ),
        "pilot.tasks.title": "UX pilot tasks",
        "pilot.tasks.intro": (
            "Complete these tasks without additional help where possible. Mark only tasks you actually completed."
        ),
        "pilot.tasks.choose_company": "Choose a stock you do not already know well",
        "pilot.tasks.understand_business": "Explain the business model and main revenue drivers",
        "pilot.tasks.review_risks": "Find at least three risks or counterarguments",
        "pilot.tasks.run_scenario": "Run one downside and one neutral scenario",
        "pilot.tasks.use_watchlist": "Open and understand the watchlist or portfolio area",
        "pilot.tasks.send_feedback": "Prepare or email at least one specific piece of feedback",
        "pilot.tasks.progress": "{completed} of {total} pilot tasks completed",
        "pilot.tasks.complete": "Thank you – all pilot tasks were completed in this session.",
        "pilot.feedback.title": "Structured pilot feedback",
        "pilot.feedback.intro": (
            "Your input is not stored locally or sent automatically. You can optionally open a prepared email to "
            "nykoenner@gmail.com."
        ),
        "pilot.feedback.category": "Category",
        "pilot.feedback.category.bug": "Bug",
        "pilot.feedback.category.idea": "Improvement idea",
        "pilot.feedback.category.question": "Question",
        "pilot.feedback.category.data": "Data issue",
        "pilot.feedback.category.usability": "Usability",
        "pilot.feedback.rating": "How helpful was the current experience?",
        "pilot.feedback.message": "Your feedback",
        "pilot.feedback.placeholder": "What was unclear, slow, helpful or broken?",
        "pilot.feedback.email": "Contact email in message (optional)",
        "pilot.feedback.storage_consent": "Not used",
        "pilot.feedback.save": "Prepare email",
        "pilot.feedback.consent_required": "Not used",
        "pilot.feedback.saved": "The email has been prepared.",
        "pilot.feedback.email_copy": "Open email",
        "pilot.feedback.prepare_email": "Prepare email",
        "pilot.feedback.message_required": "Please enter at least three characters of feedback.",
        "pilot.feedback.prepared": "The email has been prepared. It is sent only after you confirm it in your email client.",
        "pilot.feedback.open_email": "Open email to nykoenner@gmail.com",
        "pilot.feedback.email_optional": "Optional: open the prepared email to {recipient}. Nothing is transmitted without this click.",
        "pilot.feedback.privacy": (
            "Nothing is stored or sent automatically. Opening the email inserts only the visible feedback fields plus "
            "app version, section, language and knowledge mode."
        ),
        "pilot.admin.title": "Local pilot summary",
        "pilot.admin.not_configured": (
            "No local admin PIN is configured. Set the PILOT_ADMIN_PIN environment variable or the "
            "pilot_admin_pin secret before starting the app."
        ),
        "pilot.admin.pin": "Admin PIN",
        "pilot.admin.unlock": "Unlock summary",
        "pilot.admin.wrong_pin": "The PIN is incorrect.",
        "pilot.admin.feedback_count": "Feedback items",
        "pilot.admin.event_count": "Page events",
        "pilot.admin.rating": "Average rating",
        "pilot.admin.download": "Download feedback as CSV",
        "pilot.admin.no_feedback": "No structured feedback has been stored yet.",
        "pilot.admin.page": "Section",
        "pilot.admin.views": "Views",
    }
)
