from __future__ import annotations

import json
import os
import re
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True, slots=True)
class EventDatabaseSnapshot:
    ticker: str
    events: pd.DataFrame
    articles: pd.DataFrame
    saved_at: str


class EventDatabase:
    """Local, append-safe storage for derived event intelligence.

    Only titles, short feed summaries, source metadata and derived classifications
    are stored. Full article bodies are intentionally not persisted.
    """

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_ticker(ticker: str) -> str:
        value = re.sub(r"[^A-Za-z0-9_-]+", "_", str(ticker or "").upper()).strip("_")
        return value or "UNKNOWN"

    def _directory(self, ticker: str) -> Path:
        directory = self.root_dir / self._safe_ticker(ticker)
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @staticmethod
    def _atomic_write_text(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        handle, temp_name = tempfile.mkstemp(prefix=f"{path.stem}_", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(handle, "w", encoding="utf-8", newline="") as stream:
                stream.write(content)
            for attempt in range(5):
                try:
                    os.replace(temp_name, path)
                    return
                except PermissionError:
                    if attempt == 4:
                        raise
                    time.sleep(0.15 * (attempt + 1))
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    @classmethod
    def _write_csv(cls, frame: pd.DataFrame, path: Path) -> None:
        cls._atomic_write_text(path, frame.to_csv(index=False, lineterminator="\n"))

    @staticmethod
    def _read_csv(path: Path) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()

    def save(self, ticker: str, events: pd.DataFrame, articles: pd.DataFrame) -> EventDatabaseSnapshot:
        directory = self._directory(ticker)
        existing_events = self._read_csv(directory / "events.csv")
        existing_articles = self._read_csv(directory / "articles.csv")

        event_frame = events.copy() if events is not None else pd.DataFrame()
        article_frame = articles.copy() if articles is not None else pd.DataFrame()
        if "summary" in event_frame.columns:
            event_frame["summary"] = event_frame["summary"].fillna("").astype(str).str.slice(0, 800)
        if "summary" in article_frame.columns:
            article_frame["summary"] = article_frame["summary"].fillna("").astype(str).str.slice(0, 800)

        combined_events = pd.concat([existing_events, event_frame], ignore_index=True, sort=False)
        if not combined_events.empty:
            subset = [column for column in ["cluster_id"] if column in combined_events.columns]
            if subset:
                combined_events = combined_events.drop_duplicates(subset=subset, keep="last")
            combined_events = combined_events.sort_values("published", ascending=False, na_position="last")

        combined_articles = pd.concat([existing_articles, article_frame], ignore_index=True, sort=False)
        if not combined_articles.empty:
            subset = [
                column for column in ["link", "title", "published"] if column in combined_articles.columns
            ]
            if subset:
                combined_articles = combined_articles.drop_duplicates(subset=subset, keep="last")
            combined_articles = combined_articles.sort_values(
                "published", ascending=False, na_position="last"
            )

        self._write_csv(combined_events, directory / "events.csv")
        self._write_csv(combined_articles, directory / "articles.csv")
        saved_at = datetime.now().isoformat(timespec="seconds")
        metadata: dict[str, Any] = {
            "ticker": str(ticker).upper(),
            "saved_at": saved_at,
            "events": len(combined_events),
            "articles": len(combined_articles),
        }
        self._atomic_write_text(
            directory / "manifest.json",
            json.dumps(metadata, ensure_ascii=False, indent=2),
        )
        return EventDatabaseSnapshot(str(ticker).upper(), combined_events, combined_articles, saved_at)

    def load(self, ticker: str) -> EventDatabaseSnapshot:
        directory = self._directory(ticker)
        events = self._read_csv(directory / "events.csv")
        articles = self._read_csv(directory / "articles.csv")
        saved_at = ""
        manifest = directory / "manifest.json"
        if manifest.exists():
            try:
                saved_at = str(json.loads(manifest.read_text(encoding="utf-8")).get("saved_at", ""))
            except (OSError, json.JSONDecodeError):
                saved_at = ""
        return EventDatabaseSnapshot(str(ticker).upper(), events, articles, saved_at)
