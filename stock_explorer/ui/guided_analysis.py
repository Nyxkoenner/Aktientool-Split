"""Geführte Einstiege und Analysepfade für unterschiedliche Wissensstände."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

import pandas as pd
import streamlit as st

from stock_explorer.domain.ux_preferences import KnowledgeLevel
from stock_explorer.i18n import current_language, t
from stock_explorer.ui.app_shell import request_navigation
from stock_explorer.ui.company_select import company_selectbox
from stock_explorer.ui.responsive import is_compact_layout
from stock_explorer.ui.ux_foundation import current_knowledge_level


@dataclass(frozen=True)
class GuidedStep:
    number: int
    page_id: str
    title_key: str
    description_key: str


GUIDED_ANALYSIS_STEPS: Final[tuple[GuidedStep, ...]] = (
    GuidedStep(1, "company_profiles", "ux.flow.step.business", "ux.flow.step.business.description"),
    GuidedStep(2, "fundamentals", "ux.flow.step.quality", "ux.flow.step.quality.description"),
    GuidedStep(3, "analysis", "ux.flow.step.risk", "ux.flow.step.risk.description"),
    GuidedStep(4, "news", "ux.flow.step.events", "ux.flow.step.events.description"),
    GuidedStep(5, "scenarios", "ux.flow.step.scenario", "ux.flow.step.scenario.description"),
)


def _safe_count(frame: pd.DataFrame, column: str) -> int:
    if frame is None or frame.empty or column not in frame.columns:
        return 0
    return int(frame[column].dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique())


def _safe_number(value: Any, *, digits: int = 1) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "–"
    if pd.isna(numeric):
        return "–"
    return f"{numeric:.{digits}f}"


def _display_text(value: Any, fallback: str = "–") -> str:
    if value is None or pd.isna(value):
        return fallback
    candidate = str(value).strip()
    return candidate or fallback


def _company_name(row: pd.Series, ticker: str) -> str:
    return _display_text(row.get("name"), ticker)


def _progress_key(ticker: str, page_id: str) -> str:
    safe_ticker = "".join(character if character.isalnum() else "_" for character in ticker)
    return f"guided_analysis_done_{safe_ticker}_{page_id}"


def completed_guided_steps(ticker: str) -> int:
    """Zählt die vom Nutzer für eine Aktie bewusst bestätigten Analyseschritte."""
    return sum(
        bool(st.session_state.get(_progress_key(ticker, step.page_id))) for step in GUIDED_ANALYSIS_STEPS
    )


def _render_action_card(
    *,
    title_key: str,
    description_key: str,
    button_key: str,
    target_page: str,
    language: str,
) -> None:
    with st.container(border=True):
        st.subheader(t(title_key, language))
        st.write(t(description_key, language))
        st.button(
            t("ux.home.open", language),
            key=button_key,
            on_click=request_navigation,
            args=(target_page,),
            use_container_width=True,
        )


def render_start_page(data: pd.DataFrame) -> None:
    """Rendert eine ruhige Startseite mit drei klaren Arbeitswegen."""
    language = current_language()
    level = current_knowledge_level()

    st.header(t("ux.home.title", language))
    st.write(t(f"ux.home.intro.{level.value}", language))

    company_count = _safe_count(data, "ticker_yahoo")
    sector_count = _safe_count(data, "sector")
    scored_count = 0
    if data is not None and not data.empty and "total_score" in data.columns:
        scored_count = int(pd.to_numeric(data["total_score"], errors="coerce").notna().sum())

    metric_columns = st.columns(3)
    metric_columns[0].metric(t("ux.home.metric.companies", language), company_count)
    metric_columns[1].metric(t("ux.home.metric.sectors", language), sector_count)
    metric_columns[2].metric(t("ux.home.metric.scored", language), scored_count)

    st.subheader(t("ux.home.choose_path", language))
    action_cards = (
        (
            "ux.home.stock.title",
            "ux.home.stock.description",
            "ux_home_stock",
            "analysis_hub",
        ),
        (
            "ux.home.portfolio.title",
            "ux.home.portfolio.description",
            "ux_home_portfolio",
            "portfolio",
        ),
        (
            "ux.home.events.title",
            "ux.home.events.description",
            "ux_home_events",
            "watchlist",
        ),
    )
    if is_compact_layout():
        for title_key, description_key, button_key, target_page in action_cards:
            _render_action_card(
                title_key=title_key,
                description_key=description_key,
                button_key=button_key,
                target_page=target_page,
                language=language,
            )
    else:
        for column, card in zip(st.columns(3), action_cards, strict=True):
            with column:
                title_key, description_key, button_key, target_page = card
                _render_action_card(
                    title_key=title_key,
                    description_key=description_key,
                    button_key=button_key,
                    target_page=target_page,
                    language=language,
                )

    if level == KnowledgeLevel.BEGINNER:
        st.info(t("ux.home.beginner_tip", language))
    elif level == KnowledgeLevel.EXPERT:
        st.caption(t("ux.home.expert_tip", language))


def _render_company_snapshot(row: pd.Series, ticker: str, language: str) -> None:
    metrics = (
        (t("ux.flow.metric.company", language), _company_name(row, ticker)),
        (t("ux.flow.metric.sector", language), _display_text(row.get("sector"))),
        (t("ux.flow.metric.quality", language), _safe_number(row.get("total_score"))),
        (
            t("ux.flow.metric.value", language),
            _safe_number(row.get("value_profile_score", row.get("value_score"))),
        ),
    )
    column_count = 1 if is_compact_layout() else 4
    columns = st.columns(column_count)
    for index, (label, value) in enumerate(metrics):
        columns[index % column_count].metric(label, value)


def render_guided_analysis_hub(data: pd.DataFrame) -> None:
    """Rendert einen fünfstufigen, bewusst bestätigbaren Aktienanalysepfad."""
    language = current_language()
    level = current_knowledge_level()

    st.header(t("ux.flow.title", language))
    st.write(t(f"ux.flow.intro.{level.value}", language))

    try:
        ticker = company_selectbox(
            t("ux.flow.select_company", language),
            data,
            key="guided_analysis_ticker",
        )
    except ValueError:
        st.info(t("loading.prompt", language))
        return

    ticker_rows = data[data["ticker_yahoo"].astype(str) == ticker]
    row = ticker_rows.iloc[0] if not ticker_rows.empty else pd.Series(dtype=object)
    _render_company_snapshot(row, ticker, language)

    completed = completed_guided_steps(ticker)
    st.progress(completed / len(GUIDED_ANALYSIS_STEPS))
    st.caption(
        t(
            "ux.flow.progress",
            language,
            completed=completed,
            total=len(GUIDED_ANALYSIS_STEPS),
        )
    )

    compact = is_compact_layout()
    for step in GUIDED_ANALYSIS_STEPS:
        with st.container(border=True):
            if compact:
                st.markdown(f"### {step.number}. {t(step.title_key, language)}")
                if level == KnowledgeLevel.EXPERT:
                    st.caption(t(step.description_key, language))
                else:
                    st.write(t(step.description_key, language))
                st.button(
                    t("ux.flow.open_step", language),
                    key=f"guided_open_{ticker}_{step.page_id}",
                    on_click=request_navigation,
                    args=(step.page_id,),
                    use_container_width=True,
                )
            else:
                title_column, action_column = st.columns([4, 1])
                title_column.markdown(f"### {step.number}. {t(step.title_key, language)}")
                if level == KnowledgeLevel.EXPERT:
                    title_column.caption(t(step.description_key, language))
                else:
                    title_column.write(t(step.description_key, language))
                action_column.button(
                    t("ux.flow.open_step", language),
                    key=f"guided_open_{ticker}_{step.page_id}",
                    on_click=request_navigation,
                    args=(step.page_id,),
                    use_container_width=True,
                )
            st.checkbox(
                t("ux.flow.mark_done", language),
                key=_progress_key(ticker, step.page_id),
            )

    incomplete = [
        step
        for step in GUIDED_ANALYSIS_STEPS
        if not st.session_state.get(_progress_key(ticker, step.page_id))
    ]
    if incomplete:
        next_step = incomplete[0]
        st.button(
            t("ux.flow.next_recommended", language, step=t(next_step.title_key, language)),
            key=f"guided_next_{ticker}",
            type="primary",
            on_click=request_navigation,
            args=(next_step.page_id,),
        )
    else:
        st.success(t("ux.flow.complete", language))

    st.caption(t("ux.flow.disclaimer", language))


def render_analysis_next_steps(active_page: str) -> None:
    """Zeigt unter Fachseiten einen kompakten Vor-/Zurück-Pfad an."""
    page_ids = [step.page_id for step in GUIDED_ANALYSIS_STEPS]
    if active_page not in page_ids:
        return

    language = current_language()
    index = page_ids.index(active_page)
    st.divider()
    st.caption(t("ux.flow.footer", language))
    if is_compact_layout():
        if index > 0:
            previous = GUIDED_ANALYSIS_STEPS[index - 1]
            st.button(
                t("ux.flow.previous", language, step=t(previous.title_key, language)),
                key=f"guided_footer_previous_{active_page}",
                on_click=request_navigation,
                args=(previous.page_id,),
                use_container_width=True,
            )
        st.button(
            t("ux.flow.back_to_hub", language),
            key=f"guided_footer_hub_{active_page}",
            on_click=request_navigation,
            args=("analysis_hub",),
            use_container_width=True,
        )
        if index < len(GUIDED_ANALYSIS_STEPS) - 1:
            next_step = GUIDED_ANALYSIS_STEPS[index + 1]
            st.button(
                t("ux.flow.next", language, step=t(next_step.title_key, language)),
                key=f"guided_footer_next_{active_page}",
                on_click=request_navigation,
                args=(next_step.page_id,),
                use_container_width=True,
            )
        return

    previous_column, hub_column, next_column = st.columns(3)
    if index > 0:
        previous = GUIDED_ANALYSIS_STEPS[index - 1]
        previous_column.button(
            t("ux.flow.previous", language, step=t(previous.title_key, language)),
            key=f"guided_footer_previous_{active_page}",
            on_click=request_navigation,
            args=(previous.page_id,),
            use_container_width=True,
        )
    hub_column.button(
        t("ux.flow.back_to_hub", language),
        key=f"guided_footer_hub_{active_page}",
        on_click=request_navigation,
        args=("analysis_hub",),
        use_container_width=True,
    )
    if index < len(GUIDED_ANALYSIS_STEPS) - 1:
        next_step = GUIDED_ANALYSIS_STEPS[index + 1]
        next_column.button(
            t("ux.flow.next", language, step=t(next_step.title_key, language)),
            key=f"guided_footer_next_{active_page}",
            on_click=request_navigation,
            args=(next_step.page_id,),
            use_container_width=True,
        )


__all__ = [
    "GUIDED_ANALYSIS_STEPS",
    "GuidedStep",
    "completed_guided_steps",
    "render_analysis_next_steps",
    "render_guided_analysis_hub",
    "render_start_page",
]
