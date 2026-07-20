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
        "scenario.caption_v2": (
            "Berechnet sektorspezifische Stress- und Prognoseszenarien aus Gewinn, Wachstum, Marge, "
            "Finanzierung, Bewertung, Dividende und Währung. Die Ergebnisse sind transparente "
            "Modellrechnungen und keine Kursziele."
        ),
        "scenario.operating_margin": "Operative Marge",
        "scenario.net_debt": "Net Debt / EBITDA",
        "scenario.preset": "Szenario auswählen",
        "scenario.preset.base": "Basisszenario",
        "scenario.preset.recession": "Rezession",
        "scenario.preset.rate_hike": "Zinsanstieg",
        "scenario.preset.inflation": "Inflation & Rohstoffschock",
        "scenario.preset.margin_pressure": "Margendruck",
        "scenario.preset.dividend_cut": "Dividendenkürzung",
        "scenario.preset.deleveraging": "Schuldenabbau",
        "scenario.preset.valuation_normalization": "Bewertungsnormalisierung",
        "scenario.preset.currency_shock": "Währungsschock",
        "scenario.preset.custom": "Eigenes Szenario",
        "scenario.sector_model": "Verwendetes Sektormodell: {model}",
        "scenario.sector.bank": "Banken",
        "scenario.sector.insurance": "Versicherungen",
        "scenario.sector.real_estate": "Immobilien / REITs",
        "scenario.sector.technology": "Technologie / Software",
        "scenario.sector.industrial": "Industrie",
        "scenario.sector.utility": "Versorger",
        "scenario.sector.energy": "Energie",
        "scenario.sector.consumer": "Konsum",
        "scenario.sector.healthcare": "Gesundheit",
        "scenario.sector.generic": "Allgemeines Unternehmensmodell",
        "scenario.band_help": "Schwache und starke Bandbreite variieren Wachstum, Marge, Bewertung, Dividende und Ertragseffekte um konservative Stresswerte.",
        "scenario.price_and_dividends": "Modellpreis {price} · Dividenden {dividends}",
        "scenario.details": "Annahmen, Treiber und Risiken",
        "scenario.assumption": "Annahme",
        "scenario.value": "Veränderung",
        "scenario.unit": "Einheit",
        "scenario.assumptions": "Zentrale Annahmen",
        "scenario.risks": "Wichtigste Risiken",
        "scenario.assumption.growth_delta": "Änderung Wachstum p.a.",
        "scenario.assumption.margin_delta": "Relativer Margeneffekt",
        "scenario.assumption.valuation_delta": "Änderung Bewertungsmultiple",
        "scenario.assumption.dividend_delta": "Änderung Dividende",
        "scenario.assumption.financing_delta": "Ertragseffekt Finanzierung",
        "scenario.assumption.sector_delta": "Sektorspezifischer Ertragseffekt",
        "scenario.assumption.fx_delta": "Währungseffekt auf Ertrag",
        "scenario.custom_hint": "Die Werte verändern das heutige quantitative Ausgangsbild. Positive Werte verbessern, negative Werte belasten das Modell.",
        "scenario.custom_growth_delta": "Änderung Wachstum p.a. (Prozentpunkte)",
        "scenario.custom_valuation": "Änderung Bewertungsmultiple (%)",
        "scenario.custom_dividend": "Änderung Dividende (%)",
        "scenario.custom_financing": "Ertragseffekt Finanzierung (%)",
        "scenario.custom_sector": "Sektorspezifischer Ertragseffekt (%)",
        "scenario.custom_fx": "Währungseffekt auf Ertrag (%)",
        "scenario.calibration.title": "Historische Plausibilitätsprüfung",
        "scenario.calibration.caption": "Vergleicht die modellhafte Gesamtrendite mit rollierenden historischen Haltedauerrenditen derselben Aktie. Fundamentale Annahmen werden zusätzlich gegen typische Sektorbandbreiten geprüft.",
        "scenario.calibration.samples": "Historische Beobachtungen",
        "scenario.calibration.weak": "Historisch schwach · 20 %",
        "scenario.calibration.median": "Historischer Median",
        "scenario.calibration.strong": "Historisch stark · 80 %",
        "scenario.calibration.volatility": "Volatilität p.a.",
        "scenario.calibration.drawdown": "Max. Drawdown",
        "scenario.calibration.insufficient": "Nur {count} historische Beobachtungen für diesen Horizont. Die historische Einordnung ist nicht belastbar.",
        "scenario.projection.insufficient": "Für eine belastbare historische Einordnung fehlen ausreichend lange Kursdaten.",
        "scenario.projection.below": "Die Modellrendite liegt unter dem historischen 20%-Bereich und bildet ein außergewöhnlich schwaches Ergebnis ab.",
        "scenario.projection.within": "Die Modellrendite liegt innerhalb der historischen 20%- bis 80%-Bandbreite.",
        "scenario.projection.above": "Die Modellrendite liegt oberhalb des historischen 80%-Bereichs und setzt ein außergewöhnlich starkes Ergebnis voraus.",
        "scenario.growth_assessment.very_weak": "Die angenommene jährliche Entwicklung ist schwächer als die typische Stressbandbreite dieses Sektormodells.",
        "scenario.growth_assessment.plausible": "Die angenommene jährliche Entwicklung liegt innerhalb der verwendeten Sektorbandbreite.",
        "scenario.growth_assessment.very_strong": "Die angenommene jährliche Entwicklung liegt über der typischen starken Sektorbandbreite.",
        "scenario.disclaimer": "Szenarien sind keine Prognosen oder Kursziele. Historische Kursbandbreiten, heutige Kennzahlen und vereinfachte Sektormodelle können strukturelle Veränderungen, Sondereffekte und Datenfehler nicht vollständig abbilden.",
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
        "report.title": "Geschäftsberichte automatisch analysieren",
        "report.caption": (
            "Importiert PDF-, HTML- oder Textberichte, erkennt Geschäftsmodell, Risiken, Chancen, "
            "Abhängigkeiten sowie mögliche Segment- und Regionsdaten. Alle Ergebnisse sind heuristische "
            "Recherchehilfen und müssen am Originalbericht geprüft werden."
        ),
        "report.tab.upload": "Bericht hochladen",
        "report.tab.official": "Offiziellen Bericht laden",
        "report.upload": "Geschäftsbericht auswählen",
        "report.upload_help": "Unterstützt textbasierte PDF-, TXT- und HTML-Dateien. Gescannte PDFs benötigen vorher OCR.",
        "report.analyze_upload": "Bericht analysieren",
        "report.official_hint": "Für {company} ({ticker}) wird der neueste SEC-Jahresbericht gesucht. Das funktioniert nur bei SEC-gemappten US-Tickern und ADRs.",
        "report.load_official": "Neuesten SEC-Jahresbericht laden",
        "report.loading": "Offiziellen Bericht laden und analysieren …",
        "report.loaded": "Bericht über {source} geladen.",
        "report.content_type": "Dateityp",
        "report.duration": "Dauer ms",
        "report.metric.year": "Geschäftsjahr",
        "report.metric.type": "Berichtstyp",
        "report.metric.pages": "Seiten",
        "report.metric.characters": "Textzeichen",
        "report.metric.coverage": "Extraktionsabdeckung",
        "report.summary": "Automatisch erkannte Zusammenfassung",
        "report.tab.overview": "Überblick",
        "report.tab.findings": "Erkannte Themen",
        "report.tab.candidates": "Segmente & Regionen prüfen",
        "report.tab.text": "Quelltext",
        "report.tab.risks": "Risiken",
        "report.tab.opportunities": "Chancen",
        "report.tab.dependencies": "Abhängigkeiten",
        "report.tab.sections": "Erkannte Abschnitte",
        "report.tab.segments": "Segmentkandidaten",
        "report.tab.regions": "Regionskandidaten",
        "report.column.category": "Kategorie",
        "report.column.confidence": "Konfidenz",
        "report.column.evidence": "Fundstelle / Textbeleg",
        "report.column.include": "Übernehmen",
        "report.column.segment": "Segment",
        "report.column.region": "Region",
        "report.column.revenue": "Umsatz",
        "report.column.share": "Umsatzanteil %",
        "report.no_candidates": "Keine strukturierten Kandidaten erkannt.",
        "report.review_hint": "Prüfe jede Zeile am Originalbericht. Nur markierte Zeilen werden in die lokalen Profildateien übernommen.",
        "report.save_segments": "Markierte Segmente speichern",
        "report.save_regions": "Markierte Regionen speichern",
        "report.saved_rows": "{count} Zeile(n) gespeichert.",
        "report.brands": "Mögliche Marken und Tochtergesellschaften",
        "report.source_document": "Analysiertes Dokument: {filename}",
        "report.open_source": "Originalquelle öffnen",
        "report.search_text": "Im extrahierten Text suchen",
        "report.search_empty": "Keine passende Textstelle gefunden.",
        "report.extracted_text": "Extrahierter Berichtstext",
        "report.download_text": "Extrahierten Text herunterladen",
        "report.save_snapshot": "Analyse-Snapshot speichern",
        "report.snapshot_saved": "Snapshot gespeichert: {path}",
        "report.transfer_profile": "Erkenntnisse ins Unternehmensprofil übernehmen",
        "report.profile_updated": "Qualitatives Unternehmensprofil wurde ergänzt.",
        "report.snapshots": "Gespeicherte Berichtsanalysen",
        "report.no_snapshots": "Noch keine Analyse-Snapshots für diesen Ticker gespeichert.",
        "report.snapshot_select": "Gespeicherte Analyse auswählen",
        "report.snapshot_load": "Gespeicherte Analyse laden",
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
        "news_v2.title": "News- und Ereignisanalyse 2.0",
        "news_v2.caption": (
            "Führt Mehrfachmeldungen zusammen, trennt Nachrichtenton und mögliche Aktienwirkung und misst "
            "historische Kursreaktionen gegenüber {benchmark}."
        ),
        "news_v2.no_events": "Im aktuellen Zeitraum wurden keine ausreichend relevanten Ereigniscluster erkannt.",
        "news_v2.metric.clusters": "Ereigniscluster",
        "news_v2.metric.official": "Hohes Quellenvertrauen",
        "news_v2.metric.negative": "Negative Aktienwirkung",
        "news_v2.metric.reactions": "Mit Kursreaktion",
        "news_v2.filter.event": "Ereignistyp",
        "news_v2.filter.impact": "Mögliche Aktienwirkung",
        "news_v2.filter.trust": "Min. Quellenvertrauen",
        "news_v2.filter.multi": "Nur mehrere Quellen",
        "news_v2.column.event": "Ereignis",
        "news_v2.column.title": "Titel",
        "news_v2.column.tone": "Nachrichtenton",
        "news_v2.column.impact": "Aktienwirkung",
        "news_v2.column.trust": "Quellenvertrauen",
        "news_v2.column.sources": "Quellen",
        "news_v2.column.excess20": "Überrendite 20T",
        "news_v2.filtered_empty": "Kein Ereignis erfüllt die aktuellen Filter.",
        "news_v2.detail.select": "Ereignis für Detailansicht",
        "news_v2.primary_source": "Primärquelle",
        "news_v2.sources_detail": "Zusammengeführte Quellen",
        "news_v2.open_source": "Quelle öffnen",
        "news_v2.source_summary": "Quellenübersicht",
        "news_v2.fulltext.load": "Textauszug der Primärquelle abrufen",
        "news_v2.fulltext.loading": "Textauszug wird geladen …",
        "news_v2.fulltext.chars": "Extrahierte Zeichen",
        "news_v2.fulltext.excerpt": "Begrenzter Textauszug",
        "news_v2.fulltext.notice": (
            "Der Text wird nur auf Nutzeraktion abgerufen und nicht vollständig in der Ereignisdatenbank gespeichert. "
            "Paywalls, Nutzungsbedingungen und Quellenrechte bleiben zu beachten."
        ),
        "news_v2.database.save": "Analyse in lokaler Ereignisdatenbank speichern",
        "news_v2.database.saved": "Gespeichert: {events} Ereignisse und {articles} Quellenmeldungen.",
        "news_v2.database.status": (
            "Lokale Ereignisdatenbank: zuletzt {timestamp} · {events} Ereignisse · {articles} Quellenmeldungen"
        ),
        "news_v2.disclaimer": (
            "Ton, Aktienwirkung und Quellenvertrauen sind heuristische Recherchehilfen. Kursreaktionen zeigen "
            "historische Marktbewegungen und keine Kausalität oder Prognose."
        ),
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
        "scenario.caption_v2": (
            "Calculates sector-specific stress and forecast scenarios from earnings, growth, margins, "
            "financing, valuation, dividends and currencies. Results are transparent model calculations, "
            "not price targets."
        ),
        "scenario.operating_margin": "Operating margin",
        "scenario.net_debt": "Net debt / EBITDA",
        "scenario.preset": "Select scenario",
        "scenario.preset.base": "Base scenario",
        "scenario.preset.recession": "Recession",
        "scenario.preset.rate_hike": "Interest-rate increase",
        "scenario.preset.inflation": "Inflation & commodity shock",
        "scenario.preset.margin_pressure": "Margin pressure",
        "scenario.preset.dividend_cut": "Dividend cut",
        "scenario.preset.deleveraging": "Deleveraging",
        "scenario.preset.valuation_normalization": "Valuation normalization",
        "scenario.preset.currency_shock": "Currency shock",
        "scenario.preset.custom": "Custom scenario",
        "scenario.sector_model": "Sector model used: {model}",
        "scenario.sector.bank": "Banks",
        "scenario.sector.insurance": "Insurance",
        "scenario.sector.real_estate": "Real estate / REITs",
        "scenario.sector.technology": "Technology / software",
        "scenario.sector.industrial": "Industrials",
        "scenario.sector.utility": "Utilities",
        "scenario.sector.energy": "Energy",
        "scenario.sector.consumer": "Consumer",
        "scenario.sector.healthcare": "Healthcare",
        "scenario.sector.generic": "Generic company model",
        "scenario.band_help": "Weak and strong bands vary growth, margins, valuation, dividends and earnings effects using conservative stress adjustments.",
        "scenario.price_and_dividends": "Model price {price} · dividends {dividends}",
        "scenario.details": "Assumptions, drivers and risks",
        "scenario.assumption": "Assumption",
        "scenario.value": "Change",
        "scenario.unit": "Unit",
        "scenario.assumptions": "Key assumptions",
        "scenario.risks": "Main risks",
        "scenario.assumption.growth_delta": "Annual growth change",
        "scenario.assumption.margin_delta": "Relative margin effect",
        "scenario.assumption.valuation_delta": "Valuation multiple change",
        "scenario.assumption.dividend_delta": "Dividend change",
        "scenario.assumption.financing_delta": "Financing earnings effect",
        "scenario.assumption.sector_delta": "Sector-specific earnings effect",
        "scenario.assumption.fx_delta": "FX earnings effect",
        "scenario.custom_hint": "Inputs alter today's quantitative starting point. Positive values improve and negative values weaken the model.",
        "scenario.custom_growth_delta": "Annual growth change (percentage points)",
        "scenario.custom_valuation": "Valuation multiple change (%)",
        "scenario.custom_dividend": "Dividend change (%)",
        "scenario.custom_financing": "Financing earnings effect (%)",
        "scenario.custom_sector": "Sector-specific earnings effect (%)",
        "scenario.custom_fx": "FX earnings effect (%)",
        "scenario.calibration.title": "Historical plausibility check",
        "scenario.calibration.caption": "Compares modelled total return with rolling historical holding-period returns for the same stock. Fundamental assumptions are also checked against typical sector ranges.",
        "scenario.calibration.samples": "Historical observations",
        "scenario.calibration.weak": "Historically weak · 20%",
        "scenario.calibration.median": "Historical median",
        "scenario.calibration.strong": "Historically strong · 80%",
        "scenario.calibration.volatility": "Annual volatility",
        "scenario.calibration.drawdown": "Max drawdown",
        "scenario.calibration.insufficient": "Only {count} historical observations are available for this horizon. The historical assessment is not robust.",
        "scenario.projection.insufficient": "There is not enough price history for a robust historical assessment.",
        "scenario.projection.below": "The model return is below the historical 20th-percentile range and represents an unusually weak outcome.",
        "scenario.projection.within": "The model return is within the historical 20th- to 80th-percentile range.",
        "scenario.projection.above": "The model return is above the historical 80th-percentile range and assumes an unusually strong outcome.",
        "scenario.growth_assessment.very_weak": "The assumed annual development is weaker than the typical stress range for this sector model.",
        "scenario.growth_assessment.plausible": "The assumed annual development is within the sector range used by the model.",
        "scenario.growth_assessment.very_strong": "The assumed annual development is above the typical strong range for this sector model.",
        "scenario.disclaimer": "Scenarios are not forecasts or price targets. Historical price ranges, current metrics and simplified sector models cannot fully capture structural change, one-off effects or data errors.",
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
        "report.title": "Automated annual-report analysis",
        "report.caption": (
            "Imports PDF, HTML or text reports and identifies business descriptions, risks, opportunities, "
            "dependencies and possible segment or regional data. All outputs are heuristic research aids and "
            "must be checked against the original report."
        ),
        "report.tab.upload": "Upload report",
        "report.tab.official": "Load official report",
        "report.upload": "Select annual report",
        "report.upload_help": "Supports text-based PDF, TXT and HTML files. Scanned PDFs require OCR first.",
        "report.analyze_upload": "Analyse report",
        "report.official_hint": "The latest SEC annual filing is requested for {company} ({ticker}). This is available only for SEC-mapped US tickers and ADRs.",
        "report.load_official": "Load latest SEC annual filing",
        "report.loading": "Loading and analysing official report …",
        "report.loaded": "Report loaded from {source}.",
        "report.content_type": "Content type",
        "report.duration": "Duration ms",
        "report.metric.year": "Fiscal year",
        "report.metric.type": "Report type",
        "report.metric.pages": "Pages",
        "report.metric.characters": "Text characters",
        "report.metric.coverage": "Extraction coverage",
        "report.summary": "Automatically identified summary",
        "report.tab.overview": "Overview",
        "report.tab.findings": "Detected topics",
        "report.tab.candidates": "Review segments & regions",
        "report.tab.text": "Source text",
        "report.tab.risks": "Risks",
        "report.tab.opportunities": "Opportunities",
        "report.tab.dependencies": "Dependencies",
        "report.tab.sections": "Detected sections",
        "report.tab.segments": "Segment candidates",
        "report.tab.regions": "Region candidates",
        "report.column.category": "Category",
        "report.column.confidence": "Confidence",
        "report.column.evidence": "Evidence / source passage",
        "report.column.include": "Include",
        "report.column.segment": "Segment",
        "report.column.region": "Region",
        "report.column.revenue": "Revenue",
        "report.column.share": "Revenue share %",
        "report.no_candidates": "No structured candidates were detected.",
        "report.review_hint": "Check every row against the original report. Only selected rows are written to the local profile files.",
        "report.save_segments": "Save selected segments",
        "report.save_regions": "Save selected regions",
        "report.saved_rows": "Saved {count} row(s).",
        "report.brands": "Possible brands and subsidiaries",
        "report.source_document": "Analysed document: {filename}",
        "report.open_source": "Open original source",
        "report.search_text": "Search extracted text",
        "report.search_empty": "No matching passage was found.",
        "report.extracted_text": "Extracted report text",
        "report.download_text": "Download extracted text",
        "report.save_snapshot": "Save analysis snapshot",
        "report.snapshot_saved": "Snapshot saved: {path}",
        "report.transfer_profile": "Transfer findings to company profile",
        "report.profile_updated": "The qualitative company profile was enriched.",
        "report.snapshots": "Saved report analyses",
        "report.no_snapshots": "No analysis snapshots have been saved for this ticker.",
        "report.snapshot_select": "Select saved analysis",
        "report.snapshot_load": "Load saved analysis",
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
        "news_v2.title": "News and event analysis 2.0",
        "news_v2.caption": (
            "Clusters duplicate reports, separates article tone from potential stock impact and measures "
            "historical market reactions versus {benchmark}."
        ),
        "news_v2.no_events": "No sufficiently relevant event clusters were identified in the selected period.",
        "news_v2.metric.clusters": "Event clusters",
        "news_v2.metric.official": "High source trust",
        "news_v2.metric.negative": "Negative stock impact",
        "news_v2.metric.reactions": "With market reaction",
        "news_v2.filter.event": "Event type",
        "news_v2.filter.impact": "Potential stock impact",
        "news_v2.filter.trust": "Minimum source trust",
        "news_v2.filter.multi": "Multiple sources only",
        "news_v2.column.event": "Event",
        "news_v2.column.title": "Title",
        "news_v2.column.tone": "Article tone",
        "news_v2.column.impact": "Stock impact",
        "news_v2.column.trust": "Source trust",
        "news_v2.column.sources": "Sources",
        "news_v2.column.excess20": "20D excess return",
        "news_v2.filtered_empty": "No event matches the current filters.",
        "news_v2.detail.select": "Select event for details",
        "news_v2.primary_source": "Primary source",
        "news_v2.sources_detail": "Clustered sources",
        "news_v2.open_source": "Open source",
        "news_v2.source_summary": "Source summary",
        "news_v2.fulltext.load": "Fetch text excerpt from primary source",
        "news_v2.fulltext.loading": "Loading text excerpt …",
        "news_v2.fulltext.chars": "Extracted characters",
        "news_v2.fulltext.excerpt": "Limited text excerpt",
        "news_v2.fulltext.notice": (
            "Text is fetched only after a user action and is not stored in full in the event database. "
            "Paywalls, terms of use and source rights still apply."
        ),
        "news_v2.database.save": "Save analysis to local event database",
        "news_v2.database.saved": "Saved {events} events and {articles} source reports.",
        "news_v2.database.status": (
            "Local event database: last saved {timestamp} · {events} events · {articles} source reports"
        ),
        "news_v2.disclaimer": (
            "Tone, stock impact and source trust are heuristic research aids. Market reactions show historical "
            "movements, not causality or a forecast."
        ),
    },
}


_AI_LAB_TRANSLATIONS: Final[dict[str, dict[str, str]]] = {
    "de": {
        "nav.ai_lab": "KI-/RL-Labor",
        "ai.title": "KI-/Reinforcement-Learning-Labor",
        "ai.caption": (
            "Vergleicht transparente Regelstrategien mit einem eingebauten Q-Learning-Agenten in "
            "expanding Walk-forward-Tests. Nur außerhalb der Trainingsfenster erzielte Ergebnisse werden verglichen."
        ),
        "ai.research_warning": (
            "Research-Modul: Die Ergebnisse sind keine Kauf-, Halte- oder Verkaufsempfehlung. "
            "Ein gutes historisches Testergebnis kann durch Überanpassung, Datenfehler und veränderte Marktbedingungen entstehen."
        ),
        "ai.load_data": "Bitte zuerst Index- und Marktdaten laden.",
        "ai.history_hint": (
            "Standardmäßig nutzt das Labor die bereits geladenen Kursdaten. Für belastbarere Walk-forward-Tests "
            "kannst du die maximal verfügbare Historie separat laden."
        ),
        "ai.load_max_history": "Maximale Historie laden",
        "ai.loading_history": "Lade vollständige Kurshistorie …",
        "ai.history_loaded": "{count} historische Kurspunkte geladen.",
        "ai.history_error": "Für diesen Ticker konnte keine längere Historie geladen werden.",
        "ai.no_history": "Für das KI-Labor fehlen mindestens rund 260 Handelstage Kursdaten.",
        "ai.settings": "Walk-forward- und Trainingsparameter",
        "ai.training_years": "Anfängliche Trainingsjahre",
        "ai.test_months": "Testfenster in Monaten",
        "ai.step_months": "Weiterrollen alle Monate",
        "ai.episodes": "Q-Learning-Episoden je Fold",
        "ai.costs": "Handelskosten in Basispunkten",
        "ai.downside_penalty": "Strafe für negative Tagesrenditen",
        "ai.seed": "Zufalls-Seed",
        "ai.run": "Walk-forward-Analyse starten",
        "ai.running": "Trainiere und teste Strategien ausschließlich auf den jeweiligen Out-of-Sample-Fenstern …",
        "ai.error": "KI-Labor konnte nicht ausgeführt werden: {error}",
        "ai.run_prompt": "Starte die Analyse, um Baselines und Q-Learning außerhalb der Trainingsdaten zu vergleichen.",
        "ai.metric.folds": "Test-Folds",
        "ai.metric.period": "Out-of-Sample-Zeitraum",
        "ai.metric.best": "Beste historische Strategie",
        "ai.metric.q_states": "Gelernte Zustände",
        "ai.metric.q_return": "Q-Learning-Rendite",
        "ai.comparison": "Strategievergleich außerhalb der Trainingsdaten",
        "ai.strategy.buy_hold": "Buy & Hold",
        "ai.strategy.momentum": "Momentum-Regel",
        "ai.strategy.recovery": "Drawdown-Recovery-Regel",
        "ai.strategy.combined": "Kombinierte Regel",
        "ai.strategy.q_learning": "Q-Learning-Agent",
        "ai.column.strategy": "Strategie",
        "ai.column.total_return": "Gesamtrendite",
        "ai.column.annualized": "Rendite p.a.",
        "ai.column.volatility": "Volatilität p.a.",
        "ai.column.sharpe": "Sharpe",
        "ai.column.drawdown": "Max. Drawdown",
        "ai.column.exposure": "Investitionsquote",
        "ai.column.trades": "Positionswechsel",
        "ai.column.turnover": "Umschlag",
        "ai.column.date": "Datum",
        "ai.column.equity": "Modellwert",
        "ai.chart_equity": "Out-of-Sample-Modellwert · Start 100",
        "ai.folds": "Ergebnisse je Walk-forward-Fold",
        "ai.fold.number": "Fold",
        "ai.fold.train_start": "Training Start",
        "ai.fold.train_end": "Training Ende",
        "ai.fold.test_start": "Test Start",
        "ai.fold.test_end": "Test Ende",
        "ai.fold.train_rows": "Trainingstage",
        "ai.fold.test_rows": "Testtage",
        "ai.fold.q_return": "Q-Learning",
        "ai.fold.buy_hold": "Buy & Hold",
        "ai.fold.momentum": "Momentum",
        "ai.explanation": "Wie das Labor arbeitet",
        "ai.explanation_text": (
            "**Zustand:** Trend zu SMA 50/200, 20-Tage-Momentum, Volatilität, Drawdown und aktuelle Position.  \n"
            "**Aktionen:** verkaufen/auf Cash wechseln, Position halten oder vollständig investieren.  \n"
            "**Belohnung:** nächste Tagesrendite abzüglich Handelskosten und einer einstellbaren Downside-Strafe.  \n"
            "**Walk-forward:** Der Agent wird nur mit früheren Daten trainiert und anschließend im nächsten Zeitfenster getestet. "
            "Danach wird das Trainingsfenster erweitert."
        ),
        "ai.action": "Aktion",
        "ai.action.count": "Anzahl im Test",
        "ai.action.sell": "Verkaufen / Cash",
        "ai.action.hold": "Halten",
        "ai.action.buy": "Kaufen / investiert",
        "ai.no_fundamental_leakage": (
            "Heutige Aktien-Scores werden nur als Kontext angezeigt und bewusst nicht als historische Trainingsmerkmale genutzt. "
            "Ohne Point-in-Time-Fundamentaldaten würde dies einen Rückschaufehler erzeugen."
        ),
        "ai.save": "Analyse lokal speichern",
        "ai.saved": "Analyse gespeichert: {path}",
        "ai.disclaimer": (
            "Das Q-Learning-Modell ist absichtlich einfach und dient als überprüfbare Forschungsbaseline. "
            "Es berücksichtigt keine Steuern, Slippage, Liquiditätsgrenzen, Short-Positionen oder fundamentale Point-in-Time-Daten."
        ),
    },
    "en": {
        "nav.ai_lab": "AI / RL lab",
        "ai.title": "AI / reinforcement-learning lab",
        "ai.caption": (
            "Compares transparent rule-based strategies with a built-in Q-learning agent using expanding "
            "walk-forward tests. Only results generated outside the training windows are compared."
        ),
        "ai.research_warning": (
            "Research module: results are not buy, hold or sell recommendations. Strong historical results may be caused "
            "by overfitting, data errors or changing market regimes."
        ),
        "ai.load_data": "Load index and market data first.",
        "ai.history_hint": (
            "The lab initially uses the price data already loaded by the app. Load the maximum available history "
            "separately for more meaningful walk-forward tests."
        ),
        "ai.load_max_history": "Load maximum history",
        "ai.loading_history": "Loading full price history …",
        "ai.history_loaded": "Loaded {count} historical price observations.",
        "ai.history_error": "No longer history could be loaded for this ticker.",
        "ai.no_history": "The AI lab requires at least roughly 260 trading days of price data.",
        "ai.settings": "Walk-forward and training parameters",
        "ai.training_years": "Initial training years",
        "ai.test_months": "Test-window months",
        "ai.step_months": "Roll forward every months",
        "ai.episodes": "Q-learning episodes per fold",
        "ai.costs": "Trading costs in basis points",
        "ai.downside_penalty": "Negative daily-return penalty",
        "ai.seed": "Random seed",
        "ai.run": "Run walk-forward analysis",
        "ai.running": "Training and evaluating strategies exclusively on their out-of-sample windows …",
        "ai.error": "AI lab failed: {error}",
        "ai.run_prompt": "Run the analysis to compare baselines and Q-learning outside the training data.",
        "ai.metric.folds": "Test folds",
        "ai.metric.period": "Out-of-sample period",
        "ai.metric.best": "Best historical strategy",
        "ai.metric.q_states": "Learned states",
        "ai.metric.q_return": "Q-learning return",
        "ai.comparison": "Out-of-sample strategy comparison",
        "ai.strategy.buy_hold": "Buy and hold",
        "ai.strategy.momentum": "Momentum rule",
        "ai.strategy.recovery": "Drawdown-recovery rule",
        "ai.strategy.combined": "Combined rule",
        "ai.strategy.q_learning": "Q-learning agent",
        "ai.column.strategy": "Strategy",
        "ai.column.total_return": "Total return",
        "ai.column.annualized": "Annualised return",
        "ai.column.volatility": "Annualised volatility",
        "ai.column.sharpe": "Sharpe",
        "ai.column.drawdown": "Maximum drawdown",
        "ai.column.exposure": "Market exposure",
        "ai.column.trades": "Position changes",
        "ai.column.turnover": "Turnover",
        "ai.column.date": "Date",
        "ai.column.equity": "Model value",
        "ai.chart_equity": "Out-of-sample model value · start 100",
        "ai.folds": "Results by walk-forward fold",
        "ai.fold.number": "Fold",
        "ai.fold.train_start": "Training start",
        "ai.fold.train_end": "Training end",
        "ai.fold.test_start": "Test start",
        "ai.fold.test_end": "Test end",
        "ai.fold.train_rows": "Training days",
        "ai.fold.test_rows": "Test days",
        "ai.fold.q_return": "Q-learning",
        "ai.fold.buy_hold": "Buy and hold",
        "ai.fold.momentum": "Momentum",
        "ai.explanation": "How the lab works",
        "ai.explanation_text": (
            "**State:** SMA 50/200 trend, 20-day momentum, volatility, drawdown and current position.  \n"
            "**Actions:** sell/move to cash, hold the current position or invest fully.  \n"
            "**Reward:** next-day return minus trading costs and a configurable downside penalty.  \n"
            "**Walk-forward:** The agent is trained only on earlier observations and tested in the following period. "
            "The training window is then expanded."
        ),
        "ai.action": "Action",
        "ai.action.count": "Count in test",
        "ai.action.sell": "Sell / cash",
        "ai.action.hold": "Hold",
        "ai.action.buy": "Buy / invested",
        "ai.no_fundamental_leakage": (
            "Today's stock scores are displayed as context only and are deliberately excluded from historical training. "
            "Using them without point-in-time fundamentals would introduce look-ahead bias."
        ),
        "ai.save": "Save analysis locally",
        "ai.saved": "Analysis saved: {path}",
        "ai.disclaimer": (
            "The Q-learning model is intentionally simple and serves as an auditable research baseline. "
            "It does not model taxes, slippage, liquidity constraints, short positions or point-in-time fundamentals."
        ),
    },
}

for _language, _messages in _AI_LAB_TRANSLATIONS.items():
    TRANSLATIONS[_language].update(_messages)


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
