# Aktien Explorer V7.2.2 – UX-Grundlage

Dieser Patch setzt einen funktionierenden Stand **V7.2.1** voraus.

## Installation

1. Streamlit mit `Strg + C` stoppen.
2. Optional einen neuen Git-Branch anlegen:

```powershell
git switch main
git pull --ff-only origin main
git switch -c feature/ux-foundation-v722
```

3. Den gesamten Inhalt dieses Patch-Ordners in den bestehenden Projektordner kopieren.
4. Vorhandene Dateien ersetzen, die Verzeichnisstruktur beibehalten.
5. Virtuelle Umgebung aktivieren und prüfen:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
python -m streamlit run app.py
```

Neue Python-Abhängigkeiten werden nicht benötigt.

## Neu in V7.2.2

- Wissensmodus **Einsteiger**, **Fortgeschritten** oder **Experte**
- getrennte Widget- und Anwendungs-Session-Keys zur Vermeidung von Streamlit-State-Fehlern
- seitenspezifische Erklärungen und empfohlene nächste Schritte
- zweisprachiges, durchsuchbares Börsenlexikon
- kuratierte externe Vertiefungslinks, unter anderem zu Wikipedia
- einheitliche Anzeige von Datenstand, Hauptquelle, Abdeckung und Modellgrenzen
- globaler Feedback-Bereich an `nykoenner@gmail.com`
- App- und Paketversion `7.2.2`

Der Wissensmodus verändert zunächst Erklärungen und Hilfen, nicht die fachlichen Berechnungen oder die verfügbaren Seiten. Die stärkere Reduzierung und Gruppierung der Navigation ist für den nächsten UX-Schritt vorgesehen.

## Feedback-Funktion

Der Feedback-Bereich öffnet das lokal eingerichtete E-Mail-Programm mit einer vorbereiteten Nachricht. Die Mail wird nicht automatisch versendet.

Automatisch eingetragen werden nur:

- App-Version
- aktueller Bereich
- Sprache
- Wissensmodus
- Feedback-Kategorie

Portfolio-, Dokument-, Modell- oder andere persönliche Daten werden nicht automatisch angehängt.

## Neue Dateien

```text
stock_explorer/content/__init__.py
stock_explorer/content/glossary.py
stock_explorer/content/page_guides.py
stock_explorer/domain/ux_preferences.py
stock_explorer/i18n/ux_translations.py
stock_explorer/ui/ux_foundation.py

tests/test_feedback_v722.py
tests/test_glossary_v722.py
tests/test_page_guides_v722.py
tests/test_ux_i18n_v722.py
tests/test_ux_preferences_v722.py
```

## Ersetzte Dateien

```text
README.md
CHANGELOG.md
stock_explorer/__init__.py
stock_explorer/app_runtime.py
stock_explorer/config.py
stock_explorer/i18n/translations.py
stock_explorer/ui/__init__.py
tests/test_version_consistency_v721.py
```

## Manueller Kurztest

1. Sprache zwischen Deutsch und Englisch wechseln.
2. Alle drei Wissensmodi auswählen.
3. Prüfen, ob die Erklärung oberhalb einer Fachseite ihren Detailgrad ändert.
4. Im Börsenlexikon nach `KGV`, `Drawdown` und `Cashflow` suchen.
5. Einen externen Lernlink öffnen.
6. Feedback-Kategorie und Nachricht eingeben und kontrollieren, ob das E-Mail-Programm mit `nykoenner@gmail.com` geöffnet wird.
7. Daten laden und den Bereich **Daten, Quellen und Annahmen** öffnen.

## Git

```powershell
git status
git add .
git commit -m "V7.2.2 UX-Grundlage mit Wissensmodus und Feedback"
git push -u origin feature/ux-foundation-v722
```

Danach den Pull Request nach `main` mergen.
