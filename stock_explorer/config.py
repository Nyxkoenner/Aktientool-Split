"""Zentrale, unveränderliche Metadaten der Anwendung."""

from __future__ import annotations

from pathlib import Path

APP_VERSION = "7.2.9"
APP_TITLE = "Aktien Explorer"
BASE_CURRENCY = "EUR"
FEEDBACK_EMAIL = "nykoenner@gmail.com"
LOG_DIR = Path("data/logs")
PILOT_DATA_DIR = Path("data/pilot")

__all__ = [
    "APP_VERSION",
    "APP_TITLE",
    "BASE_CURRENCY",
    "FEEDBACK_EMAIL",
    "LOG_DIR",
    "PILOT_DATA_DIR",
]
