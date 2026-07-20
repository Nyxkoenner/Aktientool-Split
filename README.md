# Aktien Explorer V6.5

V6.5 erweitert die Portfolio-Simulation um ein echtes, ereignisbasiertes
Transaktionsmodell. Die bisherige Gewichtungssimulation bleibt als zweiter Modus
weiterhin verfügbar.

## Installation

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
python -m streamlit run app.py
```

## Portfolio-Simulation 2.0

Im Bereich **Portfolio-Simulation** stehen nun zwei Modelle zur Verfügung:

1. **Transaktionsbuch 2.0**
   - Käufe und Verkäufe zu ihren tatsächlichen Daten
   - Ein- und Auszahlungen
   - explizite Gebühren
   - zusätzliche Handelskosten in Basispunkten
   - historisch geladene Dividenden
   - optionale Dividenden-Reinvestition
   - Modellsteuer auf Dividenden
   - Cash-Konto
   - historische FX-Umrechnung über den konfigurierten FX-Provider
   - Aktiensplits als Ledger-Ereignis
   - TWR, XIRR, Drawdown, Beiträge, Gebühren und Dividenden
   - Vergleich mit DAX, S&P 500, MSCI-World-ETF oder eigenem Benchmark-Ticker

2. **Gewichtungsmodell**
   - bisheriger Buy-and-Hold-/Rebalancing-Vergleich anhand heutiger Gewichte

## Erweitertes Transaktionsformat

Die bestehende Datei `data/transactions.csv` bleibt kompatibel. Zusätzlich werden
folgende Ereignistypen unterstützt:

```text
BUY
SELL
DEPOSIT
WITHDRAWAL
DIVIDEND
FEE
SPLIT
```

Zusätzliche optionale Spalte:

```text
cash_amount
```

Für `DEPOSIT`, `WITHDRAWAL`, `DIVIDEND` und `FEE` enthält `cash_amount` den
Geldbetrag. Fehlt die Spalte, wird aus Kompatibilitätsgründen `price` als Betrag
verwendet.

Eine Vorlage liegt unter:

```text
templates/transactions_v2_template.csv
```

## Wichtige Modellgrenzen

- Steuerregeln werden nur als frei einstellbare Dividendenquote modelliert.
- Quellensteuer, Verlustverrechnung und individuelle Brokerabrechnungen sind nicht enthalten.
- Kapitalmaßnahmen müssen als Transaktion beziehungsweise Split dokumentiert werden.
- Historische FX- und Dividendeninformationen hängen vom gewählten Datenanbieter ab.
- Die Ergebnisse sind Recherchehilfen und keine steuerliche oder Anlageberatung.

## Qualitätsprüfung

```powershell
.\scripts\check.ps1
```

Der Prüflauf umfasst 34 Tests sowie Ruff, Mypy und Syntaxprüfung.

## Szenario-Engine 2.0

Ab Version 6.6 enthält der Bereich **Szenarien** sektorspezifische Stressmodelle. Die Engine unterscheidet unter anderem Banken, Versicherungen, Immobilien, Technologie, Industrie, Versorger und Energie. Vorgefertigte Szenarien verändern Wachstum, Marge, Finanzierung, Bewertung, Dividende und Währungseffekte transparent.

Die Ausgabe zeigt eine schwache, mittlere und starke Modellbandbreite. Zusätzlich wird die modellhafte Gesamtrendite mit rollierenden historischen Haltedauerrenditen derselben Aktie verglichen. Diese Einordnung ist eine Research-Hilfe und weder Kursziel noch Renditeprognose.
