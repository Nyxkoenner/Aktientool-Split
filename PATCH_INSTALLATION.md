# Aktien Explorer V7.1 – Patch-Installation

Dieser Patch setzt einen funktionierenden **V7.0-Stand** voraus.

## 1. Branch vorbereiten

```powershell
git switch main
git pull --ff-only origin main
git status
git switch -c feature/runtime-control-v71
```

Stoppe eine laufende Streamlit-Sitzung mit `Strg + C`.

## 2. Dateien kopieren

Entpacke die ZIP-Datei und kopiere ihren gesamten Inhalt in den bestehenden
Projektordner. Vorhandene Dateien ersetzen.

Der Patch verändert keine Portfolio-, Transaktions-, Profil- oder
Analyse-Snapshots in `data/`.

## 3. Umgebung und Prüfung

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
python -m streamlit run app.py
```

## 4. Manuell prüfen

1. Index laden und das **KI-/RL-Labor** öffnen.
2. Eine Aktie auswählen und bei Bedarf die maximale Historie laden.
3. Die Modi **Schnell**, **Standard** und **Intensiv** durchschalten.
4. Prüfen, ob Datenqualität, Fold-Anzahl, Trainingsschritte und Laufzeitschätzung erscheinen.
5. Einen schnellen Lauf starten und die Fortschrittsanzeige beobachten.
6. Das Fold-Limit kleiner als die geplante Anzahl setzen und ein Teilergebnis erzeugen.
7. Unter `data/logs/stock_explorer.log` prüfen, ob die lokale Logdatei angelegt wurde.
8. Deutsch und Englisch testen.

## 5. Git-Commit

```powershell
git status
git add .
git commit -m "V7.1 Stabilität und Laufzeitkontrolle"
git push -u origin feature/runtime-control-v71
```

Danach auf GitHub einen Pull Request von `feature/runtime-control-v71` nach
`main` erstellen.

## Hinweise

- Das Zeitlimit wird zwischen vollständigen Walk-forward-Folds geprüft. Ein
  bereits laufender Fold wird sauber beendet.
- Die Laufzeitschätzung ist eine Bandbreite und hängt deutlich von CPU,
  Datenmenge und Hintergrundlast ab.
- `data/logs/` ist in `.gitignore` eingetragen.
