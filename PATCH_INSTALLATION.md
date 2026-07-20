# V6.3-Patch auf ein bestehendes V6.2-Projekt anwenden

Kopiere den **gesamten Inhalt dieses Patch-Ordners** in den Stammordner deines
bestehenden Projekts. Die Ordnerstruktur entspricht dem Zielpfad. Bei
Rückfragen von Windows/IntelliJ vorhandene Dateien ersetzen.

## Dateien ersetzen

```text
README.md
CHANGELOG.md
stock_explorer/__init__.py
stock_explorer/legacy_app.py
stock_explorer/domain/portfolio_simulation.py
stock_explorer/providers/registry.py
stock_explorer/providers/sec.py
stock_explorer/services/event_service.py
stock_explorer/services/news_service.py
stock_explorer/services/profile_service.py
stock_explorer/ui/__init__.py
stock_explorer/ui/portfolio_simulation.py
stock_explorer/ui/scenarios.py
```

## Dateien neu hinzufügen

```text
stock_explorer/domain/event_resolution.py
stock_explorer/domain/news_analysis.py
stock_explorer/providers/ir.py
stock_explorer/providers/sec_companyfacts.py
stock_explorer/services/source_health.py
stock_explorer/ui/profile_automation.py
stock_explorer/ui/source_monitor.py

tests/test_event_resolution.py
tests/test_ir_provider.py
tests/test_news_analysis.py
tests/test_sec_companyfacts.py
tests/test_source_health.py
```

## Optionale Vorlage

```text
templates/ir_sources_template.csv
```

Deine bestehende Datei `data/ir_sources.csv` wird vom Patch **nicht**
überschrieben. Nutze die Vorlage nur als Orientierung.

## Nach dem Kopieren

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
python -m streamlit run app.py
```

Erwarteter Prüflauf:

```text
24 passed
All checks passed
Success: no issues found
Alle Qualitätsprüfungen waren erfolgreich.
```

## Neue Oberfläche prüfen

1. Einen Index und Marktdaten laden.
2. Den neuen Hauptbereich **Datenquellen** öffnen.
3. Ein Unternehmen auswählen und News-, Event- und Profilquellen prüfen.
4. Unter **Unternehmensprofile** den Bereich **Automatische Anreicherung** öffnen.
5. Bei einem US-Ticker ohne Börsensuffix, z. B. `MSFT`, die SEC-Finanzreihe prüfen.
6. Unter **News & Events** kontrollieren, ob konfigurierte IR-RSS-/ICS-Quellen eingebunden werden.

## Git

```powershell
git status
git add .
git commit -m "V6.3 News-, Event- und Profilautomatisierung"
git pull --rebase origin main
git push origin main
```

Optional:

```powershell
git tag -a v6.3.0 -m "News-, Event- und Profilautomatisierung"
git push origin v6.3.0
```
