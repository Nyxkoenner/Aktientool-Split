"""Datenmodelle und Validierung für den geschlossenen UX-Pilot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Final

FEEDBACK_CATEGORIES: Final[tuple[str, ...]] = (
    "bug",
    "idea",
    "question",
    "data",
    "usability",
)
ALLOWED_EVENT_METADATA: Final[frozenset[str]] = frozenset(
    {
        "action",
        "target",
        "result",
        "task_id",
        "source",
    }
)


def utc_now_iso() -> str:
    """Liefert einen stabilen UTC-Zeitstempel ohne Mikrosekunden."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sanitize_text(value: object, *, max_length: int = 4_000) -> str:
    """Entfernt Steuerzeichen und begrenzt lokale Pilottexte."""
    text = str(value or "").replace("\x00", " ").strip()
    return text[:max_length]


def normalize_feedback_category(value: object) -> str:
    candidate = str(value or "").strip().lower()
    return candidate if candidate in FEEDBACK_CATEGORIES else "idea"


def normalize_rating(value: object) -> int:
    try:
        rating = int(str(value))
    except (TypeError, ValueError):
        rating = 0
    if not 1 <= rating <= 5:
        raise ValueError("Die Bewertung muss zwischen 1 und 5 liegen.")
    return rating


def safe_event_metadata(metadata: dict[str, Any] | None) -> dict[str, str]:
    """Übernimmt nur bewusst freigegebene, kurze Telemetrie-Felder."""
    if not metadata:
        return {}
    return {
        key: sanitize_text(value, max_length=120)
        for key, value in metadata.items()
        if key in ALLOWED_EVENT_METADATA and value is not None
    }


@dataclass(frozen=True)
class PilotFeedback:
    reference_id: str
    created_at: str
    category: str
    rating: int
    message: str
    contact_email: str
    page_id: str
    app_version: str
    language: str
    knowledge_level: str
    display_mode: str
    session_id: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PilotEvent:
    created_at: str
    event_type: str
    page_id: str
    app_version: str
    language: str
    knowledge_level: str
    display_mode: str
    session_id: str
    metadata: dict[str, str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PilotSummary:
    feedback_count: int
    event_count: int
    average_rating: float | None
    category_counts: dict[str, int]
    page_counts: dict[str, int]


__all__ = [
    "ALLOWED_EVENT_METADATA",
    "FEEDBACK_CATEGORIES",
    "PilotEvent",
    "PilotFeedback",
    "PilotSummary",
    "normalize_feedback_category",
    "normalize_rating",
    "safe_event_metadata",
    "sanitize_text",
    "utc_now_iso",
]
