"""Modularer Streamlit-Anwendungsablauf für Aktien Explorer V7."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, cast

import pandas as pd
import streamlit as st

from stock_explorer import legacy_app as legacy
from stock_explorer.application import ScannerThresholds, SidebarSelection, selected_tickers
from stock_explorer.config import APP_TITLE, APP_VERSION, BASE_CURRENCY, LOG_DIR
from stock_explorer.i18n import current_language, t
from stock_explorer.services.app_logging import configure_application_logging
from stock_explorer.services.universe_session import UniverseSessionStore
from stock_explorer.ui import (
    render_ai_lab,
    render_header,
    render_language_selector,
    render_main_navigation,
    render_portfolio_simulation,
    render_scenario_engine,
    render_source_monitor,
)
from stock_explorer.ui.page_router import PageRenderer, dispatch_page
from stock_explorer.ui.sidebar import SidebarCallbacks, render_sidebar


def _clear_function_cache(function: Any) -> None:
    clear = getattr(function, "clear", None)
    if callable(clear):
        clear()


def clear_application_cache() -> None:
    """Leert externe Daten-Caches und die davon abhängigen Session-State-Werte."""
    cached_functions = (
        legacy.load_index_constituents,
        legacy.download_price_histories,
        legacy.fetch_ticker_info,
        legacy.fetch_dividends,
        legacy.fetch_news_for_ticker,
        legacy.fetch_news_bundle,
        legacy.fetch_yahoo_calendar_events,
        legacy.fetch_sec_company_map,
        legacy.fetch_sec_filings_events,
        legacy.fetch_registered_ir_events,
        legacy.fetch_benchmark_history,
        legacy.fetch_long_history,
        legacy.fetch_historical_financials,
        legacy.fetch_13f_filing_list,
        legacy.fetch_13f_holdings,
        legacy.fx_to_eur,
    )
    for function in cached_functions:
        _clear_function_cache(function)
    UniverseSessionStore(cast(Any, st.session_state)).clear(include_extended=True)


def _render_sidebar(language: str) -> SidebarSelection:
    callbacks = SidebarCallbacks(
        load_index_constituents=legacy.load_index_constituents,
        index_source_description=legacy.index_source_description,
        clear_application_cache=clear_application_cache,
    )
    with st.sidebar:
        return render_sidebar(
            language=language,
            provider_name=legacy.MARKET_PROVIDER.name,
            index_options=legacy.INDEX_OPTIONS,
            strategy_profiles=legacy.STRATEGY_PROFILES,
            callbacks=callbacks,
        )


def _load_and_score_universe(
    selection: SidebarSelection,
    language: str,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, Any], pd.DataFrame]:
    selected_constituents = selection.selected_constituents()
    ticker_key = selected_tickers(selected_constituents, legacy.clean_ticker)
    store = UniverseSessionStore(cast(Any, st.session_state))

    if store.needs_refresh(ticker_key, selection.reload_clicked):
        with st.spinner(t("loading.companies", language, count=len(selected_constituents))):
            raw_metrics, histories, errors = legacy.collect_metrics(selected_constituents)
        store.save(
            raw_metrics=raw_metrics,
            histories=histories,
            selected_tickers=ticker_key,
            errors=errors,
            selected_constituents=selected_constituents,
            last_refresh=datetime.now().strftime("%d.%m.%Y %H:%M"),
        )
        if errors:
            st.warning(t("loading.partial", language, errors=" | ".join(errors[:8])))

    snapshot = store.snapshot(selected_constituents)
    if snapshot.raw_metrics is None or snapshot.raw_metrics.empty:
        st.info(t("loading.prompt", language))
        st.stop()

    thresholds = selection.thresholds
    data = legacy.enrich_with_scores(
        snapshot.raw_metrics,
        drawdown_trigger=thresholds.drawdown_trigger,
        payout_max=thresholds.payout_max,
        score_min=thresholds.score_min,
        yield_min=thresholds.yield_min,
    )
    data = legacy.enrich_with_special_situations(data)

    status_summary, status_detail = legacy.build_data_status(
        snapshot.selected_constituents,
        data,
        snapshot.histories,
        snapshot.errors,
        index_name=selection.index_name,
    )
    _render_status_caption(
        status_summary=status_summary,
        last_refresh=snapshot.last_refresh,
        profile_name=selection.profile_name,
        language=language,
    )
    return data, snapshot.histories, status_summary, status_detail


def _render_status_caption(
    *,
    status_summary: dict[str, Any],
    last_refresh: str,
    profile_name: str,
    language: str,
) -> None:
    requested_count = int(status_summary.get("angefragt", 0))
    loaded_count = int(status_summary.get("analysiert", 0))
    coverage = legacy.safe_float(status_summary.get("abdeckung_prozent"))
    coverage_label = legacy.format_percent(coverage, 1) if coverage is not None else "–"
    st.caption(
        t(
            "status.summary",
            language,
            timestamp=last_refresh,
            loaded=loaded_count,
            requested=requested_count,
            coverage=coverage_label,
            profile=profile_name,
            currency=BASE_CURRENCY,
        )
    )


def _portfolio_simulation_page(data: pd.DataFrame, histories: dict[str, pd.DataFrame]) -> None:
    holdings, _, warnings = legacy.portfolio_input()
    for warning in warnings:
        st.warning(warning)
    render_portfolio_simulation(
        data,
        histories,
        holdings,
        transactions_path=legacy.TRANSACTIONS_PATH,
        market_provider=legacy.MARKET_PROVIDER,
        fx_provider=legacy.FX_PROVIDER,
        base_currency=BASE_CURRENCY,
    )


def _routes(
    *,
    data: pd.DataFrame,
    histories: dict[str, pd.DataFrame],
    status_summary: dict[str, Any],
    status_detail: pd.DataFrame,
    selection: SidebarSelection,
) -> dict[str, PageRenderer]:
    thresholds: ScannerThresholds = selection.thresholds

    routes: dict[str, Callable[[], None]] = {
        "overview": lambda: legacy.render_overview(data),
        "data_status": lambda: legacy.render_data_status(status_summary, status_detail, data),
        "fundamentals": lambda: legacy.render_fundamentals(data),
        "stock_profiles": lambda: legacy.render_profile_scores(data),
        "analysis": lambda: legacy.render_risk_and_chart(data, histories),
        "sectors": lambda: legacy.render_sector_view(data, histories),
        "news": lambda: legacy.render_news(data, histories, selection.index_name),
        "sources": lambda: render_source_monitor(
            data,
            global_news_sources=legacy.GLOBAL_RSS_SOURCES,
            headers=legacy.DEFAULT_HEADERS,
            manual_events_path=legacy.MANUAL_EVENTS_PATH,
            ir_sources_path=legacy.IR_SOURCES_PATH,
        ),
        "portfolio": lambda: legacy.render_portfolio(data, histories),
        "portfolio_sim": lambda: _portfolio_simulation_page(data, histories),
        "scenarios": lambda: render_scenario_engine(data),
        "ai_lab": lambda: render_ai_lab(
            data,
            market_provider=legacy.MARKET_PROVIDER,
            storage_dir=legacy.AI_LAB_DIR,
        ),
        "watchlist": lambda: legacy.render_watchlist(
            data,
            drawdown_trigger=thresholds.drawdown_trigger,
            payout_max=thresholds.payout_max,
            score_min=thresholds.score_min,
            yield_min=thresholds.yield_min,
        ),
        "value_scanner": lambda: legacy.render_value_watchlist(
            data,
            drawdown_trigger=thresholds.drawdown_trigger,
            payout_max=thresholds.payout_max,
            score_min=thresholds.score_min,
            yield_min=thresholds.yield_min,
            profile_name=selection.profile_name,
        ),
        "deep_value": lambda: legacy.render_special_situation_scanner(data),
        "backtesting": lambda: legacy.render_bat_backtesting(data, selection.index_name),
        "patterns": lambda: legacy.render_universe_pattern_comparison(data, selection.index_name),
        "learning": lambda: legacy.render_learning_module(data),
        "company_profiles": lambda: legacy.render_deep_company_profiles(data),
        "superinvestors": lambda: legacy.render_superinvestors(data),
        "research": lambda: legacy.render_research(data, histories, selection.index_name),
    }
    return routes


def main() -> None:
    """Startet den modularen V7-Anwendungsablauf."""
    configure_application_logging(LOG_DIR)
    st.set_page_config(page_title=APP_TITLE, page_icon="📈", layout="wide")
    with st.sidebar:
        render_language_selector()
    language = current_language()
    render_header(APP_VERSION)

    selection = _render_sidebar(language)
    data, histories, status_summary, status_detail = _load_and_score_universe(selection, language)

    active_page = render_main_navigation()
    st.divider()
    dispatch_page(
        active_page,
        _routes(
            data=data,
            histories=histories,
            status_summary=status_summary,
            status_detail=status_detail,
            selection=selection,
        ),
    )


__all__ = ["clear_application_cache", "main"]
