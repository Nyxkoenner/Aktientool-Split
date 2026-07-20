# V7.0.3 – Ruff-Formatierungsfix

Dieser Mini-Patch ersetzt ausschließlich:

```text
tests/test_mypy_numpy_compatibility_v702.py
```

Kopiere den Inhalt des Patch-Ordners in das Projekt und ersetze die vorhandene Datei.

Danach ausführen:

```powershell
.\.venv\Scripts\Activate.ps1
python -m ruff format --check stock_explorer tests app.py
.\scripts\check.ps1
```

Anschließend committen:

```powershell
git add tests/test_mypy_numpy_compatibility_v702.py
git commit -m "V7.0.3 Ruff Formatierungsfix"
git push origin feature/architecture-v70
```
