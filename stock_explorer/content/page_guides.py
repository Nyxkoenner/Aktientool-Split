"""Seitenspezifische Hilfen für unterschiedliche Wissensstufen."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from stock_explorer.domain.ux_preferences import KnowledgeLevel


@dataclass(frozen=True)
class PageGuide:
    page_id: str
    title_de: str
    title_en: str
    beginner_de: str
    beginner_en: str
    intermediate_de: str
    intermediate_en: str
    expert_de: str
    expert_en: str
    steps_de: tuple[str, ...] = ()
    steps_en: tuple[str, ...] = ()
    glossary_keys: tuple[str, ...] = ()

    def title(self, language: str) -> str:
        return self.title_en if language == "en" else self.title_de

    def summary(self, language: str, level: KnowledgeLevel) -> str:
        if language == "en":
            return {
                KnowledgeLevel.BEGINNER: self.beginner_en,
                KnowledgeLevel.INTERMEDIATE: self.intermediate_en,
                KnowledgeLevel.EXPERT: self.expert_en,
            }[level]
        return {
            KnowledgeLevel.BEGINNER: self.beginner_de,
            KnowledgeLevel.INTERMEDIATE: self.intermediate_de,
            KnowledgeLevel.EXPERT: self.expert_de,
        }[level]

    def steps(self, language: str) -> tuple[str, ...]:
        return self.steps_en if language == "en" else self.steps_de


_DEFAULT_GUIDE = PageGuide(
    page_id="default",
    title_de="Orientierung zu diesem Bereich",
    title_en="Guide to this section",
    beginner_de="Beginne mit der Zusammenfassung und öffne Details erst, wenn eine Aussage unklar ist.",
    beginner_en="Start with the summary and open details only when a statement is unclear.",
    intermediate_de="Vergleiche Kennzahlen mit Historie, Sektor und Datenqualität, bevor du Schlüsse ziehst.",
    intermediate_en="Compare metrics with history, sector and data quality before drawing conclusions.",
    expert_de="Prüfe Datenstand, Definitionen, Rohdaten und Modellannahmen vor der Interpretation.",
    expert_en="Inspect data date, definitions, raw data and model assumptions before interpretation.",
)


PAGE_GUIDES: Final[dict[str, PageGuide]] = {
    "overview": PageGuide(
        page_id="overview",
        title_de="So nutzt du den Überblick",
        title_en="How to use the overview",
        beginner_de=(
            "Der Überblick ist dein Startpunkt. Suche zuerst nach auffälligen Qualitäts-, Bewertungs- und "
            "Risikohinweisen und öffne danach nur die relevanten Detailseiten."
        ),
        beginner_en=(
            "The overview is your starting point. Look for notable quality, valuation and risk signals, then open "
            "only the relevant detail pages."
        ),
        intermediate_de="Nutze Scores als Filter, nicht als alleinige Entscheidung. Prüfe die zugrunde liegenden Kennzahlen.",
        intermediate_en="Use scores as filters, not as standalone decisions. Inspect the underlying metrics.",
        expert_de="Kontrolliere Score-Grenzen, Datenabdeckung und mögliche Sektorverzerrungen des Universums.",
        expert_en="Check score thresholds, data coverage and possible sector bias in the universe.",
        steps_de=("Auffällige Unternehmen markieren", "Datenstatus prüfen", "Einzelanalyse öffnen"),
        steps_en=("Mark notable companies", "Check data status", "Open single-stock analysis"),
        glossary_keys=("pe_ratio", "free_cash_flow", "drawdown"),
    ),
    "data_status": PageGuide(
        page_id="data_status",
        title_de="Datenqualität richtig lesen",
        title_en="How to read data quality",
        beginner_de="Fehlende Daten bedeuten nicht automatisch ein schlechtes Unternehmen, sondern geringere Aussagekraft.",
        beginner_en="Missing data does not automatically mean a bad company; it means lower confidence.",
        intermediate_de="Priorisiere aktuelle, vollständig abgedeckte Unternehmen und prüfe Warnungen vor Vergleichen.",
        intermediate_en="Prioritise current, well-covered companies and inspect warnings before comparisons.",
        expert_de="Unterscheide Provider-Ausfälle, strukturell fehlende Felder und echte Nullwerte.",
        expert_en="Distinguish provider failures, structurally unavailable fields and genuine zero values.",
    ),
    "fundamentals": PageGuide(
        page_id="fundamentals",
        title_de="Fundamentaldaten einordnen",
        title_en="Interpreting fundamentals",
        beginner_de="Betrachte nicht nur einen Wert. Wachstum, Marge, Cashflow und Verschuldung sollten zusammenpassen.",
        beginner_en="Do not rely on one number. Growth, margin, cash flow and debt should tell a coherent story.",
        intermediate_de="Vergleiche aktuelle Kennzahlen mit mehreren Jahren Historie und mit Unternehmen desselben Sektors.",
        intermediate_en="Compare current metrics with several years of history and with companies in the same sector.",
        expert_de="Prüfe Definitionen, Bereinigungen, Bilanzierungsunterschiede und Sondereffekte in den Quelldaten.",
        expert_en="Review definitions, adjustments, accounting differences and one-off effects in source data.",
        steps_de=("Geschäftsmodell verstehen", "Margen und Cashflow prüfen", "Bilanzrisiken prüfen"),
        steps_en=("Understand the business model", "Check margins and cash flow", "Check balance-sheet risk"),
        glossary_keys=("free_cash_flow", "operating_margin", "payout_ratio"),
    ),
    "analysis": PageGuide(
        page_id="analysis",
        title_de="Einzelanalyse Schritt für Schritt",
        title_en="Single-stock analysis step by step",
        beginner_de="Beginne mit Geschäftsmodell, Qualität und Risiken. Die Bewertung kommt erst danach.",
        beginner_en="Start with business model, quality and risks. Assess valuation only afterwards.",
        intermediate_de="Verbinde Kursverlauf, Fundamentaldaten und Ereignisse zu einer konsistenten Investmentthese.",
        intermediate_en="Combine price history, fundamentals and events into a coherent investment thesis.",
        expert_de="Teste deine These gegen Gegenargumente, Datenlücken und alternative Bewertungsannahmen.",
        expert_en="Challenge your thesis with counterarguments, data gaps and alternative valuation assumptions.",
        glossary_keys=("drawdown", "volatility", "pe_ratio"),
    ),
    "news": PageGuide(
        page_id="news",
        title_de="News und Ereignisse bewerten",
        title_en="Assessing news and events",
        beginner_de="Trenne den Ton einer Meldung von ihrer möglichen Wirkung auf Geschäft und Aktie.",
        beginner_en="Separate the tone of a headline from its possible impact on the business and the stock.",
        intermediate_de="Bevorzuge offizielle oder mehrfach bestätigte Quellen und prüfe historische Kursreaktionen.",
        intermediate_en="Prefer official or corroborated sources and inspect historical market reactions.",
        expert_de="Achte auf Publikationszeitpunkt, bereits eingepreiste Erwartungen und Quellenabhängigkeiten.",
        expert_en="Consider publication timing, expectations already priced in and source dependencies.",
    ),
    "portfolio": PageGuide(
        page_id="portfolio",
        title_de="Portfolio-Risiken verstehen",
        title_en="Understanding portfolio risk",
        beginner_de="Achte zuerst auf sehr große Einzelpositionen und starke Konzentration in einem Sektor.",
        beginner_en="First look for oversized positions and heavy concentration in a single sector.",
        intermediate_de="Prüfe Gewichtungen, Korrelationen, Währungen und gemeinsame Risikotreiber.",
        intermediate_en="Review weights, correlations, currencies and shared risk drivers.",
        expert_de="Bewerte Konzentration zusätzlich unter Stressszenarien und mit unterschiedlichen Benchmarks.",
        expert_en="Assess concentration under stress scenarios and against different benchmarks.",
        glossary_keys=("diversification", "volatility", "drawdown"),
    ),
    "portfolio_sim": PageGuide(
        page_id="portfolio_sim",
        title_de="Simulationen vorsichtig interpretieren",
        title_en="Interpreting simulations carefully",
        beginner_de="Eine historische Simulation zeigt, was unter vergangenen Bedingungen passiert wäre – nicht die Zukunft.",
        beginner_en="A historical simulation shows what would have happened in the past, not what will happen next.",
        intermediate_de="Berücksichtige Kosten, Dividenden, Wechselkurse, Cashflows und den gewählten Startzeitpunkt.",
        intermediate_en="Consider costs, dividends, FX, cash flows and the selected starting date.",
        expert_de="Prüfe Transaktionslogik, Benchmark, Datenlücken sowie zeit- und geldgewichtete Renditen getrennt.",
        expert_en="Inspect transaction logic, benchmark, data gaps and time- versus money-weighted returns separately.",
        glossary_keys=("diversification", "drawdown", "sharpe_ratio"),
    ),
    "scenarios": PageGuide(
        page_id="scenarios",
        title_de="Szenarien statt Punktprognosen",
        title_en="Scenarios instead of point forecasts",
        beginner_de="Ein Szenario beantwortet eine Wenn-dann-Frage. Es ist kein versprochenes Kursziel.",
        beginner_en="A scenario answers a what-if question. It is not a promised price target.",
        intermediate_de="Teste mindestens ein negatives, ein neutrales und ein positives Annahmenpaket.",
        intermediate_en="Test at least one downside, one neutral and one upside set of assumptions.",
        expert_de="Vergleiche Annahmen mit historischen und sektorspezifischen Bandbreiten und dokumentiere Abhängigkeiten.",
        expert_en="Compare assumptions with historical and sector ranges and document dependencies.",
        glossary_keys=("operating_margin", "pe_ratio", "dividend_yield"),
    ),
    "ai_lab": PageGuide(
        page_id="ai_lab",
        title_de="KI-Labor als Forschung verstehen",
        title_en="Treat the AI lab as research",
        beginner_de="Das KI-Labor liefert keine automatische Kaufempfehlung. Vergleiche den Agenten immer mit einfachen Regeln.",
        beginner_en="The AI lab does not provide an automatic buy recommendation. Always compare the agent with simple rules.",
        intermediate_de="Beurteile nur Out-of-Sample-Ergebnisse und achte auf Kosten, Drawdown und Stabilität über mehrere Folds.",
        intermediate_en="Judge out-of-sample results only and inspect costs, drawdown and stability across folds.",
        expert_de="Prüfe Zustandsdiskretisierung, Belohnungsfunktion, Seeds, Modellversionen und mögliche Überanpassung.",
        expert_en="Inspect state discretisation, reward design, seeds, model versions and possible overfitting.",
        glossary_keys=("q_learning", "backtesting", "sharpe_ratio", "drawdown"),
    ),
    "company_profiles": PageGuide(
        page_id="company_profiles",
        title_de="Geschäftsberichte effizient lesen",
        title_en="Reading company reports efficiently",
        beginner_de="Beginne mit Geschäftsmodell, Segmenten und den wichtigsten Risiken. Prüfe erkannte Inhalte an der Quelle.",
        beginner_en="Start with the business model, segments and key risks. Verify extracted content against the source.",
        intermediate_de="Vergleiche Aussagen über mehrere Berichtsjahre und mit tatsächlicher finanzieller Entwicklung.",
        intermediate_en="Compare statements across reporting years and with actual financial performance.",
        expert_de="Kontrolliere Dokumenttyp, Geschäftsjahr, Währung, Segmentdefinitionen und Extraktionskonfidenz.",
        expert_en="Check document type, fiscal year, currency, segment definitions and extraction confidence.",
    ),
    "backtesting": PageGuide(
        page_id="backtesting",
        title_de="Backtests ohne Rückschaufehler",
        title_en="Backtests without look-ahead bias",
        beginner_de="Gute vergangene Ergebnisse beweisen nicht, dass eine Strategie künftig funktioniert.",
        beginner_en="Strong historical results do not prove that a strategy will work in the future.",
        intermediate_de="Achte auf Kosten, genügend Beobachtungen und getrennte Testzeiträume.",
        intermediate_en="Check costs, sufficient observations and separated test periods.",
        expert_de="Prüfe Survivorship Bias, Point-in-Time-Daten, Parameterstabilität und Mehrfachtests.",
        expert_en="Inspect survivorship bias, point-in-time data, parameter stability and multiple testing.",
        glossary_keys=("backtesting", "sharpe_ratio", "drawdown"),
    ),
    "learning": PageGuide(
        page_id="learning",
        title_de="Lernen und direkt anwenden",
        title_en="Learn and apply immediately",
        beginner_de="Wähle einen Begriff und prüfe ihn anschließend an einem echten Unternehmen im Tool.",
        beginner_en="Choose one concept and then inspect it for a real company in the tool.",
        intermediate_de="Verbinde Kennzahlen mit Geschäftsmodell, Bilanz und Marktumfeld.",
        intermediate_en="Connect metrics with business model, balance sheet and market environment.",
        expert_de="Nutze das Lernmodul als Methodikreferenz und überprüfe Definitionen in den Quelldaten.",
        expert_en="Use the learning module as a methodology reference and verify definitions in source data.",
        glossary_keys=tuple(),
    ),
}


def page_guide(page_id: str) -> PageGuide:
    return PAGE_GUIDES.get(str(page_id).strip(), _DEFAULT_GUIDE)


__all__ = ["PAGE_GUIDES", "PageGuide", "page_guide"]
