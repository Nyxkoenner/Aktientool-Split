# Aktien Explorer V6.4

V6.4 führt eine zentrale Deutsch-/Englisch-Umschaltung ein und lagert den
App-Rahmen sowie die sprachunabhängige Navigation aus der großen
`legacy_app.py` aus.

## Installation

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
python -m streamlit run app.py
```

## Sprache umschalten

Die Sprache wird oben in der Sidebar ausgewählt und bleibt bei Streamlit-Reruns
erhalten. Unterstützt werden aktuell:

- Deutsch (`de`)
- English (`en`)

Optional kann die Standardsprache gesetzt werden:

```powershell
$env:AKTIEN_EXPLORER_LANGUAGE="en"
python -m streamlit run app.py
```

## Neue Struktur

```text
stock_explorer/
├── i18n/
│   ├── context.py
│   ├── formatting.py
│   ├── navigation.py
│   └── translations.py
└── ui/
    └── app_shell.py
```

## Bereits vollständig lokalisiert

- App-Kopf und Hauptnavigation
- zentrale Sidebar-Einstellungen
- Datenquellen-Monitor
- Szenario-Engine
- Portfolio-Simulation
- automatische Profilanreicherung
- zentrale Zahlen- und Datumsformatierung der neuen Module

Die älteren, noch nicht aus `legacy_app.py` ausgelagerten Detailansichten bleiben
vorübergehend teilweise deutsch. Das Übersetzungssystem ist so aufgebaut, dass
diese Bereiche in den nächsten Auslagerungsschritten ohne erneute Architekturänderung
umgestellt werden können.

## Stabile Navigation

Im Session State werden keine sichtbaren deutschen oder englischen Labels mehr
gespeichert, sondern stabile Seiten-IDs wie `analysis`, `news` oder `scenarios`.
Dadurch bleibt der aktive Bereich auch beim Sprachwechsel und bei Reruns erhalten.

## Qualitätssicherung

```powershell
.\scripts\check.ps1
```

Der Prüflauf umfasst 29 Tests sowie Ruff, Mypy und Syntaxprüfung. Mypy prüft nun
zusätzlich die Pakete `stock_explorer/i18n` und `stock_explorer/ui`.
