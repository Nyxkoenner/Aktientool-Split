from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from stock_explorer.domain.news_analysis import primary_query_alias
from stock_explorer.i18n import current_language, t
from stock_explorer.providers.registry import get_event_service, get_news_service, get_profile_service
from stock_explorer.services.source_health import enrich_diagnostics


def _company_options(data: pd.DataFrame) -> tuple[list[str], dict[str, str]]:
    frame = data[["ticker_yahoo", "name"]].dropna(subset=["ticker_yahoo"]).drop_duplicates("ticker_yahoo")
    mapping = frame.set_index("ticker_yahoo")["name"].fillna("").astype(str).to_dict()
    options = sorted(
        frame["ticker_yahoo"].astype(str).tolist(),
        key=lambda ticker: mapping.get(ticker, ticker).casefold(),
    )
    return options, mapping


def _status_badge(value: Any, language: str) -> str:
    label = str(value or "unknown").lower()
    if label in {"stabil", "stable"}:
        return t("sources.health.stable", language)
    if label in {"eingeschränkt", "limited"}:
        return t("sources.health.limited", language)
    return t("sources.health.critical", language)


def render_source_monitor(
    data: pd.DataFrame,
    *,
    global_news_sources: list[dict[str, str]],
    headers: dict[str, str],
    manual_events_path: Path,
    ir_sources_path: Path,
) -> None:
    language = current_language()
    st.subheader(t("sources.title", language))
    st.caption(t("sources.caption", language))
    if data is None or data.empty:
        st.info(t("sources.load_data", language))
        return

    options, mapping = _company_options(data)
    ticker = st.selectbox(
        t("sources.check_company", language),
        options=options,
        format_func=lambda symbol: f"{mapping.get(symbol, symbol)} ({symbol})",
        key="source_monitor_ticker",
    )
    company_name = mapping.get(ticker, ticker)
    news_language = st.radio(
        t("sources.news_language", language),
        ["de", "en"],
        horizontal=True,
        key="source_monitor_locale",
        format_func=lambda value: t(f"language.{value}", language),
    )

    c1, c2, c3 = st.columns(3)
    if c1.button(t("sources.check_news", language), use_container_width=True):
        query = primary_query_alias(company_name, ticker)
        news_service = get_news_service(
            global_sources=global_news_sources,
            headers=headers,
            google_query=f'"{query}"',
            locale=news_language,
        )
        news, diagnostics = news_service.fetch_company_news(
            ticker=ticker,
            company_name=company_name,
            cutoff=datetime.now(timezone.utc) - timedelta(days=90),
            max_items=100,
        )
        st.session_state["source_monitor_news"] = news
        st.session_state["source_monitor_news_diag"] = enrich_diagnostics(diagnostics)
        st.session_state["source_monitor_updated"] = datetime.now().strftime("%d.%m.%Y %H:%M")

    if c2.button(t("sources.check_events", language), use_container_width=True):
        event_service = get_event_service(
            manual_events_path=manual_events_path,
            ir_sources_path=ir_sources_path,
            headers=headers,
        )
        events, diagnostics = event_service.fetch(ticker, company_name, days_back=730, days_forward=730)
        st.session_state["source_monitor_events"] = events
        st.session_state["source_monitor_events_diag"] = enrich_diagnostics(diagnostics)
        st.session_state["source_monitor_updated"] = datetime.now().strftime("%d.%m.%Y %H:%M")

    if c3.button(t("sources.check_profiles", language), use_container_width=True):
        enrichment = get_profile_service().fetch_enrichment(ticker)
        st.session_state["source_monitor_profile"] = enrichment
        st.session_state["source_monitor_updated"] = datetime.now().strftime("%d.%m.%Y %H:%M")

    updated = st.session_state.get("source_monitor_updated")
    if updated:
        st.caption(t("sources.last_check", language, timestamp=updated))

    sections = st.tabs(
        [
            t("sources.tab.news", language),
            t("sources.tab.events", language),
            t("sources.tab.profiles", language),
            t("sources.tab.config", language),
        ]
    )
    with sections[0]:
        diagnostics = st.session_state.get("source_monitor_news_diag", pd.DataFrame())
        news = st.session_state.get("source_monitor_news", pd.DataFrame())
        if diagnostics is None or diagnostics.empty:
            st.info(t("sources.news_not_checked", language))
        else:
            display = diagnostics.copy()
            health_col = t("sources.health", language)
            display[health_col] = display["health_label"].map(lambda value: _status_badge(value, language))
            columns = [
                "source",
                "kind",
                "status",
                health_col,
                "http_status",
                "entries",
                "matches",
                "uncertain_matches",
                "duration_ms",
                "message",
            ]
            st.dataframe(
                display[[column for column in columns if column in display.columns]],
                hide_index=True,
                use_container_width=True,
            )
            st.metric(
                t("sources.relevant_news", language),
                int(news.get("is_relevant", pd.Series(dtype=bool)).fillna(False).sum()),
            )

    with sections[1]:
        diagnostics = st.session_state.get("source_monitor_events_diag", pd.DataFrame())
        events = st.session_state.get("source_monitor_events", pd.DataFrame())
        if diagnostics is None or diagnostics.empty:
            st.info(t("sources.events_not_checked", language))
        else:
            display = diagnostics.copy()
            health_col = t("sources.health", language)
            display[health_col] = display["health_label"].map(lambda value: _status_badge(value, language))
            columns = [
                "source",
                "kind",
                "status",
                health_col,
                "http_status",
                "entries",
                "matches",
                "duration_ms",
                "message",
            ]
            st.dataframe(
                display[[column for column in columns if column in display.columns]],
                hide_index=True,
                use_container_width=True,
            )
            if events is not None and not events.empty:
                event_columns = [
                    "date",
                    "event_type",
                    "title",
                    "source",
                    "verification_level",
                    "verification_score",
                    "event_status",
                    "conflict_note",
                ]
                st.dataframe(
                    events[[column for column in event_columns if column in events.columns]],
                    hide_index=True,
                    use_container_width=True,
                )

    with sections[2]:
        profile = st.session_state.get("source_monitor_profile")
        if not isinstance(profile, dict):
            st.info(t("sources.profiles_not_checked", language))
        else:
            status = profile.get("provider_status", pd.DataFrame())
            if isinstance(status, pd.DataFrame) and not status.empty:
                st.dataframe(status, hide_index=True, use_container_width=True)
            available = []
            for key, value in profile.items():
                if key.startswith("provider_") or key == "errors":
                    continue
                if isinstance(value, pd.DataFrame):
                    state = (
                        t("common.rows", language, count=len(value))
                        if not value.empty
                        else t("common.empty", language)
                    )
                elif isinstance(value, dict):
                    state = (
                        t("common.fields", language, count=len(value))
                        if value
                        else t("common.empty", language)
                    )
                else:
                    state = (
                        t("common.available", language)
                        if value is not None and str(value).strip()
                        else t("common.empty", language)
                    )
                available.append(
                    {
                        "Data area" if language == "en" else "Datenbereich": key,
                        t("common.status", language): state,
                    }
                )
            st.dataframe(pd.DataFrame(available), hide_index=True, use_container_width=True)
            warnings = profile.get("provider_warnings", [])
            if warnings:
                for warning in warnings:
                    st.warning(str(warning))

    with sections[3]:
        st.code(
            "AKTIEN_EXPLORER_MARKET_PROVIDER=yahoo\n"
            "AKTIEN_EXPLORER_FX_PROVIDER=yahoo\n"
            "AKTIEN_EXPLORER_PROFILE_PROVIDER=yahoo_sec\n"
            "AKTIEN_EXPLORER_SEC_PROVIDER=sec_edgar\n"
            "AKTIEN_EXPLORER_LANGUAGE=de",
            language="text",
        )
        st.caption(t("sources.ir_path", language, path=ir_sources_path))
        st.caption(t("sources.manual_path", language, path=manual_events_path))
        st.caption(t("sources.sec_hint", language))
