# V6.2-Patch in dein bestehendes V6.1.1-Projekt einfügen

Entpacke den Patch. Kopiere anschließend den Inhalt **mit gleicher Ordnerstruktur**
in deinen bestehenden Projektordner. Vorhandene Dateien dürfen überschrieben werden.

## Dateien ersetzen

```text
requirements.txt
README.md
CHANGELOG.md
scripts/check.ps1
stock_explorer/__init__.py
stock_explorer/legacy_app.py
stock_explorer/providers/__init__.py
stock_explorer/providers/registry.py
```

## Dateien neu anlegen

```text
stock_explorer/providers/company_profiles.py
stock_explorer/providers/events.py
stock_explorer/providers/fx.py
stock_explorer/providers/http.py
stock_explorer/providers/indexes.py
stock_explorer/providers/models.py
stock_explorer/providers/news.py
stock_explorer/providers/sec.py

stock_explorer/services/__init__.py
stock_explorer/services/event_service.py
stock_explorer/services/index_service.py
stock_explorer/services/news_service.py
stock_explorer/services/profile_service.py

tests/test_event_service.py
tests/test_index_provider.py
tests/test_news_provider.py
tests/test_profile_service.py
tests/test_sec_provider.py
```

## Danach im IntelliJ-Terminal

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
python -m streamlit run app.py
```

## Git

```powershell
git status
git add .
git commit -m "V6.2 modulare Datenprovider und Services"
git push
```
