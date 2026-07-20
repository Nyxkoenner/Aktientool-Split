from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from stock_explorer.domain.news_intelligence import assess_stock_impact, classify_detailed_event
from stock_explorer.i18n import current_language, t
from stock_explorer.providers.article_text import ArticleTextProvider
from stock_explorer.services.news_intelligence_service import NewsIntelligenceBundle, NewsIntelligenceService

EVENT_LABELS: dict[str, dict[str, str]] = {
    "de": {
        "news": "Allgemeine Nachricht",
        "earnings": "Quartals-/Jahreszahlen",
        "guidance_up": "Prognose angehoben",
        "guidance_down": "Prognose gesenkt",
        "profit_warning": "Gewinnwarnung",
        "analyst_upgrade": "Analysten-Upgrade",
        "analyst_downgrade": "Analysten-Downgrade",
        "dividend_increase": "Dividende erhöht",
        "dividend_cut": "Dividende gekürzt",
        "buyback": "Aktienrückkauf",
        "m_and_a": "Übernahme / Beteiligung",
        "management_change": "Managementwechsel",
        "legal_regulatory": "Recht / Regulierung",
        "layoffs": "Stellenabbau",
        "product_approval": "Produktzulassung",
        "capital_raise": "Kapitalerhöhung",
        "refinancing": "Refinanzierung",
        "insider_transaction": "Insidertransaktion",
        "sec_filing": "SEC-Filing",
        "annual_meeting": "Hauptversammlung",
        "capital_markets_day": "Kapitalmarkttag",
        "report": "Bericht",
    },
    "en": {
        "news": "General news",
        "earnings": "Quarterly / annual results",
        "guidance_up": "Guidance raised",
        "guidance_down": "Guidance lowered",
        "profit_warning": "Profit warning",
        "analyst_upgrade": "Analyst upgrade",
        "analyst_downgrade": "Analyst downgrade",
        "dividend_increase": "Dividend increase",
        "dividend_cut": "Dividend cut",
        "buyback": "Share buyback",
        "m_and_a": "M&A / investment",
        "management_change": "Management change",
        "legal_regulatory": "Legal / regulatory",
        "layoffs": "Layoffs",
        "product_approval": "Product approval",
        "capital_raise": "Capital raise",
        "refinancing": "Refinancing",
        "insider_transaction": "Insider transaction",
        "sec_filing": "SEC filing",
        "annual_meeting": "Annual meeting",
        "capital_markets_day": "Capital markets day",
        "report": "Report",
    },
}


def _event_label(value: Any, language: str) -> str:
    return EVENT_LABELS.get(language, EVENT_LABELS["de"]).get(str(value or "news"), str(value or "news"))


def _percent(value: Any) -> str:
    number = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return "–" if pd.isna(number) else f"{float(number):+.2f} %"


def _styled_events(
    frame: pd.DataFrame,
    *,
    impact_column: str,
    trust_column: str,
    excess_column: str,
) -> pd.io.formats.style.Styler:
    def impact_style(value: Any) -> str:
        label = str(value or "").lower()
        if label == "positiv":
            return "color:#16a34a;font-weight:700"
        if label == "negativ":
            return "color:#dc2626;font-weight:700"
        if label == "gemischt":
            return "color:#ca8a04;font-weight:700"
        return "color:#64748b"

    def return_style(value: Any) -> str:
        number = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
        if pd.isna(number):
            return ""
        return "color:#16a34a" if float(number) > 0 else "color:#dc2626" if float(number) < 0 else ""

    styled = frame.style.format(
        {
            trust_column: "{:.0f}",
            "1T": lambda value: _percent(value),
            "5T": lambda value: _percent(value),
            "20T": lambda value: _percent(value),
            excess_column: lambda value: _percent(value),
        },
        na_rep="–",
    )
    if impact_column in frame.columns:
        styled = styled.map(impact_style, subset=[impact_column])
    return styled.map(
        return_style,
        subset=[column for column in ["1T", "5T", "20T", excess_column] if column in frame.columns],
    )


def _render_article_excerpt(
    cluster_id: str,
    title: str,
    link: str,
    article_provider: ArticleTextProvider,
) -> None:
    language = current_language()
    state_key = f"article_text::{cluster_id}"
    if st.button(t("news_v2.fulltext.load", language), key=f"load_article_text::{cluster_id}"):
        with st.spinner(t("news_v2.fulltext.loading", language)):
            st.session_state[state_key] = article_provider.fetch(link)

    result = st.session_state.get(state_key)
    if result is None:
        return
    if result.status != "OK":
        st.warning(f"{result.status}: {result.message}")
        return

    impact = assess_stock_impact(title, result.text)
    event_type = classify_detailed_event(title, result.text)
    columns = st.columns(3)
    columns[0].metric(t("news_v2.fulltext.chars", language), f"{result.chars:,}")
    columns[1].metric(t("news_v2.column.event", language), _event_label(event_type, language))
    columns[2].metric(t("news_v2.column.impact", language), impact.label.capitalize())
    st.caption(impact.reason)
    with st.expander(t("news_v2.fulltext.excerpt", language), expanded=False):
        st.text(result.text[:5_000])
    st.caption(t("news_v2.fulltext.notice", language))


def render_news_intelligence(
    news: pd.DataFrame,
    *,
    ticker: str,
    price_history: pd.DataFrame | pd.Series | None,
    benchmark_history: pd.DataFrame | pd.Series | None,
    benchmark_label: str,
    database_dir: Path,
    article_provider: ArticleTextProvider,
) -> NewsIntelligenceBundle:
    language = current_language()
    service = NewsIntelligenceService.with_directory(database_dir)
    bundle = service.analyze(
        news,
        ticker=ticker,
        price_history=price_history,
        benchmark_history=benchmark_history,
        persist=False,
    )

    st.markdown(f"### {t('news_v2.title', language)}")
    st.caption(t("news_v2.caption", language, benchmark=benchmark_label))
    if bundle.events.empty:
        st.info(t("news_v2.no_events", language))
        return bundle

    official_count = int((pd.to_numeric(bundle.events["source_trust_score"], errors="coerce") >= 90).sum())
    reaction_count = int(pd.to_numeric(bundle.events.get("return_5d"), errors="coerce").notna().sum())
    negative_count = int(bundle.events["impact_label"].astype(str).eq("negativ").sum())
    columns = st.columns(4)
    columns[0].metric(t("news_v2.metric.clusters", language), len(bundle.events))
    columns[1].metric(t("news_v2.metric.official", language), official_count)
    columns[2].metric(t("news_v2.metric.negative", language), negative_count)
    columns[3].metric(t("news_v2.metric.reactions", language), reaction_count)

    filter_columns = st.columns(4)
    event_options = sorted(bundle.events["event_type"].dropna().astype(str).unique())
    selected_types = filter_columns[0].multiselect(
        t("news_v2.filter.event", language),
        event_options,
        format_func=lambda value: _event_label(value, language),
    )
    selected_impact = filter_columns[1].multiselect(
        t("news_v2.filter.impact", language),
        ["positiv", "negativ", "gemischt", "unklar"],
    )
    min_trust = filter_columns[2].slider(
        t("news_v2.filter.trust", language),
        min_value=0,
        max_value=100,
        value=40,
        step=5,
    )
    multi_source_only = filter_columns[3].checkbox(t("news_v2.filter.multi", language), value=False)

    visible = bundle.events.copy()
    if selected_types:
        visible = visible[visible["event_type"].astype(str).isin(selected_types)]
    if selected_impact:
        visible = visible[visible["impact_label"].astype(str).isin(selected_impact)]
    visible = visible[pd.to_numeric(visible["source_trust_score"], errors="coerce").fillna(0) >= min_trust]
    if multi_source_only:
        visible = visible[pd.to_numeric(visible["source_count"], errors="coerce").fillna(0) >= 2]

    display = pd.DataFrame(
        {
            "Datum": pd.to_datetime(visible["published"], errors="coerce").dt.strftime("%d.%m.%Y"),
            t("news_v2.column.event", language): visible["event_type"].map(
                lambda value: _event_label(value, language)
            ),
            t("news_v2.column.title", language): visible["title"],
            t("news_v2.column.tone", language): visible["tone_label"],
            t("news_v2.column.impact", language): visible["impact_label"],
            t("news_v2.column.trust", language): visible["source_trust_score"],
            t("news_v2.column.sources", language): visible["source_count"],
            "1T": visible.get("return_1d"),
            "5T": visible.get("return_5d"),
            "20T": visible.get("return_20d"),
            t("news_v2.column.excess20", language): visible.get("excess_return_20d"),
        }
    )
    impact_column = t("news_v2.column.impact", language)
    trust_column = t("news_v2.column.trust", language)
    excess_column = t("news_v2.column.excess20", language)
    st.dataframe(
        _styled_events(
            display,
            impact_column=impact_column,
            trust_column=trust_column,
            excess_column=excess_column,
        ),
        use_container_width=True,
        hide_index=True,
    )

    if visible.empty:
        st.info(t("news_v2.filtered_empty", language))
    else:
        labels = {
            str(row["cluster_id"]): (
                f"{pd.Timestamp(row['published']).strftime('%d.%m.%Y')} · "
                f"{_event_label(row['event_type'], language)} · {str(row['title'])[:95]}"
            )
            for _, row in visible.iterrows()
        }
        selected_id = st.selectbox(
            t("news_v2.detail.select", language),
            list(labels),
            format_func=lambda value: labels[value],
        )
        selected = visible.loc[visible["cluster_id"].astype(str).eq(selected_id)].iloc[0]
        with st.container(border=True):
            st.markdown(f"#### {selected['title']}")
            detail_columns = st.columns(4)
            detail_columns[0].metric(
                t("news_v2.column.tone", language), str(selected["tone_label"]).capitalize()
            )
            detail_columns[1].metric(
                t("news_v2.column.impact", language), str(selected["impact_label"]).capitalize()
            )
            detail_columns[2].metric(
                t("news_v2.column.trust", language), f"{float(selected['source_trust_score']):.0f}/100"
            )
            detail_columns[3].metric(t("news_v2.column.sources", language), int(selected["source_count"]))
            st.caption(str(selected.get("impact_reason") or ""))
            st.caption(
                f"{t('news_v2.primary_source', language)}: {selected.get('primary_source', '–')} · "
                f"{selected.get('source_quality', '–')}"
            )
            reaction_columns = st.columns(4)
            reaction_columns[0].metric("1T", _percent(selected.get("return_1d")))
            reaction_columns[1].metric("5T", _percent(selected.get("return_5d")))
            reaction_columns[2].metric("20T", _percent(selected.get("return_20d")))
            reaction_columns[3].metric(
                t("news_v2.column.excess20", language), _percent(selected.get("excess_return_20d"))
            )
            source_articles = bundle.articles[
                bundle.articles["cluster_id"].astype(str).eq(selected_id)
            ].sort_values("source_trust_score", ascending=False)
            with st.expander(t("news_v2.sources_detail", language), expanded=False):
                for source_index, (_, article) in enumerate(source_articles.iterrows()):
                    link = str(article.get("link") or "")
                    st.markdown(
                        f"- **{article.get('source', '–')}** · "
                        f"{float(article.get('source_trust_score', 0)):.0f}/100 · "
                        f"{article.get('source_quality', '–')}"
                    )
                    if link:
                        try:
                            st.link_button(
                                t("news_v2.open_source", language),
                                link,
                                key=f"news_v2_link::{selected_id}::{source_index}",
                            )
                        except TypeError:
                            st.link_button(t("news_v2.open_source", language), link)

            primary_link = str(selected.get("primary_link") or "")
            if primary_link:
                _render_article_excerpt(
                    selected_id,
                    str(selected.get("title") or ""),
                    primary_link,
                    article_provider,
                )

    with st.expander(t("news_v2.source_summary", language), expanded=False):
        st.dataframe(bundle.source_summary, use_container_width=True, hide_index=True)

    if st.button(t("news_v2.database.save", language), key=f"save_news_database::{ticker}"):
        saved = service.analyze(
            news,
            ticker=ticker,
            price_history=price_history,
            benchmark_history=benchmark_history,
            persist=True,
        )
        snapshot = saved.database_snapshot
        if snapshot is not None:
            st.success(
                t(
                    "news_v2.database.saved",
                    language,
                    events=len(snapshot.events),
                    articles=len(snapshot.articles),
                )
            )

    stored = service.load(ticker)
    if stored is not None and stored.saved_at:
        st.caption(
            t(
                "news_v2.database.status",
                language,
                timestamp=stored.saved_at,
                events=len(stored.events),
                articles=len(stored.articles),
            )
        )
    st.caption(t("news_v2.disclaimer", language))
    return bundle


__all__ = ["render_news_intelligence"]
