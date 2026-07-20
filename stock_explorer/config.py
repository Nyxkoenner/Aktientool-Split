"""Zentrale, unveränderliche Metadaten der Anwendung."""

from __future__ import annotations

from pathlib import Path

APP_VERSION = "7.1.0"
APP_TITLE = "Aktien Explorer"
BASE_CURRENCY = "EUR"
LOG_DIR = Path("data/logs")

__all__ = ["APP_VERSION", "APP_TITLE", "BASE_CURRENCY", "LOG_DIR"]
