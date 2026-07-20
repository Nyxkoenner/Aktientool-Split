from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd


@dataclass(slots=True)
class ProviderDiagnostic:
    source: str
    kind: str
    status: str = "Nicht gestartet"
    url: str = ""
    http_status: int | None = None
    content_type: str = ""
    entries: int = 0
    matches: int = 0
    uncertain_matches: int = 0
    duration_ms: int | None = None
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class NewsEntry:
    published: datetime
    title: str
    summary: str
    link: str
    source: str
    source_kind: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class NewsFetchResult:
    entries: list[NewsEntry] = field(default_factory=list)
    diagnostic: ProviderDiagnostic | None = None


@dataclass(slots=True)
class IndexLoadResult:
    frame: pd.DataFrame
    source: str
    as_of: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EventFetchResult:
    events: pd.DataFrame
    diagnostics: pd.DataFrame


@dataclass(slots=True)
class ProfileFetchResult:
    data: dict[str, Any]
    provider_name: str
    warnings: list[str] = field(default_factory=list)
