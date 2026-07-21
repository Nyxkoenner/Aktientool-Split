# V7.2.1 – Versionsanzeige-Fix

Dieser Mini-Patch setzt V7.2 voraus.

## Ersetzt

- `stock_explorer/config.py`

## Neu

- `tests/test_version_consistency_v721.py`

Nach dem Kopieren Streamlit vollständig stoppen und neu starten:

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\check.ps1
python -m streamlit run app.py
```

Danach muss im Kopf der Anwendung `Version 7.2.0` stehen.
