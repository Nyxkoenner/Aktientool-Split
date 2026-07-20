from __future__ import annotations

import pandas as pd

from stock_explorer.providers.indexes import IndexProvider


class IndexService:
    def __init__(self, provider: IndexProvider) -> None:
        self._provider = provider
        self._sources: dict[str, str] = {}

    def load(self, index_name: str) -> pd.DataFrame:
        result = self._provider.load(index_name)
        self._sources[index_name] = result.source
        return result.frame.copy()

    def source_description(self, index_name: str) -> str:
        if index_name in self._sources:
            return self._sources[index_name]
        source_method = getattr(self._provider, "source_description", None)
        if callable(source_method):
            return str(source_method(index_name))
        return self._provider.name
