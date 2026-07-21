# Aktien Explorer V7.2.2

V6.5 erweitert die Portfolio-Simulation um ein echtes, ereignisbasiertes
Transaktionsmodell. Die bisherige Gewichtungssimulation bleibt als zweiter Modus
weiterhin verfügbar.


## UX-Grundlage V7.2.2

Die Oberfläche unterstützt drei Wissensmodi: **Einsteiger**, **Fortgeschritten**
und **Experte**. Die Auswahl verändert Erklärungen, Hilfetexte und empfohlene
Arbeitsschritte, nicht die zugrunde liegenden Berechnungen. Der bestehende
Funktionsumfang bleibt vollständig verfügbar.

Neu hinzugekommen sind:

- seitenspezifische Orientierung passend zum Wissensstand
- ein zweisprachiges, durchsuchbares Börsenlexikon
- kuratierte externe Vertiefungslinks, unter anderem zu Wikipedia
- eine einheitliche Anzeige von Datenstand, Hauptquelle, Abdeckung und Modellgrenzen
- ein globaler Feedback-Bereich mit vorbereiteter E-Mail an `nykoenner@gmail.com`
- datensparsame Feedback-Metadaten ohne automatische Portfolio-, Dokument- oder Modelldaten

Der Feedback-Link öffnet das lokal eingerichtete E-Mail-Programm. Die Nachricht
wird nicht automatisch versendet, sondern erst nach Bestätigung durch den Nutzer.

## Architektur-Release V7.0

V7.0 trennt den Streamlit-Anwendungsablauf von der historischen
Kompatibilitätsschicht. `app.py` startet jetzt `stock_explorer.app_runtime`;
Sidebar, Seitenrouting, Session-State des Aktienuniversums und gemeinsame
Datenhelfer liegen in eigenständigen, getesteten Modulen.

Wichtige neue Grenzen:

- `stock_explorer/app_runtime.py`: Start, Datenladen, Scoring und Seitenaufruf
- `stock_explorer/ui/sidebar.py`: Index-, Filter- und Scanner-Steuerung
- `stock_explorer/ui/page_router.py`: explizite Seitenregistrierung
- `stock_explorer/services/universe_session.py`: zentraler Session-State
- `stock_explorer/domain/value_utils.py`: wiederverwendbare Datenhelfer
- `stock_explorer/legacy_app.py`: nur noch Kompatibilität für ältere Fachseiten

Doppelte ältere News-/Event-Funktionsdefinitionen wurden entfernt. Neue
Anwendungslogik soll nicht mehr in `legacy_app.py` ergänzt werden.

## Stabilität und Laufzeitkontrolle V7.1

Das KI-/RL-Labor zeigt vor dem Start den erwarteten Rechenaufwand. Vier
Laufzeitmodi steuern Historienlänge, Episoden, Testfenster, maximale Fold-Anzahl
und Zeitlimit. Lange Analysen melden ihren Fortschritt nach jedem vollständigen
Walk-forward-Fold. Wird ein Limit erreicht, bleibt ein konsistentes Teilergebnis
erhalten; ein bereits laufender Fold wird nicht mitten im Training abgeschnitten.

Zusätzlich prüft das Labor die verwendete Kurshistorie auf:

- ungültige oder nicht positive Preise
- doppelte Zeitpunkte
- größere Lücken zwischen Geschäftstagen
- zu kurze Historien
- veralteten Datenstand

Vorbereitete Feature- und Walk-forward-Pläne werden zwischengespeichert. Der
Cache kann direkt im Labor geleert werden. Technische Fehler werden in einem
rotierenden lokalen Protokoll unter `data/logs/stock_explorer.log` erfasst. Der
Log-Ordner ist nicht Teil der Git-Versionierung.

## AI-Lab 2.0 und persistente Modelle V7.2

Das KI-/RL-Labor kann nun Q-Learning-Modellversionen pro Aktie lokal unter
`data/ai_models/` speichern. Die Dateien verwenden ein nachvollziehbares,
komprimiertes JSON-Format; unsichere Pickle-Dateien werden nicht verwendet.

Verfügbare Aktionen:

- **vollständig neu trainieren:** erzeugt eine unabhängige neue Modellversion
- **kontrolliert weitertrainieren:** übernimmt die bestehende Q-Tabelle und nutzt
  ausschließlich Übergänge nach dem gespeicherten Datenstand
- **nur auswerten:** misst das gespeicherte Modell ausschließlich auf danach
  hinzugekommenen Handelstagen
- **Versionen vergleichen:** zeigt Datenstand, Zustände, Trainingsumfang und die
  Übereinstimmung der Modellaktionen
- **Version löschen:** entfernt genau die ausgewählte lokale Modelldatei

Vor jedem Nachtraining prüft die App Ticker, Merkmalsdefinition, Modellschema,
Lern-/Kostenparameter, Datenüberlappung und neue Beobachtungen. Episodenzahl und
Zufalls-Seed dürfen für einen neuen Nachtrainingslauf geändert werden; Änderungen
an Zustands-, Lern- oder Kostenparametern erfordern bewusst ein vollständiges
Neutraining. Es findet weder im Hintergrund noch beim App-Start automatisches
Training statt.

Die Walk-forward-Auswertung bleibt von den persistenten Produktionsmodellen
getrennt und ist weiterhin die maßgebliche historische Validierung. Gespeicherte
Modelle und Modellaktionen sind keine Anlage- oder Handelssignale.

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

Der Prüflauf umfasst die automatisierten Tests sowie Ruff, Mypy und Syntaxprüfung.

## Szenario-Engine 2.0

Ab Version 6.6 enthält der Bereich **Szenarien** sektorspezifische Stressmodelle. Die Engine unterscheidet unter anderem Banken, Versicherungen, Immobilien, Technologie, Industrie, Versorger und Energie. Vorgefertigte Szenarien verändern Wachstum, Marge, Finanzierung, Bewertung, Dividende und Währungseffekte transparent.

Die Ausgabe zeigt eine schwache, mittlere und starke Modellbandbreite. Zusätzlich wird die modellhafte Gesamtrendite mit rollierenden historischen Haltedauerrenditen derselben Aktie verglichen. Diese Einordnung ist eine Research-Hilfe und weder Kursziel noch Renditeprognose.

## Geschäftsbericht-Automatisierung

Im Bereich **Unternehmensprofile → Automatische Anreicherung** können nun
textbasierte PDF-, HTML- oder TXT-Berichte hochgeladen und analysiert werden.
Für SEC-gemappte US-Ticker und ADRs kann alternativ der neueste 10-K-, 20-F-
oder 40-F-Bericht direkt aus EDGAR geladen werden.

Die Analyse erkennt heuristisch:

- Geschäftsmodell und relevante Berichtsteile
- wesentliche Risiken, Chancen und Abhängigkeiten
- mögliche Marken und Tochtergesellschaften
- Kandidaten für Geschäftssegmente und Regionen
- Umsatzanteile und Beträge, soweit sie im extrahierten Text eindeutig vorkommen

Kandidaten müssen vor dem Speichern manuell bestätigt werden. Analyse-Snapshots
werden lokal unter `data/company_documents/` gespeichert. Gescannte PDFs benötigen
vor dem Import OCR; die App führt selbst keine OCR aus. Die Ergebnisse ersetzen
keine Prüfung des Originalberichts.

## News- und Eventanalyse 2.0

Ab Version 6.8 enthält der Bereich **News & Events → Analyse 2.0** eine
strukturierte Ereignisintelligenz:

- ähnliche Meldungen mehrerer Quellen werden zu einem Ereigniscluster zusammengeführt
- Nachrichtenton und mögliche Aktienwirkung werden getrennt ausgewiesen
- erweiterte Ereignistypen wie Gewinnwarnung, Prognoseänderung, Dividendenänderung,
  Kapitalerhöhung, Rückkauf, Managementwechsel und Regulierung
- Quellenvertrauen von 0 bis 100 mit Kennzeichnung offizieller, etablierter,
  anbieterseitiger und aggregierter Quellen
- historische Kursreaktionen nach 1, 5 und 20 Handelstagen
- Überrendite gegenüber der Index-Benchmark
- Volatilität und maximaler Rückgang nach dem Ereignis
- lokaler, deduplizierter Ereignisspeicher unter `data/events_database/`
- optionaler, begrenzter Volltextabruf einer einzelnen Primärquelle auf Nutzeraktion

Der lokale Ereignisspeicher enthält nur Titel, kurze Feed-Zusammenfassungen,
Quellenmetadaten und abgeleitete Analysewerte. Vollständige fremde Artikel werden
nicht gespeichert. Ton, Aktienwirkung und Kursreaktion sind Research-Hilfen und
belegen weder Kausalität noch eine zukünftige Entwicklung.

## V6.9 – KI-/Reinforcement-Learning-Labor

Der neue Navigationsbereich **KI-/RL-Labor** vergleicht einfache, nachvollziehbare Regelstrategien mit einem eingebauten Q-Learning-Agenten. Die Analyse verwendet expanding Walk-forward-Fenster: Der Agent wird ausschließlich mit früheren Daten trainiert und anschließend im folgenden Testfenster bewertet.

Verglichen werden:

- Buy-and-Hold
- Momentum-Regel
- Drawdown-Recovery-Regel
- kombinierte Trend-/Recovery-Regel
- Q-Learning-Agent

Das Modul ist bewusst eine Forschungsumgebung und kein Signalgeber. Heutige Value-, Growth-, Momentum-, Safety- oder Deep-Value-Scores werden lediglich als Kontext angezeigt. Ohne historische Point-in-Time-Fundamentaldaten würden diese Werte im Training einen Rückschaufehler erzeugen.

Optional gespeicherte Läufe liegen unter `data/ai_lab/` und werden durch `.gitignore` nicht nach GitHub übertragen.
