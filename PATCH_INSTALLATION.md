# V6.9-Patch installieren

Dieser Patch setzt einen funktionierenden **V6.8-Stand** voraus.

## 1. Branch anlegen

```powershell
git switch main
git pull origin main
git switch -c feature/ai-rl-lab-v69
```

## 2. Dateien kopieren

Streamlit zuerst mit `Strg + C` stoppen. Danach den gesamten Inhalt dieses Patch-Ordners in den bestehenden Projektordner kopieren und vorhandene Dateien ersetzen.

### Ersetzte Dateien

```text
README.md
CHANGELOG.md
.gitignore
stock_explorer/__init__.py
stock_explorer/legacy_app.py
stock_explorer/domain/__init__.py
stock_explorer/services/__init__.py
stock_explorer/ui/__init__.py
stock_explorer/i18n/navigation.py
stock_explorer/i18n/translations.py
```

### Neue Dateien

```text
stock_explorer/domain/ai_features.py
stock_explorer/domain/strategy_backtest.py
stock_explorer/domain/rl_qlearning.py
stock_explorer/services/ai_lab_service.py
stock_explorer/ui/ai_lab.py

tests/test_ai_features_v69.py
tests/test_strategy_backtest_v69.py
tests/test_qlearning_v69.py
tests/test_ai_lab_service_v69.py
tests/test_ai_navigation_i18n_v69.py
```

## 3. Qualitätsprüfung

Neue Pflichtpakete sind nicht erforderlich. Das eingebaute Q-Learning nutzt NumPy und Pandas.

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
```

Der geprüfte Stand liefert:

```text
64 Tests bestanden
Ruff erfolgreich
Mypy erfolgreich
Syntaxprüfung erfolgreich
```

## 4. App starten

```powershell
python -m streamlit run app.py
```

Indexdaten laden und anschließend den neuen Bereich **KI-/RL-Labor** öffnen. Für aussagekräftigere Walk-forward-Tests im Modul die maximale Kurshistorie laden.

## 5. Git

```powershell
git status
git add .
git commit -m "V6.9 KI- und Reinforcement-Learning-Labor"
git push -u origin feature/ai-rl-lab-v69
```

Danach auf GitHub einen Pull Request nach `main` erstellen.

## Wichtige Einordnung

- Das Modul erzeugt keine Anlageempfehlung.
- Es verwendet ausschließlich historische Kursmerkmale für das Training.
- Heutige Fundamental-Scores werden nicht rückwirkend als historische Merkmale verwendet.
- Walk-forward-Ergebnisse können trotzdem überangepasst sein.
- Handelskosten werden modelliert; Steuern, Slippage, Liquidität und Short-Positionen nicht.
- Gespeicherte Läufe liegen lokal unter `data/ai_lab/` und werden nicht nach GitHub übertragen.
