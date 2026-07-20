"""Zentraler Zugriff auf den Session-State des geladenen Aktienuniversums."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import pandas as pd


class SessionStateLike(Protocol):
    def get(self, key: str | int, default: Any = None, /) -> Any: ...

    def __setitem__(self, key: str | int, value: Any) -> None: ...

    def pop(self, key: str | int, default: Any = None, /) -> Any: ...


@dataclass(frozen=True)
class UniverseSnapshot:
    raw_metrics: pd.DataFrame | None
    histories: dict[str, pd.DataFrame]
    errors: list[str]
    selected_constituents: pd.DataFrame
    last_refresh: str
    loaded_tickers: tuple[str, ...]


class UniverseSessionStore:
    """Kapselt Session-State-Schlüssel und Refresh-Entscheidungen."""

    CORE_KEYS = (
        "metrics_raw",
        "histories",
        "loaded_tickers",
        "load_errors",
        "selected_constituents_snapshot",
        "last_refresh",
    )
    EXTENDED_CACHE_KEYS = (
        "portfolio_extra_metrics",
        "portfolio_extra_histories",
        "watchlist_extra_raw_metrics",
        "watchlist_extra_histories",
        "watchlist_load_errors",
        "watchlist_last_refresh",
    )

    def __init__(self, state: SessionStateLike) -> None:
        self._state = state

    def needs_refresh(self, selected_tickers: tuple[str, ...], reload_clicked: bool) -> bool:
        loaded = tuple(self._state.get("loaded_tickers", ()))
        return reload_clicked or loaded != selected_tickers

    def save(
        self,
        *,
        raw_metrics: pd.DataFrame,
        histories: dict[str, pd.DataFrame],
        selected_tickers: tuple[str, ...],
        errors: list[str],
        selected_constituents: pd.DataFrame,
        last_refresh: str,
    ) -> None:
        self._state["metrics_raw"] = raw_metrics
        self._state["histories"] = histories
        self._state["loaded_tickers"] = selected_tickers
        self._state["load_errors"] = errors
        self._state["selected_constituents_snapshot"] = selected_constituents.copy()
        self._state["last_refresh"] = last_refresh

    def snapshot(self, fallback_constituents: pd.DataFrame) -> UniverseSnapshot:
        raw_metrics = self._state.get("metrics_raw")
        if not isinstance(raw_metrics, pd.DataFrame):
            raw_metrics = None

        histories_value = self._state.get("histories", {})
        histories = histories_value if isinstance(histories_value, dict) else {}

        errors_value = self._state.get("load_errors", [])
        errors = [str(error) for error in errors_value] if isinstance(errors_value, list) else []

        selected_value = self._state.get("selected_constituents_snapshot")
        selected = selected_value if isinstance(selected_value, pd.DataFrame) else fallback_constituents

        return UniverseSnapshot(
            raw_metrics=raw_metrics,
            histories=histories,
            errors=errors,
            selected_constituents=selected,
            last_refresh=str(self._state.get("last_refresh", "–")),
            loaded_tickers=tuple(self._state.get("loaded_tickers", ())),
        )

    def clear(self, *, include_extended: bool = True) -> None:
        keys = list(self.CORE_KEYS)
        if include_extended:
            keys.extend(self.EXTENDED_CACHE_KEYS)
        for key in keys:
            self._state.pop(key, None)


__all__ = ["UniverseSessionStore", "UniverseSnapshot"]
