from __future__ import annotations

import pandas as pd

from stock_explorer.domain.news_analysis import NewsAnalyzer


def test_short_ticker_without_company_alias_is_not_relevant():
    analyzer = NewsAnalyzer()
    result = analyzer.relevance(
        title="T steigt nach neuer Studie",
        summary="Allgemeine Meldung ohne AT&T-Bezug",
        company_name="AT&T Inc.",
        ticker="T",
        source_kind="search_fallback",
    )
    assert result.is_relevant is False


def test_company_alias_and_finance_context_is_relevant():
    analyzer = NewsAnalyzer()
    result = analyzer.relevance(
        title="AT&T raises guidance after quarterly results",
        summary="The telecom group reports stronger cash flow.",
        company_name="AT&T Inc.",
        ticker="T",
        source_kind="search_fallback",
        extra_aliases=["AT&T"],
    )
    assert result.is_relevant is True
    assert result.score >= 70


def test_mixed_sentiment_is_preserved():
    analyzer = NewsAnalyzer()
    sentiment = analyzer.sentiment(
        "Company beats expectations but cuts guidance",
        "",
    )
    assert sentiment.label == "gemischt"


def test_enrich_deduplicates_titles():
    analyzer = NewsAnalyzer()
    raw = pd.DataFrame(
        [
            {
                "published": "2026-01-02",
                "title": "Alpha raises guidance",
                "summary": "Alpha reports quarterly results",
                "link": "https://example.com/1",
                "source": "A",
                "source_kind": "global",
            },
            {
                "published": "2026-01-01",
                "title": "Alpha raises guidance!",
                "summary": "Alpha reports quarterly results",
                "link": "https://example.com/2",
                "source": "B",
                "source_kind": "global",
            },
        ]
    )
    result = analyzer.enrich(raw, ticker="AAA", company_name="Alpha Inc.")
    assert len(result) == 1
