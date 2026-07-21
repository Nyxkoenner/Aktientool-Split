"""Lokaler, datensparsamer Speicher für Feedback und Pilotereignisse."""

from __future__ import annotations

import csv
import hmac
import io
import json
import secrets
from collections import Counter
from pathlib import Path
from threading import RLock
from typing import Any

from stock_explorer.domain.pilot_models import (
    PilotEvent,
    PilotFeedback,
    PilotSummary,
    normalize_feedback_category,
    normalize_rating,
    safe_event_metadata,
    sanitize_text,
    utc_now_iso,
)

_WRITE_LOCK = RLock()


def build_feedback_reference() -> str:
    """Erzeugt eine kurze, nicht fortlaufende Feedback-Referenz."""
    date_part = utc_now_iso()[:10].replace("-", "")
    return f"FB-{date_part}-{secrets.token_hex(3).upper()}"


def verify_admin_pin(provided: str, configured: str | None) -> bool:
    """Vergleicht Pilot-PINs ohne frühes Abbrechen."""
    expected = str(configured or "")
    candidate = str(provided or "")
    return bool(expected) and hmac.compare_digest(candidate, expected)


class PilotStore:
    """Speichert Pilotdaten als lokal lesbare JSONL-Dateien."""

    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)
        self.feedback_path = self.root_dir / "feedback.jsonl"
        self.events_path = self.root_dir / "events.jsonl"

    @staticmethod
    def _append_json(path: Path, payload: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        with _WRITE_LOCK, path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line + "\n")

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        records: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                candidate = line.strip()
                if not candidate:
                    continue
                try:
                    parsed = json.loads(candidate)
                except json.JSONDecodeError:
                    continue
                if isinstance(parsed, dict):
                    records.append(parsed)
        return records

    def save_feedback(
        self,
        *,
        category: str,
        rating: int,
        message: str,
        contact_email: str,
        page_id: str,
        app_version: str,
        language: str,
        knowledge_level: str,
        display_mode: str,
        session_id: str,
    ) -> PilotFeedback:
        cleaned_message = sanitize_text(message)
        if len(cleaned_message) < 3:
            raise ValueError("Bitte mindestens drei Zeichen Feedback eingeben.")
        cleaned_email = sanitize_text(contact_email, max_length=254)
        feedback = PilotFeedback(
            reference_id=build_feedback_reference(),
            created_at=utc_now_iso(),
            category=normalize_feedback_category(category),
            rating=normalize_rating(rating),
            message=cleaned_message,
            contact_email=cleaned_email,
            page_id=sanitize_text(page_id, max_length=80),
            app_version=sanitize_text(app_version, max_length=40),
            language=sanitize_text(language, max_length=12),
            knowledge_level=sanitize_text(knowledge_level, max_length=40),
            display_mode=sanitize_text(display_mode, max_length=40),
            session_id=sanitize_text(session_id, max_length=64),
        )
        self._append_json(self.feedback_path, feedback.to_dict())
        return feedback

    def save_event(
        self,
        *,
        event_type: str,
        page_id: str,
        app_version: str,
        language: str,
        knowledge_level: str,
        display_mode: str,
        session_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> PilotEvent:
        event = PilotEvent(
            created_at=utc_now_iso(),
            event_type=sanitize_text(event_type, max_length=80),
            page_id=sanitize_text(page_id, max_length=80),
            app_version=sanitize_text(app_version, max_length=40),
            language=sanitize_text(language, max_length=12),
            knowledge_level=sanitize_text(knowledge_level, max_length=40),
            display_mode=sanitize_text(display_mode, max_length=40),
            session_id=sanitize_text(session_id, max_length=64),
            metadata=safe_event_metadata(metadata),
        )
        self._append_json(self.events_path, event.to_dict())
        return event

    def feedback_records(self) -> list[dict[str, Any]]:
        return self._read_jsonl(self.feedback_path)

    def event_records(self) -> list[dict[str, Any]]:
        return self._read_jsonl(self.events_path)

    def summary(self) -> PilotSummary:
        feedback = self.feedback_records()
        events = self.event_records()
        ratings = [
            float(record["rating"]) for record in feedback if isinstance(record.get("rating"), (int, float))
        ]
        categories = Counter(str(record.get("category", "unknown")) for record in feedback)
        pages = Counter(str(record.get("page_id", "unknown")) for record in events)
        return PilotSummary(
            feedback_count=len(feedback),
            event_count=len(events),
            average_rating=(sum(ratings) / len(ratings)) if ratings else None,
            category_counts=dict(categories),
            page_counts=dict(pages),
        )

    def feedback_csv_bytes(self) -> bytes:
        records = self.feedback_records()
        fieldnames = [
            "reference_id",
            "created_at",
            "category",
            "rating",
            "message",
            "contact_email",
            "page_id",
            "app_version",
            "language",
            "knowledge_level",
            "display_mode",
            "session_id",
        ]
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
        return buffer.getvalue().encode("utf-8-sig")


__all__ = [
    "PilotStore",
    "build_feedback_reference",
    "verify_admin_pin",
]
