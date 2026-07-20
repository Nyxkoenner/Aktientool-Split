from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from stock_explorer.domain.market_reaction import compute_market_reactions
from stock_explorer.domain.news_intelligence import cluster_news, source_health_summary

from .event_database import EventDatabase, EventDatabaseSnapshot


@dataclass(frozen=True, slots=True)
class NewsIntelligenceBundle:
    articles: pd.DataFrame
    events: pd.DataFrame
    reactions: pd.DataFrame
    source_summary: pd.DataFrame
    database_snapshot: EventDatabaseSnapshot | None = None


class NewsIntelligenceService:
    def __init__(self, database: EventDatabase | None = None) -> None:
        self._database = database

    @classmethod
    def with_directory(cls, directory: Path) -> "NewsIntelligenceService":
        return cls(EventDatabase(directory))

    def analyze(
        self,
        news: pd.DataFrame,
        *,
        ticker: str,
        price_history: pd.DataFrame | pd.Series | None,
        benchmark_history: pd.DataFrame | pd.Series | None = None,
        persist: bool = False,
    ) -> NewsIntelligenceBundle:
        articles, events = cluster_news(news)
        reactions = compute_market_reactions(events, price_history, benchmark_history)
        if not reactions.empty:
            reaction_columns = [
                column
                for column in reactions.columns
                if column == "cluster_id"
                or column.startswith("return_")
                or column.startswith("benchmark_return_")
                or column.startswith("excess_return_")
                or column
                in {
                    "reaction_trade_date",
                    "volatility_before_20d",
                    "volatility_after_20d",
                    "max_drawdown_after_20d",
                }
            ]
            events = events.merge(
                reactions[reaction_columns].drop_duplicates("cluster_id", keep="last"),
                on="cluster_id",
                how="left",
            )
        source_summary = source_health_summary(articles)
        snapshot = None
        if persist and self._database is not None:
            snapshot = self._database.save(ticker, events, articles)
        return NewsIntelligenceBundle(articles, events, reactions, source_summary, snapshot)

    def load(self, ticker: str) -> EventDatabaseSnapshot | None:
        if self._database is None:
            return None
        return self._database.load(ticker)
