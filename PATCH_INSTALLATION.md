# V7.2.9 – Einheiten in Analystenschätzungen

Voraussetzung: funktionierender Stand V7.2.8.

Den gesamten Inhalt dieses Patch-Ordners in das Projekt kopieren und vorhandene Dateien ersetzen.

## Änderungen

- Kursziele zeigen jetzt die Kurswährung, zum Beispiel `415,01 EUR`.
- Umsatzschätzungen werden kompakt als Tsd., Mio., Mrd. oder Bio. samt Berichtswährung dargestellt.
- Gewinnschätzungen tragen die Einheit `Währung/Aktie`.
- Wachstumswerte werden als Prozent statt als Dezimalzahl angezeigt.
- Analystenzahlen werden ohne Dezimalstellen dargestellt.
- Analystentabellen erhalten verständlichere deutsche Spaltenüberschriften und einen Einheitenhinweis.

## Prüfung

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\check.ps1
python -m streamlit run app.py
```

Anschließend unter **Unternehmensprofile → Analysten** die Tabs Umsatzschätzungen, Gewinnschätzungen und Wachstum prüfen.
