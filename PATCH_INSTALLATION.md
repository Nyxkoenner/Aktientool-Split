# Aktien Explorer V6.7 – Geschäftsbericht- und Profilautomatisierung

Dieser Patch setzt einen funktionierenden Stand **V6.6.1** voraus.

## Installation

1. Streamlit im Terminal mit `Strg + C` stoppen.
2. Das Patch-ZIP entpacken.
3. Den gesamten Inhalt des entpackten Ordners in den bestehenden Projektordner kopieren.
4. Beim Kopieren das Ersetzen vorhandener Dateien bestätigen.
5. Die virtuelle Umgebung aktivieren und Abhängigkeiten aktualisieren:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
python -m streamlit run app.py
```

## Ersetzte Dateien

```text
.gitignore
README.md
CHANGELOG.md
requirements.txt
stock_explorer/__init__.py
stock_explorer/legacy_app.py
stock_explorer/domain/__init__.py
stock_explorer/providers/registry.py
stock_explorer/services/__init__.py
stock_explorer/ui/__init__.py
stock_explorer/i18n/translations.py
```

## Neue Dateien

```text
stock_explorer/domain/report_analysis.py
stock_explorer/providers/annual_reports.py
stock_explorer/services/report_service.py
stock_explorer/ui/annual_report_automation.py

tests/test_report_analysis_v67.py
tests/test_annual_report_provider_v67.py
tests/test_report_service_v67.py
```

## Verwendung

1. Index- und Marktdaten laden.
2. **Unternehmensprofile** öffnen.
3. Eine Aktie auswählen.
4. Den Profilbereich **Automatische Anreicherung** öffnen.
5. Entweder einen textbasierten PDF-/HTML-/TXT-Bericht hochladen oder bei einem SEC-gemappten US-Ticker den neuesten offiziellen Jahresbericht laden.
6. Risiken, Chancen, Abhängigkeiten, Segmente und Regionen am Originalbericht prüfen.
7. Nur bestätigte Segment- oder Regionszeilen speichern.
8. Optional einen Analyse-Snapshot speichern oder qualitative Erkenntnisse ins Unternehmensprofil übernehmen.

## Lokale Speicherung

Analyse-Snapshots werden unter folgendem Pfad gespeichert:

```text
data/company_documents/
```

Dieser Ordner ist in `.gitignore` eingetragen und wird nicht nach GitHub hochgeladen.

Strukturierte Ergebnisse werden weiterhin in diesen Dateien gespeichert:

```text
data/company_profiles.csv
data/company_segments.csv
data/company_regions.csv
```

## Einschränkungen

- Gescannte PDFs benötigen vorher eine OCR-Texterkennung. Die App führt selbst keine OCR aus.
- Tabellen in PDFs werden nicht immer korrekt als Zeilen extrahiert.
- Segment-, Regions- und Risikokandidaten sind heuristisch und müssen am Originaldokument bestätigt werden.
- SEC-Abrufe benötigen eine Kontaktadresse in `SEC_CONTACT_EMAIL`.
- Die Analyse ist eine Recherchehilfe und keine Anlageberatung.

## Git

Empfohlener Branch:

```powershell
git switch main
git pull origin main
git switch -c feature/company-reports-v67
```

Nach erfolgreichem Test:

```powershell
git status
git add .
git commit -m "V6.7 Geschäftsbericht- und Profilautomatisierung"
git push -u origin feature/company-reports-v67
```
