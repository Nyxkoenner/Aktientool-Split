from __future__ import annotations

import logging
from pathlib import Path

from stock_explorer.services.app_logging import configure_application_logging


def test_rotating_application_log_is_created_without_duplicate_handler(tmp_path: Path) -> None:
    path = configure_application_logging(tmp_path)
    duplicate = configure_application_logging(tmp_path)

    assert path is not None
    assert duplicate == path
    logging.getLogger("stock_explorer.test").warning("test warning")
    for handler in logging.getLogger("stock_explorer").handlers:
        handler.flush()
    assert path.exists()
    assert "test warning" in path.read_text(encoding="utf-8")
