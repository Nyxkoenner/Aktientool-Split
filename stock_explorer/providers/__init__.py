"""Austauschbare Datenprovider des Aktien Explorers.

Konkrete Provider werden bewusst nicht pauschal importiert. Dadurch bleiben
optionale Abhängigkeiten voneinander entkoppelt und Tests können einzelne
Provider isoliert laden.
"""

from .base import MarketDataProvider

__all__ = ["MarketDataProvider"]
