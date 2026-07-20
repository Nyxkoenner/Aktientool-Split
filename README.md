# Aktien Explorer V6.3

V6.3 bindet die modularen News-, Event- und Profilanbieter vollständig in die
Oberfläche ein. Firmenzuordnung, Sentiment, Ereignisklassifikation und
Quellenpriorisierung liegen nicht mehr ausschließlich in der großen
`legacy_app.py`.

## Installation

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
python -m streamlit run app.py
```

## Neue Module

```text
stock_explorer/
├── domain/
│   ├── event_resolution.py
│   └── news_analysis.py
├── providers/
│   ├── ir.py
│   └── sec_companyfacts.py
├── services/
│   └── source_health.py
└── ui/
    ├── profile_automation.py
    └── source_monitor.py
```

## Datenquellen-Monitor

Der neue Hauptbereich **Datenquellen** prüft für ein ausgewähltes Unternehmen:

- globale RSS- und Google-News-Quellen,
- Yahoo-, SEC-, manuelle und Unternehmens-IR-Ereignisse,
- Yahoo- und SEC-Profilanreicherung,
- HTTP-Status, Treffer, Laufzeit und Quellen-Gesundheit.

## Offizielle IR-Quellen

Die Datei `data/ir_sources.csv` unterstützt diese Spalten:

```csv
ticker_yahoo,source_name,source_type,feed_url,source_url,verification_level,enabled,notes
```

Mögliche `source_type`-Werte:

- `rss` oder `atom`
- `ics`
- `web` als reiner Referenzlink

Beispiel:

```csv
SAP.DE,SAP Investor Relations,ics,https://example.com/calendar.ics,https://www.sap.com/investors,official_ir,true,
```

## Automatische Unternehmensprofile

Für SEC-gemappte US-Ticker ohne Börsensuffix ergänzt V6.3 offizielle Company
Facts, unter anderem:

- Umsatz,
- Nettoergebnis,
- operativen Cashflow,
- Investitionen,
- Free Cashflow,
- Vermögen und Verbindlichkeiten,
- Finanzschulden,
- gezahlte Dividenden.

Für deutsche und viele andere Nicht-US-Listings bleibt Yahoo die automatische
Quelle; Segmente, Regionen und qualitative Angaben können weiterhin lokal
gepflegt werden.

## Provider konfigurieren

```powershell
$env:AKTIEN_EXPLORER_MARKET_PROVIDER="yahoo"
$env:AKTIEN_EXPLORER_FX_PROVIDER="yahoo"
$env:AKTIEN_EXPLORER_PROFILE_PROVIDER="yahoo_sec"
$env:AKTIEN_EXPLORER_SEC_PROVIDER="sec_edgar"
$env:SEC_CONTACT_EMAIL="deine-email@example.com"
```

## Qualitätssicherung

```powershell
.\scripts\check.ps1
```

Der aktuelle Prüflauf umfasst 24 Tests sowie Ruff, Mypy und Syntaxprüfung.
