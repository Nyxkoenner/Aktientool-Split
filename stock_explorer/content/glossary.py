"""Kuratiertes, zweisprachiges Börsenlexikon für kontextbezogene Hilfen."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class ExternalResource:
    """Kuratiertes externes Lernziel."""

    title_de: str
    title_en: str
    url_de: str
    url_en: str

    def title(self, language: str) -> str:
        return self.title_en if language == "en" else self.title_de

    def url(self, language: str) -> str:
        return self.url_en if language == "en" else self.url_de


@dataclass(frozen=True)
class GlossaryEntry:
    """Ein Lexikoneintrag mit kurzer und ausführlicher Erklärung."""

    key: str
    title_de: str
    title_en: str
    short_de: str
    short_en: str
    explanation_de: str
    explanation_en: str
    why_it_matters_de: str
    why_it_matters_en: str
    limitations_de: str
    limitations_en: str
    resources: tuple[ExternalResource, ...] = ()

    def title(self, language: str) -> str:
        return self.title_en if language == "en" else self.title_de

    def short(self, language: str) -> str:
        return self.short_en if language == "en" else self.short_de

    def explanation(self, language: str) -> str:
        return self.explanation_en if language == "en" else self.explanation_de

    def why_it_matters(self, language: str) -> str:
        return self.why_it_matters_en if language == "en" else self.why_it_matters_de

    def limitations(self, language: str) -> str:
        return self.limitations_en if language == "en" else self.limitations_de


_WIKIPEDIA_KGV = ExternalResource(
    title_de="Wikipedia: Kurs-Gewinn-Verhältnis",
    title_en="Wikipedia: Price–earnings ratio",
    url_de="https://de.wikipedia.org/wiki/Kurs-Gewinn-Verh%C3%A4ltnis",
    url_en="https://en.wikipedia.org/wiki/Price%E2%80%93earnings_ratio",
)
_WIKIPEDIA_FCF = ExternalResource(
    title_de="Wikipedia: Freier Cashflow",
    title_en="Wikipedia: Free cash flow",
    url_de="https://de.wikipedia.org/wiki/Freier_Cashflow",
    url_en="https://en.wikipedia.org/wiki/Free_cash_flow",
)
_WIKIPEDIA_MARGIN = ExternalResource(
    title_de="Wikipedia: Umsatzrentabilität",
    title_en="Wikipedia: Operating margin",
    url_de="https://de.wikipedia.org/wiki/Umsatzrentabilit%C3%A4t",
    url_en="https://en.wikipedia.org/wiki/Operating_margin",
)
_WIKIPEDIA_DIVIDEND_YIELD = ExternalResource(
    title_de="Wikipedia: Dividendenrendite",
    title_en="Wikipedia: Dividend yield",
    url_de="https://de.wikipedia.org/wiki/Dividendenrendite",
    url_en="https://en.wikipedia.org/wiki/Dividend_yield",
)
_WIKIPEDIA_PAYOUT = ExternalResource(
    title_de="Wikipedia: Ausschüttungsquote",
    title_en="Wikipedia: Dividend payout ratio",
    url_de="https://de.wikipedia.org/wiki/Aussch%C3%BCttungsquote",
    url_en="https://en.wikipedia.org/wiki/Dividend_payout_ratio",
)
_WIKIPEDIA_DRAWDOWN = ExternalResource(
    title_de="Wikipedia: Drawdown",
    title_en="Wikipedia: Drawdown",
    url_de="https://de.wikipedia.org/wiki/Drawdown",
    url_en="https://en.wikipedia.org/wiki/Drawdown_(economics)",
)
_WIKIPEDIA_VOLATILITY = ExternalResource(
    title_de="Wikipedia: Volatilität",
    title_en="Wikipedia: Volatility",
    url_de="https://de.wikipedia.org/wiki/Volatilit%C3%A4t",
    url_en="https://en.wikipedia.org/wiki/Volatility_(finance)",
)
_WIKIPEDIA_SHARPE = ExternalResource(
    title_de="Wikipedia: Sharpe-Quotient",
    title_en="Wikipedia: Sharpe ratio",
    url_de="https://de.wikipedia.org/wiki/Sharpe-Quotient",
    url_en="https://en.wikipedia.org/wiki/Sharpe_ratio",
)
_WIKIPEDIA_DIVERSIFICATION = ExternalResource(
    title_de="Wikipedia: Diversifikation",
    title_en="Wikipedia: Diversification",
    url_de="https://de.wikipedia.org/wiki/Diversifikation_(Wirtschaft)",
    url_en="https://en.wikipedia.org/wiki/Diversification_(finance)",
)
_WIKIPEDIA_RL = ExternalResource(
    title_de="Wikipedia: Bestärkendes Lernen",
    title_en="Wikipedia: Reinforcement learning",
    url_de="https://de.wikipedia.org/wiki/Best%C3%A4rkendes_Lernen",
    url_en="https://en.wikipedia.org/wiki/Reinforcement_learning",
)
_WIKIPEDIA_BACKTEST = ExternalResource(
    title_de="Wikipedia: Backtesting",
    title_en="Wikipedia: Backtesting",
    url_de="https://de.wikipedia.org/wiki/Backtesting",
    url_en="https://en.wikipedia.org/wiki/Backtesting",
)


GLOSSARY: Final[dict[str, GlossaryEntry]] = {
    "pe_ratio": GlossaryEntry(
        key="pe_ratio",
        title_de="Kurs-Gewinn-Verhältnis (KGV)",
        title_en="Price–earnings ratio (P/E)",
        short_de="Aktienkurs geteilt durch Gewinn je Aktie.",
        short_en="Share price divided by earnings per share.",
        explanation_de=(
            "Das KGV zeigt, wie viele Geldeinheiten Anleger für eine Geldeinheit aktuellen oder erwarteten "
            "Jahresgewinn bezahlen. Ein niedriger Wert kann günstig wirken, muss aber im Kontext von Wachstum, "
            "Bilanzqualität, Zyklus und Sektor beurteilt werden."
        ),
        explanation_en=(
            "The P/E ratio shows how much investors pay for one unit of current or expected annual earnings. "
            "A low value may look cheap, but it must be assessed together with growth, balance-sheet quality, "
            "the business cycle and the sector."
        ),
        why_it_matters_de="Es ist eine schnelle Orientierung für die Gewinnbewertung einer Aktie.",
        why_it_matters_en="It is a quick orientation for a stock's earnings valuation.",
        limitations_de="Bei Verlusten, Sondereffekten oder stark zyklischen Gewinnen kann das KGV irreführend sein.",
        limitations_en="It can be misleading when earnings are negative, distorted or highly cyclical.",
        resources=(_WIKIPEDIA_KGV,),
    ),
    "free_cash_flow": GlossaryEntry(
        key="free_cash_flow",
        title_de="Free Cashflow",
        title_en="Free cash flow",
        short_de="Zahlungsmittelüberschuss nach notwendigen Investitionen.",
        short_en="Cash generated after necessary capital expenditure.",
        explanation_de=(
            "Der Free Cashflow zeigt vereinfacht, wie viel Zahlungsmittel nach dem laufenden Geschäft und den "
            "Investitionen verbleibt. Er kann für Dividenden, Rückkäufe, Übernahmen oder Schuldenabbau genutzt werden."
        ),
        explanation_en=(
            "Free cash flow approximates the cash left after operations and capital expenditure. It can fund "
            "dividends, buybacks, acquisitions or debt reduction."
        ),
        why_it_matters_de="Dauerhaft positiver Free Cashflow erhöht den finanziellen Handlungsspielraum.",
        why_it_matters_en="Sustained positive free cash flow increases financial flexibility.",
        limitations_de="Investitionszyklen, Leasing und Working Capital können einzelne Jahre stark verzerren.",
        limitations_en="Investment cycles, leases and working capital can distort individual years.",
        resources=(_WIKIPEDIA_FCF,),
    ),
    "operating_margin": GlossaryEntry(
        key="operating_margin",
        title_de="Operative Marge",
        title_en="Operating margin",
        short_de="Operatives Ergebnis im Verhältnis zum Umsatz.",
        short_en="Operating profit as a share of revenue.",
        explanation_de=(
            "Die operative Marge beschreibt, welcher Anteil des Umsatzes nach den operativen Kosten als operatives "
            "Ergebnis verbleibt. Ihre Entwicklung kann auf Preissetzungsmacht oder Kostendruck hinweisen."
        ),
        explanation_en=(
            "Operating margin shows the share of revenue left as operating profit after operating costs. Its trend "
            "can indicate pricing power or cost pressure."
        ),
        why_it_matters_de="Stabile oder steigende Margen sprechen häufig für ein widerstandsfähiges Geschäftsmodell.",
        why_it_matters_en="Stable or rising margins often indicate a resilient business model.",
        limitations_de="Sektoren haben sehr unterschiedliche typische Margen; Sondereffekte sind zu bereinigen.",
        limitations_en="Typical margins vary widely by sector and may require adjustment for one-off items.",
        resources=(_WIKIPEDIA_MARGIN,),
    ),
    "dividend_yield": GlossaryEntry(
        key="dividend_yield",
        title_de="Dividendenrendite",
        title_en="Dividend yield",
        short_de="Jahresdividende im Verhältnis zum Aktienkurs.",
        short_en="Annual dividend relative to the share price.",
        explanation_de=(
            "Die Dividendenrendite setzt die erwartete oder zuletzt gezahlte Jahresdividende ins Verhältnis zum "
            "aktuellen Kurs. Sie ist ein Ertragsbaustein, aber keine Garantie für künftige Ausschüttungen."
        ),
        explanation_en=(
            "Dividend yield compares the expected or most recently paid annual dividend with the current share "
            "price. It is one component of return, not a guarantee of future distributions."
        ),
        why_it_matters_de="Sie hilft, laufende Ausschüttungen zwischen Aktien zu vergleichen.",
        why_it_matters_en="It helps compare current distributions across stocks.",
        limitations_de="Eine sehr hohe Rendite kann durch einen Kurssturz oder eine bevorstehende Kürzung entstehen.",
        limitations_en="A very high yield may result from a price collapse or an imminent dividend cut.",
        resources=(_WIKIPEDIA_DIVIDEND_YIELD,),
    ),
    "payout_ratio": GlossaryEntry(
        key="payout_ratio",
        title_de="Ausschüttungsquote",
        title_en="Payout ratio",
        short_de="Anteil des Gewinns, der als Dividende ausgeschüttet wird.",
        short_en="Share of earnings distributed as dividends.",
        explanation_de=(
            "Die Ausschüttungsquote zeigt, welcher Anteil des Gewinns an Aktionäre fließt. Eine moderate Quote lässt "
            "mehr Puffer für Investitionen, Schuldentilgung und schwächere Geschäftsjahre."
        ),
        explanation_en=(
            "The payout ratio shows the share of earnings distributed to shareholders. A moderate ratio leaves more "
            "room for investment, debt reduction and weaker business years."
        ),
        why_it_matters_de="Sie ist ein wichtiger Hinweis auf die Nachhaltigkeit einer Dividende.",
        why_it_matters_en="It is an important indicator of dividend sustainability.",
        limitations_de="Gewinn und Cashflow können sich unterscheiden; bei REITs gelten häufig andere Kennzahlen.",
        limitations_en="Earnings and cash flow can differ, and REITs often require different measures.",
        resources=(_WIKIPEDIA_PAYOUT,),
    ),
    "drawdown": GlossaryEntry(
        key="drawdown",
        title_de="Drawdown",
        title_en="Drawdown",
        short_de="Rückgang von einem vorherigen Höchststand.",
        short_en="Decline from a previous peak.",
        explanation_de=(
            "Ein Drawdown misst den prozentualen Verlust vom vorherigen Höchststand bis zu einem späteren Tief. Der "
            "maximale Drawdown zeigt den schwersten historischen Einbruch im betrachteten Zeitraum."
        ),
        explanation_en=(
            "A drawdown measures the percentage loss from a previous peak to a later trough. Maximum drawdown is the "
            "largest historical decline within the observed period."
        ),
        why_it_matters_de="Er macht Verlustrisiken greifbarer als Volatilität allein.",
        why_it_matters_en="It makes downside risk more tangible than volatility alone.",
        limitations_de="Ein historischer Drawdown begrenzt mögliche zukünftige Verluste nicht.",
        limitations_en="Historical drawdown does not cap possible future losses.",
        resources=(_WIKIPEDIA_DRAWDOWN,),
    ),
    "volatility": GlossaryEntry(
        key="volatility",
        title_de="Volatilität",
        title_en="Volatility",
        short_de="Stärke der Kursschwankungen in einem Zeitraum.",
        short_en="Magnitude of price fluctuations over a period.",
        explanation_de=(
            "Volatilität misst, wie stark Renditen um ihren Durchschnitt schwanken. Höhere Werte bedeuten größere "
            "historische Ausschläge, unterscheiden aber nicht zwischen positiven und negativen Bewegungen."
        ),
        explanation_en=(
            "Volatility measures how widely returns fluctuate around their average. Higher values mean larger "
            "historical moves, but they do not distinguish between upside and downside movements."
        ),
        why_it_matters_de="Sie wird häufig für Risikoabschätzungen und Portfoliovergleiche verwendet.",
        why_it_matters_en="It is commonly used for risk estimates and portfolio comparisons.",
        limitations_de="Volatilität ist rückblickend und erfasst seltene Extremereignisse nur unvollständig.",
        limitations_en="Volatility is backward-looking and only partly captures rare extreme events.",
        resources=(_WIKIPEDIA_VOLATILITY,),
    ),
    "sharpe_ratio": GlossaryEntry(
        key="sharpe_ratio",
        title_de="Sharpe Ratio",
        title_en="Sharpe ratio",
        short_de="Renditeüberschuss im Verhältnis zur Volatilität.",
        short_en="Excess return relative to volatility.",
        explanation_de=(
            "Die Sharpe Ratio setzt die Rendite oberhalb eines risikofreien Vergleichswerts zur Schwankungsbreite in "
            "Beziehung. Ein höherer Wert steht im Modell für mehr Rendite je Einheit gemessenen Risikos."
        ),
        explanation_en=(
            "The Sharpe ratio relates return above a risk-free reference to volatility. In the model, a higher value "
            "means more return per unit of measured risk."
        ),
        why_it_matters_de="Sie erleichtert den risikobereinigten Vergleich verschiedener Strategien.",
        why_it_matters_en="It helps compare strategies on a risk-adjusted basis.",
        limitations_de="Das Ergebnis hängt stark von Zeitraum, Datenfrequenz und risikofreiem Zinssatz ab.",
        limitations_en="Results depend heavily on period, data frequency and the risk-free rate used.",
        resources=(_WIKIPEDIA_SHARPE,),
    ),
    "diversification": GlossaryEntry(
        key="diversification",
        title_de="Diversifikation",
        title_en="Diversification",
        short_de="Verteilung des Kapitals auf unterschiedliche Risiken.",
        short_en="Spreading capital across different risks.",
        explanation_de=(
            "Diversifikation verteilt Kapital auf mehrere Unternehmen, Branchen, Regionen oder Anlageklassen. Dadurch "
            "kann ein einzelner Ausfall das Gesamtportfolio weniger stark treffen."
        ),
        explanation_en=(
            "Diversification spreads capital across companies, sectors, regions or asset classes so that one failure "
            "has less impact on the total portfolio."
        ),
        why_it_matters_de="Sie reduziert Konzentrationsrisiken, ohne Rendite garantieren zu können.",
        why_it_matters_en="It reduces concentration risk without guaranteeing returns.",
        limitations_de="In Marktkrisen können Korrelationen steigen und Diversifikation zeitweise schwächer wirken.",
        limitations_en="Correlations can rise during crises, reducing diversification benefits temporarily.",
        resources=(_WIKIPEDIA_DIVERSIFICATION,),
    ),
    "q_learning": GlossaryEntry(
        key="q_learning",
        title_de="Q-Learning",
        title_en="Q-learning",
        short_de="Lernverfahren, das Zuständen mögliche Aktionen und erwartete Belohnungen zuordnet.",
        short_en="A learning method mapping states and actions to expected rewards.",
        explanation_de=(
            "Q-Learning ist ein Verfahren des bestärkenden Lernens. Der Agent probiert Aktionen aus und aktualisiert "
            "eine Q-Tabelle anhand nachfolgender Belohnungen. Im Aktien Explorer ist es ein Forschungsexperiment, "
            "kein autonomes Handelssystem."
        ),
        explanation_en=(
            "Q-learning is a reinforcement-learning method. The agent explores actions and updates a Q-table from "
            "subsequent rewards. In Aktien Explorer it is a research experiment, not an autonomous trading system."
        ),
        why_it_matters_de="Es erlaubt den Vergleich einer lernenden Regel mit transparenten Baseline-Strategien.",
        why_it_matters_en="It allows comparison of a learning rule with transparent baseline strategies.",
        limitations_de="Ergebnisse können überangepasst sein und ändern sich mit Daten, Zuständen und Belohnungsfunktion.",
        limitations_en="Results can be overfit and depend on data, state design and reward definition.",
        resources=(_WIKIPEDIA_RL,),
    ),
    "backtesting": GlossaryEntry(
        key="backtesting",
        title_de="Backtesting",
        title_en="Backtesting",
        short_de="Historischer Test einer Regel oder Strategie.",
        short_en="Historical test of a rule or strategy.",
        explanation_de=(
            "Beim Backtesting wird eine zuvor definierte Strategie auf historische Daten angewendet. Saubere Tests "
            "trennen Training und Auswertung und berücksichtigen Kosten sowie Informationszeitpunkte."
        ),
        explanation_en=(
            "Backtesting applies a predefined strategy to historical data. Sound tests separate training and "
            "evaluation and account for costs and information timing."
        ),
        why_it_matters_de="Es zeigt, wie eine Regel unter vergangenen Bedingungen funktioniert hätte.",
        why_it_matters_en="It shows how a rule would have behaved under past conditions.",
        limitations_de="Vergangene Ergebnisse sind keine Prognose; Datenfehler und Rückschaufehler können täuschen.",
        limitations_en="Past results are not forecasts; data issues and look-ahead bias can be misleading.",
        resources=(_WIKIPEDIA_BACKTEST,),
    ),
}


def glossary_entry(key: str) -> GlossaryEntry | None:
    return GLOSSARY.get(str(key).strip())


def search_glossary(query: str, language: str = "de") -> tuple[GlossaryEntry, ...]:
    """Sucht sprachabhängig in Titeln und Kurzbeschreibungen."""
    normalized = str(query or "").strip().casefold()
    entries = sorted(GLOSSARY.values(), key=lambda item: item.title(language).casefold())
    if not normalized:
        return tuple(entries)
    return tuple(
        item
        for item in entries
        if normalized in item.title(language).casefold()
        or normalized in item.short(language).casefold()
        or normalized in item.key.casefold()
    )


__all__ = ["ExternalResource", "GLOSSARY", "GlossaryEntry", "glossary_entry", "search_glossary"]
