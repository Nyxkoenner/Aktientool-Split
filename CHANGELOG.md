# Changelog

## 7.2.0

- Lokale, versionierte Q-Learning-Modelle pro Aktie unter `data/ai_models/`.
- Sichere JSON/Gzip-Persistenz ohne Pickle und mit atomarem Dateiaustausch.
- Vollständiges Neutraining, kontrolliertes Nachtraining nur auf neuen Marktübergängen und reine Out-of-Sample-Auswertung.
- Kompatibilitätsprüfung für Ticker, Modell-/Feature-Schema, Lernparameter, Kostenparameter und Datenüberlappung.
- Gespeicherte Metadaten zu Datenstand, Modellvorgänger, Trainingsläufen, Episoden, Zuständen und Datenfingerabdruck.
- Vergleich zweier Modellversionen über Aktionsübereinstimmung, Kaufquote und Trainingsmetadaten.
- Gezieltes Löschen einzelner Modellversionen sowie deutsche und englische Oberfläche.
- Neue Regressionstests für Modell-Roundtrip, Nachtraining, Kompatibilität, Auswertung, Vergleich und Übersetzungen.

## 7.1.0

- Schnell-, Standard-, Intensiv- und benutzerdefinierter Laufzeitmodus im KI-/RL-Labor.
- Begrenzbarer Analysezeitraum, maximale Fold-Anzahl und Laufzeitlimit.
- Vorab-Schätzung von Trainingsschritten und erwarteter Laufzeit.
- Fortschrittsanzeige je Walk-forward-Fold mit sauberem Stopp an Fold-Grenzen.
- Verwertbare Teilergebnisse, wenn Fold- oder Zeitlimit erreicht wurde.
- Cache für vorbereitete Feature- und Walk-forward-Pläne sowie sichtbare Cache-Steuerung.
- Datenqualitätsbericht für Historien mit Lücken, Duplikaten, ungültigen Preisen und Aktualität.
- Rotierendes lokales Anwendungsprotokoll unter `data/logs/stock_explorer.log`.
- Erweiterte gespeicherte AI-Lab-Runs mit Laufzeit-, Planungs- und Abbruchmetadaten.
- Vier neue Tests für Laufzeitplanung, Datenqualität, sichere Teilresultate und Logging.

## 7.0.0

- Neuer modularer Einstiegspunkt `stock_explorer.app_runtime` statt Start aus `legacy_app.py`.
- Sidebar für Index, Sektor, Suche und Scanner-Profile in ein eigenes UI-Modul ausgelagert.
- Expliziter, testbarer Seiten-Router ersetzt die lange zentrale `if/elif`-Kette.
- Session-State und Refresh-Entscheidung des geladenen Aktienuniversums in einem Service gekapselt.
- Gemeinsame Zahlen-, Ticker-, Datums- und DataFrame-Helfer in `domain/value_utils.py` ausgelagert.
- Unternehmensauswahl als wiederverwendbares UI-Element extrahiert.
- Acht doppelte ältere News-/Event-Funktionsdefinitionen aus der Kompatibilitätsschicht entfernt.
- Qualitätsprüfung auf das gesamte Paket und den neuen Einstiegspunkt erweitert.
- Zusätzliche Architektur-, Router-, Session- und Utility-Tests.

## 6.8.0

- News- und Ereigniscluster mit quellenübergreifender Deduplizierung.
- Getrennte Bewertung von Nachrichtenton und möglicher Aktienwirkung.
- Erweiterte Ereignistaxonomie für Prognosen, Gewinnwarnungen, Dividenden, Rückkäufe, Kapitalmaßnahmen, M&A, Management, Regulierung und Produktzulassungen.
- Quellenvertrauen von 0 bis 100 mit nachvollziehbarer Quellenkategorie.
- Kursreaktionen nach 1, 5 und 20 Handelstagen sowie Überrenditen zur Index-Benchmark.
- Volatilitätsvergleich und maximaler Rückgang nach historischen Ereignissen.
- Lokale Ereignisdatenbank unter `data/events_database/` mit atomarem Schreiben und Deduplizierung.
- Begrenzter Volltextabruf einer einzelnen Primärquelle auf ausdrückliche Nutzeraktion.
- Deutsche und englische Oberfläche sowie sechs neue Tests für Klassifikation, Clustering, Marktreaktion, Persistenz und Textextraktion.

## 6.7.0

- Automatischer Import textbasierter PDF-, HTML- und TXT-Geschäftsberichte.
- Offizielle SEC-Jahresberichte (10-K, 20-F und 40-F) über einen modularen Provider.
- Heuristische Erkennung von Geschäftsmodell, Risiken, Chancen, Abhängigkeiten, Marken und Tochtergesellschaften.
- Vorschläge für Segment- und Regionsdaten mit Konfidenz und Originaltextbeleg.
- Review-Workflow vor dem Schreiben in `data/company_segments.csv` und `data/company_regions.csv`.
- Gespeicherte Analyse-Snapshots unter `data/company_documents/`.
- Übernahme geprüfter Erkenntnisse in das qualitative Unternehmensprofil.
- Deutsche und englische Oberfläche sowie neue Tests für Analyse, Provider und Persistenz.


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

## 6.6.0

- sektorspezifische Szenario- und Prognose-Engine 2.0
- vorkonfigurierte Stressfälle für Rezession, Zinsen, Inflation, Margendruck, Dividendenkürzung, Schuldenabbau, Bewertung und Währung
- getrennte Modelle für Banken, Versicherungen, Immobilien, Technologie, Industrie, Versorger, Energie, Konsum und Gesundheit
- schwache, mittlere und starke Modellbandbreiten
- historische Plausibilitätsprüfung mit rollierenden Haltedauerrenditen, Volatilität und Drawdown
- frei konfigurierbares individuelles Szenario
- vollständige deutsche und englische Übersetzung des neuen Moduls
- neue Domain-, Service- und Kalibrierungstests

## 6.9.0

- Neues zweisprachiges KI-/RL-Labor mit expanding Walk-forward-Tests.
- Eingebaute Q-Learning-Baseline mit den Aktionen Verkaufen/Cash, Halten und Kaufen/Investiert.
- Vergleich gegen Buy-and-Hold, Momentum, Drawdown-Recovery und eine kombinierte Regelstrategie.
- Transaktionskosten, Downside-Strafe, reproduzierbarer Zufalls-Seed und einstellbare Trainings-/Testfenster.
- Out-of-Sample-Kennzahlen für Rendite, Volatilität, Sharpe, Drawdown, Investitionsquote, Positionswechsel und Turnover.
- Bewusster Schutz vor Look-ahead-Bias: heutige Fundamental-Scores werden nicht als historische Trainingsmerkmale verwendet.
- Lokale, nicht versionierte Speicherung von Forschungsruns unter `data/ai_lab/`.
