from __future__ import annotations

import sys
from pathlib import Path

import pytest


@pytest.mark.skipif(
    sys.version_info >= (3, 12),
    reason="Der Kompatibilitaetstest ist fuer Python 3.11 und aelter bestimmt.",
)
def test_all_project_sources_compile_with_supported_legacy_python() -> None:
    paths = [Path("app.py"), *Path("stock_explorer").rglob("*.py")]
    for path in paths:
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")
