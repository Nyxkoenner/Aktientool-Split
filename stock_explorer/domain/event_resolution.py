from __future__ import annotations

from typing import Any

import pandas as pd

VERIFICATION_PRIORITY = {
    "official": 100,
    "official_ir": 95,
    "manual_confirmed": 85,
    "manual": 85,
    "data_provider": 65,
    "provider": 65,
    "derived": 40,
    "unknown": 10,
}


def verification_score(value: Any) -> int:
    normalized = str(value or "unknown").strip().lower()
    return VERIFICATION_PRIORITY.get(normalized, 10)


def _normalize_title(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def resolve_events(
    events: pd.DataFrame,
    *,
    conflict_tolerance_days: int = 14,
) -> pd.DataFrame:
    if events is None or events.empty:
        return pd.DataFrame(columns=getattr(events, "columns", None))

    result = events.copy()
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result = result.dropna(subset=["date"])
    if not result.empty and getattr(result["date"].dt, "tz", None) is not None:
        result["date"] = result["date"].dt.tz_localize(None)

    for column, default in {
        "ticker_yahoo": "",
        "event_type": "news",
        "title": "",
        "source": "",
        "verification_level": "unknown",
        "verification_score": None,
        "event_status": "",
        "conflict_note": "",
    }.items():
        if column not in result.columns:
            result[column] = default

    calculated_scores = result["verification_level"].map(verification_score)
    existing_scores = pd.to_numeric(result["verification_score"], errors="coerce")
    result["verification_score"] = existing_scores.fillna(calculated_scores).astype(int)
    result["_normalized_title"] = result["title"].map(_normalize_title)
    result["_day"] = result["date"].dt.normalize()

    # Gleichartige Meldungen am selben Tag werden auf die verlässlichste Quelle reduziert.
    result = (
        result.sort_values(["verification_score", "source"], ascending=[False, True])
        .drop_duplicates(
            subset=["ticker_yahoo", "_day", "event_type", "_normalized_title"],
            keep="first",
        )
        .reset_index(drop=True)
    )

    today = pd.Timestamp.now().normalize()
    future = result[result["_day"] >= today]
    for (_, event_type), group in future.groupby(["ticker_yahoo", "event_type"], dropna=False):
        ordered = group.sort_values("_day")
        indices = list(ordered.index)
        for left_position, left_index in enumerate(indices):
            for right_index in indices[left_position + 1 :]:
                delta = abs((result.at[right_index, "_day"] - result.at[left_index, "_day"]).days)
                if delta > conflict_tolerance_days:
                    break
                if delta <= 1:
                    continue
                if str(result.at[left_index, "source"]) == str(result.at[right_index, "source"]):
                    continue
                note = (
                    f"Abweichende {event_type}-Termine: "
                    f"{result.at[left_index, '_day'].strftime('%d.%m.%Y')} "
                    f"({result.at[left_index, 'source']}) vs. "
                    f"{result.at[right_index, '_day'].strftime('%d.%m.%Y')} "
                    f"({result.at[right_index, 'source']})."
                )
                for index in (left_index, right_index):
                    result.at[index, "event_status"] = "prüfen"
                    result.at[index, "conflict_note"] = note

    return (
        result.drop(columns=["_normalized_title", "_day"], errors="ignore")
        .sort_values(["date", "verification_score"], ascending=[True, False])
        .reset_index(drop=True)
    )
