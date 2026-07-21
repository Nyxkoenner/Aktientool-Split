# Aktien Explorer V7.2.6 – Versions-Test-Fix

Dieser Mini-Patch setzt V7.2.5 voraus.

## Ursache

Die ältere Datei `tests/test_version_consistency_v721.py` erwartete weiterhin fest die Version `7.2.2`. Nach dem Update auf V7.2.5 musste der Test deshalb scheitern, obwohl Paket- und Anzeigeversion korrekt übereinstimmten.

## Installation

Den gesamten Inhalt dieses Ordners in das Projektverzeichnis kopieren und vorhandene Dateien ersetzen.

Ersetzt werden:

- `stock_explorer/__init__.py`
- `stock_explorer/config.py`
- `tests/test_version_consistency_v721.py`
- `tests/test_version_consistency_v724.py`

Danach ausführen:

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\check.ps1
python -m streamlit run app.py
```

Die App zeigt anschließend Version `7.2.6`. Die Regressionstests prüfen künftig nur noch, dass Paket- und Anzeigeversion übereinstimmen und dem Format `X.Y.Z` entsprechen. Sie enthalten keine veraltete feste Versionsnummer mehr.
