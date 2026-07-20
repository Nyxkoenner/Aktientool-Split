# Aktien Explorer V7.0 – Installation

Dieser Patch setzt einen funktionierenden **V6.9-Stand** voraus.

## 1. Branch anlegen

```powershell
git switch main
git pull --ff-only origin main
git switch -c feature/architecture-v70
```

## 2. Dateien kopieren

Streamlit mit `Strg + C` stoppen. Danach den kompletten Inhalt dieses Patch-Ordners in den bestehenden Projektordner kopieren und vorhandene Dateien ersetzen.

Der Patch verändert keine persönlichen Dateien in `data/`, `.cache/`, `.venv/`, `portfolio.csv` oder `data/transactions.csv`.

## 3. Abhängigkeiten und Prüfungen

V7.0 fügt keine neue Laufzeitabhängigkeit hinzu.

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
python -m streamlit run app.py
```

## 4. Manuelle Kurzprüfung

1. Sprache zwischen Deutsch und Englisch umschalten.
2. Einen Index laden und Sektor-/Suchfilter verändern.
3. Scanner-Profil wechseln und die vier Schwellenwerte verändern.
4. Jede Hauptnavigation mindestens einmal öffnen.
5. News, Portfolio-Simulation, Szenarien und KI-/RL-Labor separat öffnen.
6. „Cache leeren“ testen und anschließend Daten neu laden.

## 5. Git

```powershell
git status
git add .
git commit -m "V7.0 modulare Anwendungsarchitektur"
git push -u origin feature/architecture-v70
```

Anschließend auf GitHub einen Pull Request nach `main` erstellen.

## Architekturänderungen

- `app.py` startet jetzt `stock_explorer.app_runtime`.
- Der Streamlit-Ablauf liegt nicht mehr in `legacy_app.py`.
- Sidebar und Seitenrouting sind eigenständige UI-Module.
- Der Session-State des Aktienuniversums wird durch einen Service verwaltet.
- Allgemeine Ticker-, Zahlen-, Datums- und DataFrame-Helfer liegen im Domain-Modul.
- Doppelte ältere News-/Event-Definitionen wurden entfernt.

`legacy_app.py` bleibt vorerst als Kompatibilitätsschicht für ältere Fachseiten bestehen. Neue Start-, Navigations- oder Session-Logik soll dort nicht mehr ergänzt werden.
