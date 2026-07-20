# Changelog

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
