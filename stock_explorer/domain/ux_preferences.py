"""Wissensstufen und Anzeigepräferenzen der Benutzeroberfläche."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Protocol


class SessionStateLike(Protocol):
    """Kleinstes gemeinsames Protokoll für dict und Streamlit Session State."""

    def __contains__(self, key: object) -> bool: ...

    def __getitem__(self, key: str) -> Any: ...

    def __setitem__(self, key: str, value: Any) -> None: ...


class KnowledgeLevel(StrEnum):
    """Darstellungstiefe der Oberfläche."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class DisplayMode(StrEnum):
    """Breiten- und Bedienprofil der Oberfläche."""

    AUTO = "auto"
    COMPACT = "compact"
    DESKTOP = "desktop"


DEFAULT_KNOWLEDGE_LEVEL = KnowledgeLevel.INTERMEDIATE
KNOWLEDGE_SESSION_KEY = "knowledge_level"
DEFAULT_DISPLAY_MODE = DisplayMode.AUTO
DISPLAY_MODE_SESSION_KEY = "display_mode"


def normalize_knowledge_level(value: object) -> KnowledgeLevel:
    """Normalisiert beliebige Eingaben auf eine unterstützte Wissensstufe."""
    candidate = str(value or "").strip().lower()
    try:
        return KnowledgeLevel(candidate)
    except ValueError:
        return DEFAULT_KNOWLEDGE_LEVEL


def knowledge_level_from_state(state: SessionStateLike | None = None) -> KnowledgeLevel:
    """Liest die aktuelle Wissensstufe aus einem Session-State-ähnlichen Objekt."""
    if state is not None and KNOWLEDGE_SESSION_KEY in state:
        return normalize_knowledge_level(state[KNOWLEDGE_SESSION_KEY])
    return DEFAULT_KNOWLEDGE_LEVEL


def set_knowledge_level(
    level: KnowledgeLevel | str,
    state: SessionStateLike,
) -> KnowledgeLevel:
    """Speichert eine normalisierte Wissensstufe."""
    selected = normalize_knowledge_level(level)
    state[KNOWLEDGE_SESSION_KEY] = selected.value
    return selected


def normalize_display_mode(value: object) -> DisplayMode:
    """Normalisiert eine Anzeigeauswahl auf einen unterstützten Modus."""
    candidate = str(value or "").strip().lower()
    try:
        return DisplayMode(candidate)
    except ValueError:
        return DEFAULT_DISPLAY_MODE


def display_mode_from_state(state: SessionStateLike | None = None) -> DisplayMode:
    """Liest den Anzeigemodus aus einem Session-State-ähnlichen Objekt."""
    if state is not None and DISPLAY_MODE_SESSION_KEY in state:
        return normalize_display_mode(state[DISPLAY_MODE_SESSION_KEY])
    return DEFAULT_DISPLAY_MODE


def set_display_mode(
    mode: DisplayMode | str,
    state: SessionStateLike,
) -> DisplayMode:
    """Speichert einen normalisierten Anzeigemodus."""
    selected = normalize_display_mode(mode)
    state[DISPLAY_MODE_SESSION_KEY] = selected.value
    return selected


__all__ = [
    "DEFAULT_DISPLAY_MODE",
    "DEFAULT_KNOWLEDGE_LEVEL",
    "DISPLAY_MODE_SESSION_KEY",
    "KNOWLEDGE_SESSION_KEY",
    "DisplayMode",
    "KnowledgeLevel",
    "display_mode_from_state",
    "knowledge_level_from_state",
    "normalize_display_mode",
    "normalize_knowledge_level",
    "set_display_mode",
    "set_knowledge_level",
]
