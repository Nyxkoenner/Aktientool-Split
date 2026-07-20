from __future__ import annotations

from collections.abc import Mapping
from typing import Final

DEFAULT_LANGUAGE: Final = "de"
SUPPORTED_LANGUAGES: Final[dict[str, str]] = {
    "de": "Deutsch",
    "en": "English",
}

TRANSLATIONS: Final[dict[str, dict[str, str]]] = {
    "de": {
        "app.title": "Aktien Explorer",
        "app.subtitle": (
            "Fundamentaldaten, Score-Profile, News & Events, Portfolio-Risiko und Research. "
            "Keine Anlageberatung – Daten, Quellen und Annahmen vor Entscheidungen immer selbst prüfen."
        ),
        "language.label": "Sprache",
        "language.de": "Deutsch",
        "language.en": "English",
        "common.none": "–",
        "common.no_data": "Keine Daten verfügbar.",
        "common.select_company": "Aktie auswählen",
        "common.company": "Unternehmen",
        "common.ticker": "Ticker",
        "common.source": "Quelle",
        "common.status": "Status",
        "common.message": "Hinweis",
        "common.available": "verfügbar",
        "common.empty": "leer",
        "common.rows": "{count} Zeilen",
        "common.fields": "{count} Felder",
        "common.updated": "Aktualisiert: {timestamp}",
        "common.download_csv": "Als CSV herunterladen",
        "common.yes": "Ja",
        "common.no": "Nein",
        "nav.label": "Bereich auswählen",
        "nav.overview": "Überblick",
        "nav.data_status": "Datenstatus",
        "nav.fundamentals": "Fundamentaldaten",
        "nav.stock_profiles": "Aktienprofile",
        "nav.analysis": "Einzelanalyse",
        "nav.sectors": "Sektoren",
        "nav.news": "News & Events",
        "nav.sources": "Datenquellen",
        "nav.portfolio": "Portfolio",
        "nav.portfolio_sim": "Portfolio-Simulation",
        "nav.scenarios": "Szenarien",
        "nav.watchlist": "Watchlist",
        "nav.value_scanner": "Value-Scanner",
        "nav.deep_value": "Deep Value",
        "nav.backtesting": "Backtesting",
        "nav.patterns": "Mustervergleich",
        "nav.learning": "Lernmodul",
        "nav.company_profiles": "Unternehmensprofile",
        "nav.superinvestors": "Superinvestoren",
        "nav.research": "Research",
        "sidebar.title": "Analyse-Einstellungen",
        "sidebar.provider": "Marktdatenanbieter: {provider}",
        "sidebar.index": "Index",
        "sidebar.index_hint": (
            "DAX, MDAX und SDAX werden offline aus integrierten Listen geladen. "
            "Eigene CSVs unter data/indices/ überschreiben die Vorlage."
        ),
        "sidebar.index_loaded": "{index}: {count} Unternehmen geladen",
        "sidebar.index_source": "Indexquelle: {source}",
        "sidebar.index_error": "Index konnte nicht geladen werden: {error}",
        "sidebar.sector": "Sektor",
        "sidebar.all": "Alle",
        "sidebar.search": "Name oder Ticker suchen",
        "sidebar.no_companies": "Der Filter enthält keine Unternehmen.",
        "sidebar.max_companies": "Max. Unternehmen laden",
        "sidebar.max_companies_help": (
            "Mehr Unternehmen bedeuten deutlich längere Ladezeiten, weil viele Fundamentaldaten einzeln abgefragt werden."
        ),
        "sidebar.scanner_profile": "Scanner-Profil",
        "sidebar.profile": "Profil",
        "sidebar.drawdown": "Min. Drawdown vom 52W-Hoch",
        "sidebar.payout": "Max. Payout Ratio",
        "sidebar.quality": "Min. Qualitäts-Score",
        "sidebar.yield": "Min. Dividendenrendite",
        "sidebar.load": "Daten laden / aktualisieren",
        "sidebar.clear_cache": "Zwischenspeicher leeren",
        "sidebar.cache_cleared": "Zwischenspeicher wurde geleert.",
        "loading.companies": "Lade Daten für {count} Unternehmen …",
        "loading.partial": "Einige Daten konnten nicht vollständig geladen werden: {errors}",
        "loading.prompt": "Wähle links einen Index und klicke auf „Daten laden / aktualisieren“.",
        "status.summary": (
            "Aktualisiert: {timestamp} · {loaded}/{requested} Unternehmen analysiert "
            "({coverage} Abdeckung) · Profil: {profile} · Portfolio-Basiswährung: {currency}"
        ),
        "scenario.title": "Szenario- & Prognose-Engine",
        "scenario.caption": (
            "Berechnet transparente Wenn-dann-Szenarien aus Gewinn, Wachstum, Marge, Bewertung und Dividende. "
            "Die Ergebnisse sind Modellrechnungen und keine Kursziele."
        ),
        "scenario.load_data": "Für die Szenarioanalyse müssen zunächst Marktdaten geladen werden.",
        "scenario.current_price": "aktueller Kurs {price}",
        "scenario.derived_eps": "Abgeleitetes EPS",
        "scenario.current_pe": "Aktuelles KGV",
        "scenario.revenue_growth": "Umsatzwachstum",
        "scenario.dividend_yield": "Dividendenrendite",
        "scenario.horizon": "Szenariohorizont in Jahren",
        "scenario.weak": "Schwach",
        "scenario.base": "Basis",
        "scenario.strong": "Stark",
        "scenario.column.scenario": "Szenario",
        "scenario.column.growth": "Wachstum p.a.",
        "scenario.column.margin": "Margeneffekt",
        "scenario.column.target_pe": "Ziel-KGV",
        "scenario.column.model_price": "Modellpreis",
        "scenario.column.dividends": "Dividenden",
        "scenario.column.total_return": "Gesamtrendite",
        "scenario.chart_return": "Modellhafte Gesamtrendite (%)",
        "scenario.custom": "Eigenes Szenario",
        "scenario.custom_growth": "Umsatz-/Gewinnwachstum p.a.",
        "scenario.custom_margin": "Margenänderung relativ",
        "scenario.custom_pe": "Ziel-KGV",
        "scenario.accumulated_dividends": "Kumulierte Dividenden",
        "scenario.model_total_return": "Modellhafte Gesamtrendite",
        "portfolio_sim.title": "Portfolio-Simulation",
        "portfolio_sim.caption": (
            "Bietet eine historische Transaktionssimulation mit Cash, Dividenden und FX sowie ein separates "
            "Gewichtungsmodell für Buy-and-Hold und Rebalancing."
        ),
        "portfolio_sim.no_holdings": (
            "Für die Simulation werden Bestände aus data/transactions.csv oder portfolio.csv benötigt."
        ),
        "portfolio_sim.no_values": "Für die Bestände fehlen aktuelle Marktwerte.",
        "portfolio_sim.no_history": "Für die Portfolio-Titel fehlen historische Kursreihen.",
        "portfolio_sim.no_match": "Bestände und verfügbare Kursreihen konnten nicht zusammengeführt werden.",
        "portfolio_sim.initial_capital": "Startkapital",
        "portfolio_sim.years": "Historie in Jahren",
        "portfolio_sim.fees": "Handelskosten je Umschichtung (Basispunkte)",
        "portfolio_sim.rebalancing": "Rebalancing",
        "portfolio_sim.none": "Kein Rebalancing",
        "portfolio_sim.monthly": "Monatlich",
        "portfolio_sim.quarterly": "Quartalsweise",
        "portfolio_sim.yearly": "Jährlich",
        "portfolio_sim.buy_hold_value": "Buy & Hold Endwert",
        "portfolio_sim.rebalanced_value": "Rebalancing Endwert",
        "portfolio_sim.max_drawdown": "Max. Drawdown Rebalancing",
        "portfolio_sim.dividends": "Geschätzte Dividenden",
        "portfolio_sim.date": "Datum",
        "portfolio_sim.strategy": "Strategie",
        "portfolio_sim.portfolio_value": "Depotwert",
        "portfolio_sim.buy_hold": "Buy & Hold",
        "portfolio_sim.note": (
            "Modellierte Handelskosten Rebalancing: {costs}. Dividenden werden gleichmäßig über Handelstage verteilt; "
            "reale Zahlungstermine weichen ab."
        ),
        "portfolio_sim.mode": "Simulationsmodus",
        "portfolio_sim.mode_ledger": "Transaktionsbuch 2.0",
        "portfolio_sim.mode_weights": "Gewichtungsmodell",
        "portfolio_sim.weight_model": "Modell aus heutigen Gewichten",
        "portfolio_sim.weight_model_caption": (
            "Vergleicht Buy-and-Hold und Rebalancing anhand der heutigen Portfolio-Gewichte."
        ),
        "portfolio_sim.ledger_model": "Historische Transaktionssimulation",
        "portfolio_sim.ledger_caption": (
            "Verarbeitet Käufe, Verkäufe, Ein- und Auszahlungen, Gebühren, Splits sowie tatsächliche "
            "Dividendendaten. Historische Wechselkurse werden über den konfigurierten FX-Provider geladen."
        ),
        "portfolio_sim.download_template": "Erweiterte Transaktionsvorlage herunterladen",
        "portfolio_sim.ledger_not_configured": "Transaktionspfad oder Datenprovider sind nicht konfiguriert.",
        "portfolio_sim.empty_ledger": "Das Transaktionsbuch ist leer: {path}",
        "portfolio_sim.transaction_preview": "Transaktionsbuch prüfen",
        "portfolio_sim.transaction_types": (
            "Unterstützte Typen: BUY, SELL, DEPOSIT, WITHDRAWAL, DIVIDEND, FEE und SPLIT. "
            "Für Geldbewegungen kann cash_amount verwendet werden."
        ),
        "portfolio_sim.initial_cash": "Anfangsbestand Cash",
        "portfolio_sim.auto_fund": "Käufe automatisch finanzieren",
        "portfolio_sim.auto_fund_help": (
            "Ist nicht genug Cash vorhanden, wird die Differenz als externe Einzahlung verbucht. "
            "So bleiben ältere Transaktionsdateien ohne DEPOSIT-Zeilen nutzbar."
        ),
        "portfolio_sim.actual_dividends": "Historische Dividenden laden",
        "portfolio_sim.reinvest_dividends": "Dividenden reinvestieren",
        "portfolio_sim.dividend_tax": "Modellsteuer auf Dividenden (%)",
        "portfolio_sim.extra_costs": "Zusätzliche Handelskosten (Basispunkte)",
        "portfolio_sim.benchmark": "Benchmark",
        "portfolio_sim.benchmark_none": "Keine Benchmark",
        "portfolio_sim.custom_benchmark": "Eigener Benchmark-Ticker (optional)",
        "portfolio_sim.run_ledger": "Transaktionssimulation starten",
        "portfolio_sim.loading_ledger": "Lade Historien, Dividenden und Wechselkurse …",
        "portfolio_sim.simulation_error": "Simulation fehlgeschlagen: {error}",
        "portfolio_sim.run_prompt": "Starte die Simulation, um Depotkurve und Kennzahlen zu berechnen.",
        "portfolio_sim.final_value": "Endwert",
        "portfolio_sim.net_contributions": "Nettoeinzahlungen",
        "portfolio_sim.twr": "Zeitgewichtete Rendite (TWR)",
        "portfolio_sim.mwr": "Geldgewichtete Rendite (XIRR)",
        "portfolio_sim.final_cash": "Cash am Ende",
        "portfolio_sim.total_fees": "Gebühren",
        "portfolio_sim.taxes": "Modellsteuern",
        "portfolio_sim.actual_portfolio": "Transaktionsdepot",
        "portfolio_sim.cash": "Cash",
        "portfolio_sim.benchmark_summary": (
            "Benchmark {ticker}: Endwert {value} · geldgewichtete Rendite {mwr}"
        ),
        "portfolio_sim.warnings": "Prüfhinweise",
        "portfolio_sim.final_positions": "Endbestände",
        "portfolio_sim.ledger_note": (
            "Die Simulation ist eine Recherchehilfe. Steuerregeln, Brokerabrechnungen, Quellensteuer, "
            "Kapitalmaßnahmen und historische Daten können abweichen und müssen vor Entscheidungen geprüft werden."
        ),
        "sources.title": "Datenquellen & Provider-Monitor",
        "sources.caption": (
            "Prüft die modularen News-, Event- und Profilanbieter unabhängig von der normalen Analyse. "
            "So erkennst du, ob fehlende Informationen von der Quelle, der Firmenzuordnung oder dem Parser kommen."
        ),
        "sources.load_data": "Lade zuerst einen Index beziehungsweise Marktdaten.",
        "sources.check_company": "Unternehmen prüfen",
        "sources.news_language": "News-Sprache",
        "sources.check_news": "Newsquellen prüfen",
        "sources.check_events": "Eventquellen prüfen",
        "sources.check_profiles": "Profilquellen prüfen",
        "sources.last_check": "Letzte Provider-Prüfung: {timestamp}",
        "sources.tab.news": "News",
        "sources.tab.events": "Events",
        "sources.tab.profiles": "Profile",
        "sources.tab.config": "Konfiguration",
        "sources.news_not_checked": "Newsquellen wurden noch nicht geprüft.",
        "sources.events_not_checked": "Eventquellen wurden noch nicht geprüft.",
        "sources.profiles_not_checked": "Profilquellen wurden noch nicht geprüft.",
        "sources.health": "Gesundheit",
        "sources.health.stable": "🟢 stabil",
        "sources.health.limited": "🟡 eingeschränkt",
        "sources.health.critical": "🔴 kritisch",
        "sources.relevant_news": "Relevante Meldungen",
        "sources.ir_path": "IR-Quellen: {path}",
        "sources.manual_path": "Manuelle Events: {path}",
        "sources.sec_hint": "SEC-Abfragen sollten über SEC_CONTACT_EMAIL mit einer Kontaktadresse gekennzeichnet werden.",
        "profile_auto.title": "Automatische Profilanreicherung",
        "profile_auto.caption": (
            "Yahoo-Daten werden bei SEC-gemappten US-Unternehmen durch offizielle SEC Company Facts ergänzt. "
            "Die SEC-Reihe ist eine regulatorische Datenquelle, ersetzt aber keine Prüfung des Geschäftsberichts."
        ),
        "profile_auto.no_sec": (
            "Für diesen Ticker sind keine offiziellen SEC Company Facts verfügbar. "
            "Das ist bei deutschen und vielen anderen Nicht-US-Listings normal."
        ),
        "profile_auto.available": "Offizielle SEC-Finanzreihe verfügbar: {entity} · CIK {cik}",
        "profile_auto.fiscal_year": "Geschäftsjahr",
        "profile_auto.revenue": "Umsatz",
        "profile_auto.net_income": "Nettoergebnis",
        "profile_auto.operating_cashflow": "Operativer Cashflow",
        "profile_auto.capex": "Investitionen",
        "profile_auto.free_cashflow": "Free Cashflow",
        "profile_auto.assets": "Vermögen",
        "profile_auto.liabilities": "Verbindlichkeiten",
        "profile_auto.total_debt": "Finanzschulden",
        "profile_auto.dividends_paid": "Gezahlte Dividenden",
        "profile_auto.download": "Offizielle Finanzreihe als CSV herunterladen",
        "profile_auto.warnings": "Provider-Hinweise",
    },
    "en": {
        "app.title": "Stock Explorer",
        "app.subtitle": (
            "Fundamentals, score profiles, news & events, portfolio risk and research. "
            "Not investment advice – always verify data, sources and assumptions before making decisions."
        ),
        "language.label": "Language",
        "language.de": "Deutsch",
        "language.en": "English",
        "common.none": "–",
        "common.no_data": "No data available.",
        "common.select_company": "Select stock",
        "common.company": "Company",
        "common.ticker": "Ticker",
        "common.source": "Source",
        "common.status": "Status",
        "common.message": "Note",
        "common.available": "available",
        "common.empty": "empty",
        "common.rows": "{count} rows",
        "common.fields": "{count} fields",
        "common.updated": "Updated: {timestamp}",
        "common.download_csv": "Download as CSV",
        "common.yes": "Yes",
        "common.no": "No",
        "nav.label": "Select section",
        "nav.overview": "Overview",
        "nav.data_status": "Data status",
        "nav.fundamentals": "Fundamentals",
        "nav.stock_profiles": "Stock profiles",
        "nav.analysis": "Stock analysis",
        "nav.sectors": "Sectors",
        "nav.news": "News & Events",
        "nav.sources": "Data sources",
        "nav.portfolio": "Portfolio",
        "nav.portfolio_sim": "Portfolio simulation",
        "nav.scenarios": "Scenarios",
        "nav.watchlist": "Watchlist",
        "nav.value_scanner": "Value scanner",
        "nav.deep_value": "Deep value",
        "nav.backtesting": "Backtesting",
        "nav.patterns": "Pattern comparison",
        "nav.learning": "Learning module",
        "nav.company_profiles": "Company profiles",
        "nav.superinvestors": "Superinvestors",
        "nav.research": "Research",
        "sidebar.title": "Analysis settings",
        "sidebar.provider": "Market data provider: {provider}",
        "sidebar.index": "Index",
        "sidebar.index_hint": (
            "DAX, MDAX and SDAX are loaded from integrated offline lists. "
            "Custom CSV files under data/indices/ override the template."
        ),
        "sidebar.index_loaded": "{index}: {count} companies loaded",
        "sidebar.index_source": "Index source: {source}",
        "sidebar.index_error": "Index could not be loaded: {error}",
        "sidebar.sector": "Sector",
        "sidebar.all": "All",
        "sidebar.search": "Search name or ticker",
        "sidebar.no_companies": "The filter contains no companies.",
        "sidebar.max_companies": "Max. companies to load",
        "sidebar.max_companies_help": (
            "Loading more companies takes considerably longer because many fundamentals are requested individually."
        ),
        "sidebar.scanner_profile": "Scanner profile",
        "sidebar.profile": "Profile",
        "sidebar.drawdown": "Min. drawdown from 52-week high",
        "sidebar.payout": "Max. payout ratio",
        "sidebar.quality": "Min. quality score",
        "sidebar.yield": "Min. dividend yield",
        "sidebar.load": "Load / refresh data",
        "sidebar.clear_cache": "Clear cache",
        "sidebar.cache_cleared": "Cache cleared.",
        "loading.companies": "Loading data for {count} companies …",
        "loading.partial": "Some data could not be loaded completely: {errors}",
        "loading.prompt": "Select an index on the left and click “Load / refresh data”.",
        "status.summary": (
            "Updated: {timestamp} · {loaded}/{requested} companies analysed "
            "({coverage} coverage) · Profile: {profile} · Portfolio base currency: {currency}"
        ),
        "scenario.title": "Scenario & Forecast Engine",
        "scenario.caption": (
            "Calculates transparent what-if scenarios from earnings, growth, margins, valuation and dividends. "
            "The results are model calculations, not price targets."
        ),
        "scenario.load_data": "Load market data before running the scenario analysis.",
        "scenario.current_price": "current price {price}",
        "scenario.derived_eps": "Derived EPS",
        "scenario.current_pe": "Current P/E",
        "scenario.revenue_growth": "Revenue growth",
        "scenario.dividend_yield": "Dividend yield",
        "scenario.horizon": "Scenario horizon in years",
        "scenario.weak": "Weak",
        "scenario.base": "Base",
        "scenario.strong": "Strong",
        "scenario.column.scenario": "Scenario",
        "scenario.column.growth": "Annual growth",
        "scenario.column.margin": "Margin effect",
        "scenario.column.target_pe": "Target P/E",
        "scenario.column.model_price": "Model price",
        "scenario.column.dividends": "Dividends",
        "scenario.column.total_return": "Total return",
        "scenario.chart_return": "Modelled total return (%)",
        "scenario.custom": "Custom scenario",
        "scenario.custom_growth": "Annual revenue / earnings growth",
        "scenario.custom_margin": "Relative margin change",
        "scenario.custom_pe": "Target P/E",
        "scenario.accumulated_dividends": "Accumulated dividends",
        "scenario.model_total_return": "Modelled total return",
        "portfolio_sim.title": "Portfolio simulation",
        "portfolio_sim.caption": (
            "Provides a historical transaction simulation with cash, dividends and FX plus a separate "
            "weight model for buy-and-hold and rebalancing."
        ),
        "portfolio_sim.no_holdings": (
            "The simulation requires holdings from data/transactions.csv or portfolio.csv."
        ),
        "portfolio_sim.no_values": "Current market values are missing for the holdings.",
        "portfolio_sim.no_history": "Historical price series are missing for the portfolio holdings.",
        "portfolio_sim.no_match": "Holdings and available price series could not be matched.",
        "portfolio_sim.initial_capital": "Initial capital",
        "portfolio_sim.years": "History in years",
        "portfolio_sim.fees": "Trading costs per rebalance (basis points)",
        "portfolio_sim.rebalancing": "Rebalancing",
        "portfolio_sim.none": "No rebalancing",
        "portfolio_sim.monthly": "Monthly",
        "portfolio_sim.quarterly": "Quarterly",
        "portfolio_sim.yearly": "Yearly",
        "portfolio_sim.buy_hold_value": "Buy & hold final value",
        "portfolio_sim.rebalanced_value": "Rebalanced final value",
        "portfolio_sim.max_drawdown": "Max. rebalanced drawdown",
        "portfolio_sim.dividends": "Estimated dividends",
        "portfolio_sim.date": "Date",
        "portfolio_sim.strategy": "Strategy",
        "portfolio_sim.portfolio_value": "Portfolio value",
        "portfolio_sim.buy_hold": "Buy & hold",
        "portfolio_sim.note": (
            "Modelled rebalancing costs: {costs}. Dividends are spread evenly across trading days; "
            "actual payment dates differ."
        ),
        "portfolio_sim.mode": "Simulation mode",
        "portfolio_sim.mode_ledger": "Transaction ledger 2.0",
        "portfolio_sim.mode_weights": "Weight model",
        "portfolio_sim.weight_model": "Model based on current weights",
        "portfolio_sim.weight_model_caption": (
            "Compares buy-and-hold and rebalancing using the portfolio's current weights."
        ),
        "portfolio_sim.ledger_model": "Historical transaction simulation",
        "portfolio_sim.ledger_caption": (
            "Processes buys, sells, deposits, withdrawals, fees, splits and actual dividend history. "
            "Historical FX rates are loaded through the configured FX provider."
        ),
        "portfolio_sim.download_template": "Download extended transaction template",
        "portfolio_sim.ledger_not_configured": "Transaction path or data providers are not configured.",
        "portfolio_sim.empty_ledger": "The transaction ledger is empty: {path}",
        "portfolio_sim.transaction_preview": "Review transaction ledger",
        "portfolio_sim.transaction_types": (
            "Supported types: BUY, SELL, DEPOSIT, WITHDRAWAL, DIVIDEND, FEE and SPLIT. "
            "Use cash_amount for cash movements."
        ),
        "portfolio_sim.initial_cash": "Initial cash balance",
        "portfolio_sim.auto_fund": "Automatically fund purchases",
        "portfolio_sim.auto_fund_help": (
            "If available cash is insufficient, the difference is recorded as an external contribution. "
            "This keeps older ledgers without DEPOSIT rows usable."
        ),
        "portfolio_sim.actual_dividends": "Load historical dividends",
        "portfolio_sim.reinvest_dividends": "Reinvest dividends",
        "portfolio_sim.dividend_tax": "Modelled dividend tax (%)",
        "portfolio_sim.extra_costs": "Additional trading costs (basis points)",
        "portfolio_sim.benchmark": "Benchmark",
        "portfolio_sim.benchmark_none": "No benchmark",
        "portfolio_sim.custom_benchmark": "Custom benchmark ticker (optional)",
        "portfolio_sim.run_ledger": "Run transaction simulation",
        "portfolio_sim.loading_ledger": "Loading histories, dividends and FX rates …",
        "portfolio_sim.simulation_error": "Simulation failed: {error}",
        "portfolio_sim.run_prompt": "Run the simulation to calculate the equity curve and metrics.",
        "portfolio_sim.final_value": "Final value",
        "portfolio_sim.net_contributions": "Net contributions",
        "portfolio_sim.twr": "Time-weighted return (TWR)",
        "portfolio_sim.mwr": "Money-weighted return (XIRR)",
        "portfolio_sim.final_cash": "Final cash",
        "portfolio_sim.total_fees": "Fees",
        "portfolio_sim.taxes": "Modelled taxes",
        "portfolio_sim.actual_portfolio": "Transaction portfolio",
        "portfolio_sim.cash": "Cash",
        "portfolio_sim.benchmark_summary": (
            "Benchmark {ticker}: final value {value} · money-weighted return {mwr}"
        ),
        "portfolio_sim.warnings": "Review notes",
        "portfolio_sim.final_positions": "Final positions",
        "portfolio_sim.ledger_note": (
            "The simulation is a research aid. Tax rules, broker statements, withholding tax, corporate actions "
            "and historical data may differ and must be verified before decisions."
        ),
        "sources.title": "Data Sources & Provider Monitor",
        "sources.caption": (
            "Checks modular news, event and profile providers independently from the normal analysis. "
            "This helps distinguish source, company-matching and parser issues."
        ),
        "sources.load_data": "Load an index or market data first.",
        "sources.check_company": "Check company",
        "sources.news_language": "News language",
        "sources.check_news": "Check news sources",
        "sources.check_events": "Check event sources",
        "sources.check_profiles": "Check profile sources",
        "sources.last_check": "Last provider check: {timestamp}",
        "sources.tab.news": "News",
        "sources.tab.events": "Events",
        "sources.tab.profiles": "Profiles",
        "sources.tab.config": "Configuration",
        "sources.news_not_checked": "News sources have not been checked yet.",
        "sources.events_not_checked": "Event sources have not been checked yet.",
        "sources.profiles_not_checked": "Profile sources have not been checked yet.",
        "sources.health": "Health",
        "sources.health.stable": "🟢 stable",
        "sources.health.limited": "🟡 limited",
        "sources.health.critical": "🔴 critical",
        "sources.relevant_news": "Relevant articles",
        "sources.ir_path": "IR sources: {path}",
        "sources.manual_path": "Manual events: {path}",
        "sources.sec_hint": "SEC requests should identify a contact address through SEC_CONTACT_EMAIL.",
        "profile_auto.title": "Automated profile enrichment",
        "profile_auto.caption": (
            "For SEC-mapped US companies, Yahoo data is supplemented with official SEC Company Facts. "
            "The SEC series is a regulatory data source and does not replace reviewing the annual report."
        ),
        "profile_auto.no_sec": (
            "No official SEC Company Facts are available for this ticker. "
            "This is normal for German and many other non-US listings."
        ),
        "profile_auto.available": "Official SEC financial series available: {entity} · CIK {cik}",
        "profile_auto.fiscal_year": "Fiscal year",
        "profile_auto.revenue": "Revenue",
        "profile_auto.net_income": "Net income",
        "profile_auto.operating_cashflow": "Operating cash flow",
        "profile_auto.capex": "Capital expenditure",
        "profile_auto.free_cashflow": "Free cash flow",
        "profile_auto.assets": "Assets",
        "profile_auto.liabilities": "Liabilities",
        "profile_auto.total_debt": "Financial debt",
        "profile_auto.dividends_paid": "Dividends paid",
        "profile_auto.download": "Download official financial series as CSV",
        "profile_auto.warnings": "Provider notes",
    },
}


def normalize_language(language: str | None) -> str:
    value = str(language or DEFAULT_LANGUAGE).strip().lower()
    return value if value in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def translate(key: str, language: str | None = None, **values: object) -> str:
    selected = normalize_language(language)
    table: Mapping[str, str] = TRANSLATIONS.get(selected, TRANSLATIONS[DEFAULT_LANGUAGE])
    text = table.get(key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key))
    try:
        return text.format(**values)
    except (KeyError, ValueError):
        return text


def missing_translation_keys() -> dict[str, set[str]]:
    baseline = set(TRANSLATIONS[DEFAULT_LANGUAGE])
    return {
        language: baseline.difference(table)
        for language, table in TRANSLATIONS.items()
        if language != DEFAULT_LANGUAGE
    }
