"""Sidebar für Universumsauswahl und Scanner-Parameter."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import pandas as pd
import streamlit as st

from stock_explorer.application import ScannerThresholds, SidebarSelection
from stock_explorer.i18n import t


@dataclass(frozen=True)
class SidebarCallbacks:
    load_index_constituents: Callable[[str], pd.DataFrame]
    index_source_description: Callable[[str], str]
    clear_application_cache: Callable[[], None]


def _apply_strategy_profile(profile_name: str, profile: Mapping[str, Any]) -> None:
    if st.session_state.get("_applied_strategy_profile") == profile_name:
        return
    st.session_state["scanner_drawdown"] = int(profile["drawdown"])
    st.session_state["scanner_payout"] = int(profile["payout"])
    st.session_state["scanner_score"] = int(profile["score"])
    st.session_state["scanner_yield"] = float(profile["yield"])
    st.session_state["_applied_strategy_profile"] = profile_name


def render_sidebar(
    *,
    language: str,
    provider_name: str,
    index_options: Sequence[str],
    strategy_profiles: Mapping[str, Mapping[str, Any]],
    callbacks: SidebarCallbacks,
) -> SidebarSelection:
    """Rendert die komplette fachliche Sidebar und gibt eine typisierte Auswahl zurück."""
    st.header(t("sidebar.title", language))
    st.caption(t("sidebar.provider", language, provider=provider_name))
    index_name = st.selectbox(t("sidebar.index", language), list(index_options), key="index_name")
    st.caption(t("sidebar.index_hint", language))

    try:
        constituents = callbacks.load_index_constituents(str(index_name))
        st.success(
            t("sidebar.index_loaded", language, index=index_name, count=len(constituents)),
            icon="✅",
        )
        st.caption(
            t(
                "sidebar.index_source",
                language,
                source=callbacks.index_source_description(str(index_name)),
            )
        )
    except Exception as error:
        st.error(t("sidebar.index_error", language, error=error))
        st.stop()

    all_sector_value = "__all__"
    sector_options = [all_sector_value] + sorted(
        constituents["sector"].dropna().astype(str).unique().tolist()
    )
    selected_sector = st.selectbox(
        t("sidebar.sector", language),
        sector_options,
        format_func=lambda value: t("sidebar.all", language) if value == all_sector_value else value,
    )
    query = st.text_input(t("sidebar.search", language)).strip()

    filtered_constituents = constituents.copy()
    if selected_sector != all_sector_value:
        filtered_constituents = filtered_constituents[filtered_constituents["sector"] == selected_sector]
    if query:
        mask = filtered_constituents["name"].astype(str).str.contains(
            query, case=False, na=False
        ) | filtered_constituents["ticker_yahoo"].astype(str).str.contains(query, case=False, na=False)
        filtered_constituents = filtered_constituents[mask]

    maximum = len(filtered_constituents)
    if maximum <= 0:
        st.error(t("sidebar.no_companies", language))
        st.stop()

    default_count = min(40, maximum)
    slider_step = 1 if maximum <= 150 else 10
    max_stocks = st.slider(
        t("sidebar.max_companies", language),
        min_value=1,
        max_value=maximum,
        value=default_count,
        step=slider_step,
        help=t("sidebar.max_companies_help", language),
    )

    st.divider()
    st.header(t("sidebar.scanner_profile", language))
    profile_name = st.selectbox(
        t("sidebar.profile", language),
        list(strategy_profiles),
        key="strategy_profile",
    )
    profile = strategy_profiles[str(profile_name)]
    _apply_strategy_profile(str(profile_name), profile)

    st.caption(str(profile["description"]))
    thresholds = ScannerThresholds(
        drawdown_trigger=float(
            st.slider(
                t("sidebar.drawdown", language),
                min_value=10,
                max_value=60,
                step=5,
                key="scanner_drawdown",
            )
        ),
        payout_max=float(
            st.slider(
                t("sidebar.payout", language),
                min_value=40,
                max_value=120,
                step=5,
                key="scanner_payout",
            )
        ),
        score_min=float(
            st.slider(
                t("sidebar.quality", language),
                min_value=0,
                max_value=100,
                step=5,
                key="scanner_score",
            )
        ),
        yield_min=float(
            st.slider(
                t("sidebar.yield", language),
                min_value=1.0,
                max_value=10.0,
                step=0.5,
                key="scanner_yield",
            )
        ),
    )

    st.divider()
    reload_clicked = st.button(t("sidebar.load", language), type="primary", use_container_width=True)
    if st.button(t("sidebar.clear_cache", language), use_container_width=True):
        callbacks.clear_application_cache()
        st.success(t("sidebar.cache_cleared", language))
        st.rerun()

    return SidebarSelection(
        index_name=str(index_name),
        filtered_constituents=filtered_constituents,
        max_stocks=int(max_stocks),
        profile_name=str(profile_name),
        thresholds=thresholds,
        reload_clicked=bool(reload_clicked),
    )


__all__ = ["SidebarCallbacks", "render_sidebar"]
