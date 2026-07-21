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


DEFAULT_KNOWLEDGE_LEVEL = KnowledgeLevel.INTERMEDIATE
KNOWLEDGE_SESSION_KEY = "knowledge_level"


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


__all__ = [
    "DEFAULT_KNOWLEDGE_LEVEL",
    "KNOWLEDGE_SESSION_KEY",
    "KnowledgeLevel",
    "knowledge_level_from_state",
    "normalize_knowledge_level",
    "set_knowledge_level",
]
