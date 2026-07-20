# V7.2 – AI-Lab 2.0 und persistente Modelle

Dieser Patch setzt einen funktionierenden **V7.1-Stand** inklusive der bereits
angewendeten Python-3.11-, Mypy-/NumPy- und Ruff-Fixes voraus.

## Inhalt

V7.2 ergänzt das KI-/RL-Labor um lokale, versionierte Q-Learning-Modelle pro
Aktie. Es findet weiterhin **kein automatisches Hintergrundtraining** statt.

Neue Modellaktionen:

- vollständig neues Modell trainieren
- gespeichertes Modell laden
- kontrolliert nur mit neuen Marktübergängen weitertrainieren
- gespeichertes Modell ausschließlich auf danach hinzugekommenen Daten auswerten
- zwei Modellversionen anhand ihrer Aktionspolitik und Metadaten vergleichen
- einzelne Modellversion dauerhaft löschen

Modelle werden als komprimierte JSON-Dateien gespeichert:

```text
data/ai_models/<TICKER>/*.json.gz
```

Der Ordner wird durch `.gitignore` nicht nach GitHub übertragen. Es werden keine
Pickle-Dateien verwendet.

## Dateien kopieren

Den vollständigen Inhalt des Patchordners in den Projektordner kopieren und
vorhandene Dateien ersetzen.

### Ersetzte Dateien

```text
.gitignore
README.md
CHANGELOG.md
stock_explorer/__init__.py
stock_explorer/domain/__init__.py
stock_explorer/domain/rl_qlearning.py
stock_explorer/i18n/translations.py
stock_explorer/services/__init__.py
stock_explorer/ui/ai_lab.py
```

### Neue Dateien

```text
stock_explorer/services/ai_model_store.py
tests/test_qlearning_persistence_v72.py
tests/test_ai_model_store_v72.py
tests/test_ai_model_i18n_v72.py
```

## Installation und Prüfung

Neue Python-Pakete sind nicht erforderlich.

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\check.ps1
python -m streamlit run app.py
```

## Manueller Kurztest

1. Index- und Marktdaten laden.
2. `KI-/RL-Labor` öffnen und eine Aktie auswählen.
3. Für den ersten Test den Laufzeitmodus `Schnell` verwenden.
4. Unter `Persistente Q-Learning-Modelle` ein Modell vollständig trainieren.
5. App neu starten und prüfen, ob die Modellversion weiterhin auswählbar ist.
6. Ein zweites Modell mit einem anderen Seed oder einer anderen Episodenzahl
   vollständig trainieren und beide Versionen vergleichen.
7. Eine Testversion über den bestätigten Löschdialog entfernen.

`Weitertrainieren` und `Nur auf neuen Daten auswerten` sind absichtlich erst
aktiv, wenn Kurspunkte nach dem gespeicherten Datenstand vorhanden sind. Eine
Änderung von Lernrate, Diskontfaktor, Exploration, Handelskosten oder
Downside-Strafe macht ein gespeichertes Modell inkompatibel und erfordert ein
vollständiges Neutraining. Episodenzahl und Seed dürfen beim Nachtraining
abweichen.

## Git

```powershell
git status
git add .
git commit -m "V7.2 AI-Lab 2.0 und persistente Modelle"
git push -u origin feature/ai-models-v72
```

Danach den Pull Request nach `main` mergen.
