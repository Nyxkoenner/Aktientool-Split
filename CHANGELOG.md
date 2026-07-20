# Changelog

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
