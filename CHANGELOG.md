# Changelog

## 6.5.0

- Ereignisbasierte Portfolio-Simulation aus `data/transactions.csv`.
- Cash-Konto, Ein- und Auszahlungen sowie automatische Kauf-Finanzierung.
- Historische Dividenden mit optionaler Reinvestition und Modellsteuer.
- Historische FX-Umrechnung über den modularen FX-Provider.
- Unterstützung für BUY, SELL, DEPOSIT, WITHDRAWAL, DIVIDEND, FEE und SPLIT.
- Zeitgewichtete Rendite (TWR) und geldgewichtete Rendite (XIRR).
- Vergleich mit DAX, S&P 500, MSCI-World-ETF oder eigenem Benchmark.
- Bestehendes Gewichtungs-/Rebalancing-Modell bleibt als zweiter Modus erhalten.
- Neuer `PortfolioSimulationService` und neue UI-unabhängige Ledger-Domainlogik.
- Fünf zusätzliche Tests für Ledger, Dividenden, XIRR und Provider-Orchestrierung.

## 6.4.0

- Zentrale Deutsch-/Englisch-Umschaltung über die Sidebar.
- Vollständiger Übersetzungskatalog mit automatischer Fallback-Logik.
- Sprachabhängige Zahlen-, Prozent-, Währungs- und Datumsformatierung.
- Hauptnavigation verwendet stabile Seiten-IDs statt sichtbarer Labels.
- App-Kopf und zentrale Sidebar lokalisiert.
- Szenario-Engine, Portfolio-Simulation, Datenquellen-Monitor und Profilautomatisierung vollständig lokalisiert.
- Neuer modularer App-Rahmen in `ui/app_shell.py`.
- Mypy-Prüfung auf `i18n` und `ui` erweitert.
- Fünf zusätzliche Tests für Übersetzungskatalog, Formatierung und Navigation.

## 6.3.0

- Firmenzuordnung, News-Relevanz, Sentiment und Ereignisklassifikation in `domain/news_analysis.py` ausgelagert.
- Offizielle Unternehmens-IR-Feeds und ICS-Kalender als austauschbarer Event-Provider.
- Konflikt- und Prioritätslogik für Ereignisse in `domain/event_resolution.py`.
- SEC Company Facts als zweite automatische Profilquelle für US-Unternehmen und ADRs.
- Neuer Provider-Monitor für News-, Event- und Profilquellen in der Streamlit-Oberfläche.
- Neuer Profilbereich „Automatische Anreicherung“ mit offiziellen SEC-Finanzreihen.
- Quellen-Gesundheitsscore und transparentere Providerdiagnose.
- 24 automatisierte Tests für Provider-, Domain- und Service-Logik.

## 6.2.0

- Austauschbare Provider für FX, Indizes, News, Events, SEC und Unternehmensprofile.
- Neue Service-Schicht zur Orchestrierung mehrerer Quellen.
- News-Transport von RSS und Google News aus der Bestands-App ausgelagert.
- SEC-Filings und Yahoo-/manuelle Kalendertermine über Event-Provider angebunden.
- Indexabruf über CSV-/Offline-/S&P-Provider.
- Profilanreicherung über einen Yahoo-Profilprovider.
- Zwölf Tests für Domain- und Providerlogik.
- Qualitätsprüfung um `stock_explorer/services` erweitert.

## 6.1.0

- Szenario- und Prognose-Engine als eigenständiges UI-Modul eingebunden.
- Transparente schwache, mittlere und starke Szenarien sowie benutzerdefinierte Annahmen.
- Portfolio-Simulation mit Buy-and-Hold-Vergleich, regelmäßigem Rebalancing, Gebühren und Dividenden-Näherung.
- Neue Tests für Szenariologik, Handelskosten und Dividendenerfassung.

## 6.0.1

- Python-3.13-, Ruff- und Mypy-Konfiguration korrigiert.
