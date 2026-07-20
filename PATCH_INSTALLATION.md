# V6.6.1 – Sprachwahl-/Session-State-Fix

Dieser Mini-Patch behebt den Streamlit-Fehler:

```text
st.session_state.app_language cannot be modified after the widget with key app_language is instantiated
```

## Dateien kopieren

Kopiere den Inhalt dieses Patch-Ordners in deinen bestehenden Projektordner.

Ersetzen:

```text
stock_explorer/ui/app_shell.py
```

Neu hinzufügen:

```text
tests/test_language_selector_state.py
```

## Danach prüfen

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\check.ps1
python -m streamlit run app.py
```

Die Selectbox verwendet jetzt den eigenen Widget-Key `app_language_selector`. Die aktive Anwendungssprache bleibt separat unter `app_language` gespeichert.
