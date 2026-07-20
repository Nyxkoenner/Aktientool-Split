from __future__ import annotations

from datetime import datetime

import pandas as pd

from stock_explorer.domain.news_intelligence import (
    assess_source,
    assess_stock_impact,
    classify_detailed_event,
    cluster_news,
)


def _news_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "published": datetime(2026, 1, 10, 8),
                "ticker_yahoo": "TEST",
                "title": "Test AG hebt Prognose nach starkem Quartal an",
                "summary": "Das Unternehmen raises guidance und meldet bessere Margen.",
                "link": "https://example.com/ir/release-1",
                "source": "Test AG Investor Relations",
                "source_kind": "official_ir",
                "sentiment_label": "positiv",
                "event_type": "earnings",
                "relevance_score": 95,
            },
            {
                "published": datetime(2026, 1, 10, 9),
                "ticker_yahoo": "TEST",
                "title": "Test AG raises guidance after strong quarter",
                "summary": "Guidance raised after results.",
                "link": "https://reuters.com/test-guidance",
                "source": "Reuters",
                "source_kind": "global",
                "sentiment_label": "positiv",
                "event_type": "earnings",
                "relevance_score": 93,
            },
        ]
    )


def test_source_trust_prefers_official_and_established_sources() -> None:
    official = assess_source(source="SEC EDGAR", source_kind="sec", link="https://www.sec.gov/a")
    aggregator = assess_source(
        source="Google News", source_kind="search_fallback", link="https://news.google.com/a"
    )
    assert official.score == 100
    assert aggregator.score < official.score


def test_tone_and_stock_impact_are_separate() -> None:
    impact = assess_stock_impact(
        "Company cuts jobs but raises guidance",
        "Cost savings support higher margin expectations.",
        tone_label="negativ",
    )
    assert impact.label in {"positiv", "gemischt"}
    assert classify_detailed_event("Company cuts jobs but raises guidance") == "guidance_up"


def test_duplicate_reports_are_clustered() -> None:
    articles, clusters = cluster_news(_news_frame())
    assert len(articles) == 2
    assert len(clusters) == 1
    assert int(clusters.iloc[0]["source_count"]) == 2
    assert clusters.iloc[0]["event_type"] == "guidance_up"
