# V6.8-Patch installieren

Dieser Patch setzt einen funktionierenden Stand **V6.7** voraus.

## 1. Vorbereiten

Streamlit im Terminal mit `Strg + C` stoppen. Optional einen neuen Git-Branch anlegen:

```powershell
git switch main
git pull origin main
git switch -c feature/news-events-v68
```

## 2. Dateien kopieren

Den Inhalt dieses Patch-Ordners in den bestehenden Projektordner
`Aktien_Explorer_V6_0_1_modular/` kopieren. Die Ordnerstruktur entspricht bereits
den Zielpfaden. Vorhandene Dateien ersetzen.

### Ersetzte Dateien

```text
.gitignore
README.md
CHANGELOG.md
stock_explorer/__init__.py
stock_explorer/legacy_app.py
stock_explorer/domain/__init__.py
stock_explorer/domain/news_analysis.py
stock_explorer/providers/registry.py
stock_explorer/services/__init__.py
stock_explorer/ui/__init__.py
stock_explorer/i18n/translations.py
```

### Neue Dateien

```text
stock_explorer/domain/news_intelligence.py
stock_explorer/domain/market_reaction.py
stock_explorer/providers/article_text.py
stock_explorer/services/event_database.py
stock_explorer/services/news_intelligence_service.py
stock_explorer/ui/news_intelligence.py

tests/test_news_intelligence_v68.py
tests/test_market_reaction_v68.py
tests/test_event_database_v68.py
tests/test_article_text_provider_v68.py
```

## 3. Prüfen

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
```

Der geprüfte Patch liefert:

```text
57 Tests bestanden
Ruff erfolgreich
Mypy erfolgreich
Syntaxprüfung erfolgreich
```

## 4. App testen

```powershell
python -m streamlit run app.py
```

Danach:

1. Einen Index und eine Aktie laden.
2. `News & Events` öffnen.
3. News aktualisieren.
4. Den Unterbereich `Analyse 2.0` öffnen.
5. Ereigniscluster, Quellenvertrauen und Kursreaktionen prüfen.
6. Optional einen Textauszug einer Primärquelle auf Nutzeraktion laden.
7. Die Analyse in der lokalen Ereignisdatenbank speichern.

Die Datenbank liegt unter:

```text
data/events_database/
```

Dieser Ordner ist in `.gitignore` enthalten.

## 5. Commit und Push

```powershell
git status
git add .
git commit -m "V6.8 News- und Eventanalyse 2.0"
git push -u origin feature/news-events-v68
```

Nach dem Merge in `main` optional taggen:

```powershell
git switch main
git pull origin main
git tag -a v6.8.0 -m "News- und Eventanalyse 2.0"
git push origin v6.8.0
```

## Hinweise

- Der Volltextabruf erfolgt nur für eine einzelne ausgewählte Quelle nach ausdrücklicher Nutzeraktion.
- Vollständige fremde Artikel werden nicht in der Ereignisdatenbank gespeichert.
- Kursreaktionen zeigen historische Bewegungen, aber keine nachgewiesene Kausalität.
- Quellenvertrauen, Ton und Aktienwirkung sind heuristische Recherchehilfen.
