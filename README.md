# Aktien Explorer V6.2

V6.2 setzt die modulare Umstellung fort. Markt-, Index-, FX-, News-, Event-,
SEC- und Profilquellen sind jetzt über klar getrennte Provider und Services
angebunden. Die bestehende Streamlit-Oberfläche bleibt dabei erhalten.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
.\scripts\check.ps1
python -m streamlit run app.py
```

## Neue Struktur

```text
stock_explorer/
├── providers/
│   ├── base.py
│   ├── company_profiles.py
│   ├── events.py
│   ├── fx.py
│   ├── http.py
│   ├── indexes.py
│   ├── models.py
│   ├── news.py
│   ├── registry.py
│   ├── sec.py
│   └── yahoo.py
├── services/
│   ├── event_service.py
│   ├── index_service.py
│   ├── news_service.py
│   └── profile_service.py
├── domain/
├── ui/
└── legacy_app.py
```

## Was bereits über Provider läuft

- Marktdaten und Dividenden: Yahoo-Market-Provider
- Wechselkurse: eigenständiger FX-Provider
- Indexbestandteile: CSV-/Offline-/S&P-Provider
- RSS- und Google-News-Transport: News-Provider
- SEC-Unternehmensmapping und Filings: SEC-Provider
- Yahoo-Kalender und manuelle Termine: Event-Provider
- Ownership-, Analysten- und Governance-Daten: Profil-Provider

Die Firmenzuordnung, Sentimentlogik und Ereignisklassifikation bleiben vorerst
in der Fachlogik der Bestands-App. In V6.3 werden auch diese Bestandteile weiter
aus `legacy_app.py` herausgezogen.

## Anbieter konfigurieren

```powershell
$env:AKTIEN_EXPLORER_MARKET_PROVIDER="yahoo"
$env:AKTIEN_EXPLORER_FX_PROVIDER="yahoo"
$env:AKTIEN_EXPLORER_PROFILE_PROVIDER="yahoo"
$env:AKTIEN_EXPLORER_SEC_PROVIDER="sec_edgar"
$env:SEC_CONTACT_EMAIL="deine-email@example.com"
```

## Qualitätssicherung

```powershell
.\scripts\check.ps1
```

Der Prüflauf umfasst Pytest, Ruff, Mypy und die Syntaxprüfung der bestehenden
Streamlit-App. In V6.2 sind zwölf Kern- und Provider-Tests enthalten.

## Git

```powershell
git add .
git commit -m "V6.2 modulare Datenprovider und Services"
git push
git tag -a v6.2.0 -m "Modulare News-, Event-, Index-, FX-, SEC- und Profilprovider"
git push origin v6.2.0
```

## Nächste Schritte

- V6.3: News-/Event-Fachlogik und Profilautomatisierung weiter auslagern
- V6.4: vollständige Sprachumschaltung
- V6.5: Portfolio-Simulation 2.0
- V6.6: KI-/RL-Labor
