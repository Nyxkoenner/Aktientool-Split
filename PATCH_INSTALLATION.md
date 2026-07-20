# V6.4-Patch installieren

Dieser Patch setzt **V6.3.1** voraus.

## 1. Backup oder Git-Commit anlegen

```powershell
git status
git add .
git commit -m "Backup vor V6.4"
```

Falls nichts zu committen ist, kannst du direkt fortfahren.

## 2. Dateien kopieren

Entpacke die ZIP-Datei. Kopiere anschließend den gesamten Inhalt des entpackten
Ordners in deinen bestehenden Projektordner. Die Verzeichnisstruktur entspricht
bereits den Zielpfaden.

Vorhandene Dateien beim Kopieren ersetzen.

### Ersetzt werden

```text
README.md
CHANGELOG.md
scripts/check.ps1
stock_explorer/__init__.py
stock_explorer/legacy_app.py
stock_explorer/i18n/__init__.py
stock_explorer/i18n/translations.py
stock_explorer/ui/__init__.py
stock_explorer/ui/portfolio_simulation.py
stock_explorer/ui/profile_automation.py
stock_explorer/ui/scenarios.py
stock_explorer/ui/source_monitor.py
```

### Neu angelegt werden

```text
stock_explorer/i18n/context.py
stock_explorer/i18n/formatting.py
stock_explorer/i18n/navigation.py
stock_explorer/ui/app_shell.py
tests/test_app_shell.py
tests/test_i18n.py
```

## 3. Qualitätsprüfung

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
```

Erwartet werden unter anderem:

```text
29 passed
All checks passed
Success: no issues found
Alle Qualitätsprüfungen waren erfolgreich.
```

## 4. App starten

```powershell
python -m streamlit run app.py
```

Oben in der Sidebar erscheint nun die Sprachauswahl **Deutsch / English**.

## 5. Git-Commit

```powershell
git status
git add .
git commit -m "V6.4 Mehrsprachigkeit und modularer App-Rahmen"
git pull --rebase origin main
git push origin main
```

Optional:

```powershell
git tag -a v6.4.0 -m "Mehrsprachigkeit und modularer App-Rahmen"
git push origin v6.4.0
```

## Umfang der Übersetzung

V6.4 lokalisiert den App-Kopf, die Hauptnavigation, die zentrale Sidebar sowie
alle bereits modularisierten UI-Seiten. Ältere Detailansichten, die noch in
`legacy_app.py` stecken, bleiben vorübergehend teilweise deutsch und werden bei
der weiteren UI-Auslagerung schrittweise umgestellt.
