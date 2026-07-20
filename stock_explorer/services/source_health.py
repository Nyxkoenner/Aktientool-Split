from __future__ import annotations

from typing import Any

import pandas as pd


def source_health_score(row: pd.Series | dict[str, Any]) -> int:
    status = str(row.get("status", "") or "").strip().lower()
    http_status = pd.to_numeric(row.get("http_status"), errors="coerce")
    entries = pd.to_numeric(row.get("entries"), errors="coerce")
    matches = pd.to_numeric(row.get("matches"), errors="coerce")

    score = 20
    if pd.notna(http_status) and 200 <= int(http_status) <= 299:
        score += 35
    elif pd.notna(http_status) and int(http_status) >= 400:
        score -= 20

    if status in {"ok", "bestätigt", "anbieterangabe"}:
        score += 25
    elif "keine" in status or "nicht konfiguriert" in status or "nur link" in status:
        score += 5
    elif "fehler" in status:
        score -= 20

    if pd.notna(entries) and float(entries) > 0:
        score += 10
    if pd.notna(matches) and float(matches) > 0:
        score += 10
    return max(0, min(100, int(score)))


def health_label(score: int) -> str:
    if score >= 80:
        return "stabil"
    if score >= 55:
        return "eingeschränkt"
    return "kritisch"


def enrich_diagnostics(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame(columns=getattr(frame, "columns", None))
    result = frame.copy()
    result["health_score"] = result.apply(source_health_score, axis=1)
    result["health_label"] = result["health_score"].map(health_label)
    return result
