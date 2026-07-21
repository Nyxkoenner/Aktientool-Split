"""Zentrale, unveränderliche Metadaten der Anwendung."""

from __future__ import annotations

from pathlib import Path

APP_VERSION = "7.2.6"
APP_TITLE = "Aktien Explorer"
BASE_CURRENCY = "EUR"
FEEDBACK_EMAIL = "nykoenner@gmail.com"
LOG_DIR = Path("data/logs")

__all__ = ["APP_VERSION", "APP_TITLE", "BASE_CURRENCY", "FEEDBACK_EMAIL", "LOG_DIR"]
