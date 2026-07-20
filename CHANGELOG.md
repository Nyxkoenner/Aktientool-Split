# Changelog

## V6.0.1

- Ruff-Zielversion auf Python 3.13 aktualisiert.
- Mypy-Zielversion auf Python 3.13 aktualisiert; damit sind aktuelle NumPy-Stubs kompatibel.
- Importreihenfolge und öffentliche Re-Exports bereinigt.
- Typfehler in Yahoo-FX-Umrechnung, Provider-Registry und optionaler RL-Umgebung korrigiert.
- `check.ps1` bricht nun zuverlässig beim ersten fehlgeschlagenen Prüfschritt ab.
- Formatprüfung und Syntaxprüfung der großen Bestands-App ergänzt.
- `legacy_app.py` bewusst als Übergangsdatei von Ruff/Mypy ausgenommen; Syntax wird weiter geprüft.
