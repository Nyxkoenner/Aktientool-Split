from __future__ import annotations

import ast
from pathlib import Path


def test_streamlit_entry_uses_modular_runtime() -> None:
    source = Path("app.py").read_text(encoding="utf-8")
    assert "from stock_explorer.app_runtime import main" in source
    assert "legacy_app import main" not in source


def test_legacy_module_no_longer_owns_application_main() -> None:
    source = Path("stock_explorer/legacy_app.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    top_level_functions = {node.name for node in module.body if isinstance(node, ast.FunctionDef)}
    assert "main" not in top_level_functions


def test_legacy_duplicate_event_definitions_were_removed() -> None:
    source = Path("stock_explorer/legacy_app.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    names = [node.name for node in module.body if isinstance(node, ast.FunctionDef)]
    for name in (
        "empty_events_frame",
        "news_to_events",
        "persist_events",
        "load_persisted_events",
        "combine_events",
        "_event_type_label",
        "_render_event_table",
        "render_event_calendar",
    ):
        assert names.count(name) == 1
