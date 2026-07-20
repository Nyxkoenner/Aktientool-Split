from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_HANDLER_MARKER = "_stock_explorer_log_path"


def configure_application_logging(
    directory: Path,
    *,
    level: int = logging.INFO,
    max_bytes: int = 2_000_000,
    backup_count: int = 5,
) -> Path | None:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        path = (directory / "stock_explorer.log").resolve()
        logger = logging.getLogger("stock_explorer")
        logger.setLevel(level)
        logger.propagate = False
        for handler in logger.handlers:
            if getattr(handler, _HANDLER_MARKER, None) == str(path):
                return path
        handler = RotatingFileHandler(
            path,
            maxBytes=max(int(max_bytes), 10_000),
            backupCount=max(int(backup_count), 1),
            encoding="utf-8",
        )
        setattr(handler, _HANDLER_MARKER, str(path))
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
        logger.addHandler(handler)
        logger.info("Application logging initialised")
        return path
    except OSError:
        return None


__all__ = ["configure_application_logging"]
