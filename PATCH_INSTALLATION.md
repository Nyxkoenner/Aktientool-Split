# V6.5-Patch installieren

Dieser Patch setzt einen funktionierenden V6.4-Stand voraus.

## 1. Sicherung und Git-Status

```powershell
git status
git switch -c feature/portfolio-simulation-v65
```

Alternativ kannst du vor dem Kopieren einen ZIP-Backup des Projektordners anlegen.

## 2. Dateien kopieren

Kopiere den gesamten Inhalt dieses Patch-Ordners in deinen bestehenden
Projektordner. Bestätige das Ersetzen vorhandener Dateien.

### Zu ersetzen

```text
README.md
CHANGELOG.md
stock_explorer/__init__.py
stock_explorer/legacy_app.py
stock_explorer/providers/fx.py
stock_explorer/ui/portfolio_simulation.py
stock_explorer/i18n/translations.py
```

### Neu anzulegen

```text
stock_explorer/domain/portfolio_ledger.py
stock_explorer/services/portfolio_simulation_service.py
tests/test_portfolio_ledger.py
tests/test_portfolio_simulation_service.py
templates/transactions_v2_template.csv
```

Deine Dateien unter `data/`, `portfolio.csv`, `transactions.csv` und `.venv/`
werden nicht überschrieben.

## 3. Qualitätsprüfung

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\scripts\check.ps1
```

Erwartet werden 34 erfolgreiche Tests sowie Ruff-, Mypy- und Syntaxprüfung.

## 4. App starten

```powershell
python -m streamlit run app.py
```

Öffne danach **Portfolio-Simulation** und wähle **Transaktionsbuch 2.0**.

## 5. Git-Commit

```powershell
git status
git add .
git commit -m "V6.5 Portfolio-Simulation 2.0"
git pull --rebase origin main
git push -u origin feature/portfolio-simulation-v65
```

Nach erfolgreichem Test kannst du den Branch in GitHub nach `main` mergen.

## Transaktionsformat

Die bisherige `data/transactions.csv` bleibt kompatibel. Neu unterstützt werden:

```text
BUY
SELL
DEPOSIT
WITHDRAWAL
DIVIDEND
FEE
SPLIT
```

Für Geldbewegungen kann die optionale Spalte `cash_amount` verwendet werden.
Ohne diese Spalte verwendet die App bei Geldbewegungen aus Kompatibilitätsgründen
`price` als Betrag.
