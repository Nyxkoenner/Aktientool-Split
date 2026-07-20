# Aktien Explorer V6.0.1

V6.0.1 ist die korrigierte modulare Grundlage des bisherigen Streamlit-Tools.

## Unterstützte Python-Version

Dieses Projekt ist auf **Python 3.13** abgestimmt. Prüfe deine aktive Umgebung mit:

```powershell
python --version
python -c "import sys; print(sys.executable)"
```

Beide Befehle sollten auf die `.venv` des Projektordners zeigen.

## Start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Architektur

- `app.py`: stabiler Streamlit-Einstiegspunkt
- `stock_explorer/legacy_app.py`: bestehende vollständige Benutzeroberfläche
- `stock_explorer/providers/`: austauschbare Marktdatenanbieter
- `stock_explorer/domain/`: neue, UI-unabhängige Logik
- `stock_explorer/i18n/`: zentrale Übersetzungen
- `tests/`: schnelle Logik- und Vertragstests

Der Umbau folgt dem Strangler-Pattern: Das funktionierende Tool bleibt erhalten,
während Datenzugriffe und Fachlogik schrittweise aus der alten Datei herausgezogen werden.

## Datenanbieter wechseln

Aktuell ist Yahoo implementiert. Die Auswahl läuft über:

```powershell
$env:AKTIEN_EXPLORER_MARKET_PROVIDER="yahoo"
```

Weitere Anbieter implementieren `MarketDataProvider` und werden in
`stock_explorer/providers/registry.py` registriert.

## Qualitätssicherung

Komplettlauf:

```powershell
.\scripts\check.ps1
```

Einzelschritte:

```powershell
python -m pytest
python -m ruff format --check stock_explorer tests
python -m ruff check stock_explorer tests
python -m mypy stock_explorer/providers stock_explorer/domain
python -m py_compile app.py stock_explorer/legacy_app.py
```

### Warum `legacy_app.py` noch nicht vollständig gelintet wird

Die große Bestandsdatei wird in dieser Übergangsphase weiterhin ausgeführt und per
`py_compile` auf Syntaxfehler geprüft. Ruff und Mypy prüfen bereits die neuen Module.
Die Bestandsdatei wird in den folgenden V6-Releases schrittweise aufgeteilt und dann
abschnittsweise in die strengeren Prüfungen aufgenommen. So bleibt die laufende App
stabil, ohne technische Altlasten zu verschweigen.

## Git-Start

```powershell
git init
git add .
git commit -m "V6.0.1 modular foundation and checks"
git tag v6.0.1
```

## Nächste Releases

- V6.1: Szenario-Engine und Portfolio-Simulation in die Oberfläche integrieren
- V6.2: News-/Event-Provider und automatische Unternehmensprofile modularisieren
- V6.3: vollständiges i18n-System
- V6.4: KI-/RL-Labor mit Baselines und Walk-forward-Tests
