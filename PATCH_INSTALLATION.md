# V7.2.10 – Optionales Feedback per E-Mail

Dieser Patch setzt den funktionierenden Stand **V7.2.9** voraus.

## Ziel

Das Pilot-Feedback wird vereinfacht:

- keine lokale Speicherung des Feedbacktexts
- keine lokale Pilot-Auswertung in der Nutzeroberfläche
- kein Admin-PIN für das Feedback
- keine automatische Übermittlung
- optional vorbereitete E-Mail an `nykoenner@gmail.com`

Der Nutzer füllt Kategorie, Bewertung und Nachricht aus. Anschließend kann er eine
vorbereitete E-Mail in seinem eigenen E-Mail-Programm öffnen, prüfen und freiwillig
absenden. Ohne diesen Klick erhält der Entwickler keine Daten.

## Installation

1. Streamlit mit `Strg + C` stoppen.
2. Den Inhalt dieses Patch-Ordners in das bestehende Projekt kopieren.
3. Vorhandene Dateien ersetzen.
4. Danach ausführen:

```powershell
.\.venv\Scripts\Activate.ps1
python -m ruff check stock_explorer tests app.py --fix
python -m ruff format stock_explorer tests app.py
.\scripts\check.ps1
python -m streamlit run app.py
```

## Manuell testen

1. `Start → Pilot & Feedback` öffnen.
2. Den Reiter `Feedback` öffnen.
3. Kategorie, Bewertung und Nachricht eintragen.
4. `E-Mail vorbereiten` anklicken.
5. Prüfen, dass noch nichts automatisch versendet wurde.
6. Optional `E-Mail an nykoenner@gmail.com öffnen` anklicken.
7. Prüfen, dass Empfänger, App-Version, Bereich, Bewertung und Nachricht im
   E-Mail-Programm vorausgefüllt sind.
8. Prüfen, dass kein Reiter `Pilot-Auswertung` mehr sichtbar ist.

## Git

```powershell
git status --short
git add .
git commit -m "V7.2.10 Optionales Pilot-Feedback per E-Mail"
git push
```
