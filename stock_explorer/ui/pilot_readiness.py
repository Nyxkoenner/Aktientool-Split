"""Onboarding, Demo und optionales Feedback per E-Mail."""

from __future__ import annotations

import secrets
from html import escape
from typing import Any, Final, Protocol

import pandas as pd
import streamlit as st

from stock_explorer.domain.pilot_models import FEEDBACK_CATEGORIES
from stock_explorer.domain.ux_preferences import (
    DisplayMode,
    KnowledgeLevel,
    set_display_mode,
    set_knowledge_level,
)
from stock_explorer.i18n import current_language, normalize_page_id, t
from stock_explorer.services.pilot_store import PilotStore
from stock_explorer.ui.app_shell import request_navigation
from stock_explorer.ui.responsive import current_display_mode, is_compact_layout
from stock_explorer.ui.ux_foundation import build_feedback_mailto, current_knowledge_level

_ONBOARDING_COMPLETE_KEY: Final = "pilot_onboarding_complete"
_TELEMETRY_CONSENT_KEY: Final = "pilot_telemetry_consent"
_SESSION_ID_KEY: Final = "pilot_session_id"
_LAST_PAGE_EVENT_KEY: Final = "pilot_last_page_event"
_PREPARED_FEEDBACK_KEY: Final = "pilot_prepared_feedback"


class _TaskStateLike(Protocol):
    """Minimaler Zustandstyp für dict und Streamlit SessionStateProxy."""

    def __contains__(self, key: object) -> bool: ...

    def __getitem__(self, key: str) -> Any: ...

    def __setitem__(self, key: str, value: Any) -> None: ...


PILOT_TASK_IDS: Final[tuple[str, ...]] = (
    "choose_company",
    "understand_business",
    "review_risks",
    "run_scenario",
    "use_watchlist",
    "send_feedback",
)


def pilot_session_id() -> str:
    """Liefert eine pseudonyme, nur für die laufende Session verwendete ID."""
    value = st.session_state.get(_SESSION_ID_KEY)
    if not value:
        value = secrets.token_hex(8)
        st.session_state[_SESSION_ID_KEY] = value
    return str(value)


def telemetry_consent_enabled() -> bool:
    return bool(st.session_state.get(_TELEMETRY_CONSENT_KEY, False))


def render_pilot_banner(*, version: str, language: str | None = None) -> None:
    selected_language = language or current_language()
    st.info(t("pilot.banner", selected_language, version=version), icon="🧪")


def _complete_onboarding(store: PilotStore, version: str, language: str) -> None:
    knowledge = str(st.session_state.get("pilot_onboarding_knowledge", KnowledgeLevel.INTERMEDIATE.value))
    display = str(st.session_state.get("pilot_onboarding_display", DisplayMode.AUTO.value))
    consent = bool(st.session_state.get("pilot_onboarding_consent", False))
    set_knowledge_level(knowledge, st.session_state)
    set_display_mode(display, st.session_state)
    # Die zugehörigen Sidebar-Widgets werden erst später in diesem Durchlauf erzeugt.
    st.session_state["knowledge_level_selector"] = knowledge
    st.session_state["display_mode_selector"] = display
    st.session_state[_TELEMETRY_CONSENT_KEY] = consent
    st.session_state[_ONBOARDING_COMPLETE_KEY] = True
    if consent:
        store.save_event(
            event_type="onboarding_completed",
            page_id="start",
            app_version=version,
            language=language,
            knowledge_level=knowledge,
            display_mode=display,
            session_id=pilot_session_id(),
            metadata={"result": "completed"},
        )


def render_onboarding_panel(
    store: PilotStore,
    *,
    version: str,
    language: str | None = None,
) -> None:
    """Zeigt beim ersten Start eine kurze, freiwillige Pilot-Einführung."""
    if st.session_state.get(_ONBOARDING_COMPLETE_KEY):
        return

    selected_language = language or current_language()
    with st.container(border=True):
        st.subheader(t("pilot.onboarding.title", selected_language))
        st.write(t("pilot.onboarding.intro", selected_language))
        with st.form("pilot_onboarding_form"):
            st.selectbox(
                t("pilot.onboarding.knowledge", selected_language),
                options=[level.value for level in KnowledgeLevel],
                index=[level.value for level in KnowledgeLevel].index(current_knowledge_level().value),
                format_func=lambda value: t(f"ux.knowledge.{value}", selected_language),
                key="pilot_onboarding_knowledge",
            )
            st.selectbox(
                t("pilot.onboarding.display", selected_language),
                options=[mode.value for mode in DisplayMode],
                index=[mode.value for mode in DisplayMode].index(current_display_mode().value),
                format_func=lambda value: t(f"ux.display.{value}", selected_language),
                key="pilot_onboarding_display",
            )
            st.checkbox(
                t("pilot.onboarding.consent", selected_language),
                value=False,
                key="pilot_onboarding_consent",
                help=t("pilot.onboarding.consent_help", selected_language),
            )
            submitted = st.form_submit_button(
                t("pilot.onboarding.start", selected_language),
                type="primary",
                use_container_width=True,
            )
        if submitted:
            _complete_onboarding(store, version, selected_language)
            st.success(t("pilot.onboarding.done", selected_language))
        if st.button(
            t("pilot.onboarding.skip", selected_language),
            key="pilot_onboarding_skip",
        ):
            st.session_state[_ONBOARDING_COMPLETE_KEY] = True
            st.rerun()


def record_pilot_page_visit(
    store: PilotStore,
    *,
    page_id: str,
    version: str,
    language: str | None = None,
) -> None:
    """Speichert mit Einwilligung höchstens einen Eintrag pro Seitenwechsel."""
    if not telemetry_consent_enabled():
        return
    normalized_page = normalize_page_id(page_id)
    if st.session_state.get(_LAST_PAGE_EVENT_KEY) == normalized_page:
        return
    selected_language = language or current_language()
    store.save_event(
        event_type="page_view",
        page_id=normalized_page,
        app_version=version,
        language=selected_language,
        knowledge_level=current_knowledge_level().value,
        display_mode=current_display_mode().value,
        session_id=pilot_session_id(),
    )
    st.session_state[_LAST_PAGE_EVENT_KEY] = normalized_page


def _render_demo(language: str, has_market_data: bool) -> None:
    st.subheader(t("pilot.demo.title", language))
    st.caption(t("pilot.demo.fictional", language))
    with st.container(border=True):
        st.markdown(f"### {t('pilot.demo.company', language)}")
        metrics = (
            (t("pilot.demo.quality", language), "78 / 100"),
            (t("pilot.demo.pe", language), "17,4"),
            (t("pilot.demo.drawdown", language), "−14 %"),
            (t("pilot.demo.scenario", language), "−22 %"),
        )
        columns = st.columns(1 if is_compact_layout() else 4)
        for index, (label, value) in enumerate(metrics):
            columns[index % len(columns)].metric(label, value)
        st.markdown(t("pilot.demo.interpretation", language))
        st.warning(t("pilot.demo.warning", language))

    if has_market_data:
        st.button(
            t("pilot.demo.real_analysis", language),
            type="primary",
            on_click=request_navigation,
            args=("analysis_hub",),
            use_container_width=True,
        )
    else:
        st.info(t("pilot.demo.load_data", language))


def _task_state_key(task_id: str) -> str:
    return f"pilot_task_state_{task_id}"


def _task_widget_key(task_id: str) -> str:
    return f"pilot_task_widget_{task_id}"


def _set_task_completed(
    task_id: str,
    completed: bool,
    state: _TaskStateLike,
) -> None:
    """Speichert den Aufgabenstatus getrennt vom zugehörigen Widget-State."""
    state[_task_state_key(task_id)] = bool(completed)


def _task_is_completed(task_id: str, state: _TaskStateLike) -> bool:
    key = _task_state_key(task_id)
    return bool(state[key]) if key in state else False


def _copy_task_widget_to_state(task_id: str) -> None:
    _set_task_completed(
        task_id,
        bool(st.session_state[_task_widget_key(task_id)])
        if _task_widget_key(task_id) in st.session_state
        else False,
        st.session_state,
    )


def _prepare_task_widget(task_id: str) -> str:
    """Synchronisiert vor der Widget-Erzeugung den sichtbaren Checkbox-Status."""
    widget_key = _task_widget_key(task_id)
    completed = _task_is_completed(task_id, st.session_state)
    current_widget_value = bool(st.session_state[widget_key]) if widget_key in st.session_state else False
    if current_widget_value != completed:
        st.session_state[widget_key] = completed
    return widget_key


def _render_tasks(language: str) -> None:
    st.subheader(t("pilot.tasks.title", language))
    st.write(t("pilot.tasks.intro", language))
    completed = 0
    for task_id in PILOT_TASK_IDS:
        widget_key = _prepare_task_widget(task_id)
        st.checkbox(
            t(f"pilot.tasks.{task_id}", language),
            key=widget_key,
            on_change=_copy_task_widget_to_state,
            args=(task_id,),
        )
        completed += int(_task_is_completed(task_id, st.session_state))
    st.progress(completed / len(PILOT_TASK_IDS))
    st.caption(t("pilot.tasks.progress", language, completed=completed, total=len(PILOT_TASK_IDS)))
    if completed == len(PILOT_TASK_IDS):
        st.success(t("pilot.tasks.complete", language))


def _feedback_mailto_html(link: str, label: str) -> str:
    safe_link = escape(link, quote=True)
    safe_label = escape(label)
    return (
        '<a href="'
        + safe_link
        + '" style="display:block;text-align:center;padding:0.65rem 0.8rem;'
        + "border:1px solid rgba(128,128,128,.45);border-radius:.5rem;"
        + 'text-decoration:none;font-weight:600;">'
        + safe_label
        + "</a>"
    )


def _build_pilot_feedback_message(
    *,
    rating: int,
    message: str,
    contact_email: str,
    language: str,
) -> str:
    """Baut den sichtbaren Mailtext ohne lokale Speicherung auf."""
    rating_label = "Bewertung" if language == "de" else "Rating"
    contact_label = "Kontakt für Rückfragen" if language == "de" else "Contact for follow-up"
    contact_value = contact_email.strip() or "–"
    return f"{rating_label}: {rating}/5\n{contact_label}: {contact_value}\n\n{message.strip()}"


def _render_structured_feedback(
    *,
    version: str,
    recipient: str,
    language: str,
) -> None:
    st.subheader(t("pilot.feedback.title", language))
    st.write(t("pilot.feedback.intro", language))
    with st.form("pilot_structured_feedback_form", clear_on_submit=False):
        category = st.selectbox(
            t("pilot.feedback.category", language),
            options=FEEDBACK_CATEGORIES,
            format_func=lambda value: t(f"pilot.feedback.category.{value}", language),
            key="pilot_feedback_category",
        )
        rating = st.slider(
            t("pilot.feedback.rating", language),
            min_value=1,
            max_value=5,
            value=4,
            key="pilot_feedback_rating",
        )
        message = st.text_area(
            t("pilot.feedback.message", language),
            placeholder=t("pilot.feedback.placeholder", language),
            height=150,
            max_chars=2000,
            key="pilot_feedback_message",
        )
        contact_email = st.text_input(
            t("pilot.feedback.email", language),
            max_chars=254,
            key="pilot_feedback_email",
        )
        submitted = st.form_submit_button(
            t("pilot.feedback.prepare_email", language),
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if len(message.strip()) < 3:
            st.error(t("pilot.feedback.message_required", language))
        else:
            st.session_state[_PREPARED_FEEDBACK_KEY] = {
                "category": str(category),
                "rating": int(rating),
                "message": message.strip(),
                "contact_email": contact_email.strip(),
                "page_id": normalize_page_id(st.session_state.get("main_navigation")),
                "knowledge_level": current_knowledge_level().value,
            }
            _set_task_completed("send_feedback", True, st.session_state)
            st.success(t("pilot.feedback.prepared", language))

    prepared = st.session_state.get(_PREPARED_FEEDBACK_KEY)
    if isinstance(prepared, dict):
        prepared_category = str(prepared.get("category", "idea"))
        mail_message = _build_pilot_feedback_message(
            rating=int(prepared.get("rating", 4)),
            message=str(prepared.get("message", "")),
            contact_email=str(prepared.get("contact_email", "")),
            language=language,
        )
        link = build_feedback_mailto(
            recipient=recipient,
            version=version,
            page_id=str(prepared.get("page_id", "pilot_center")),
            language=language,
            knowledge_level=str(prepared.get("knowledge_level", "intermediate")),
            category=t(f"pilot.feedback.category.{prepared_category}", language),
            message=mail_message,
        )
        st.markdown(
            _feedback_mailto_html(link, t("pilot.feedback.open_email", language)),
            unsafe_allow_html=True,
        )
        st.caption(t("pilot.feedback.email_optional", language, recipient=recipient))
    st.caption(t("pilot.feedback.privacy", language))


def render_pilot_center(
    data: pd.DataFrame,
    store: PilotStore,
    *,
    version: str,
    recipient: str,
) -> None:
    """Rendert Demo, Testaufgaben und optionales E-Mail-Feedback."""
    language = current_language()
    st.header(t("pilot.center.title", language))
    st.write(t("pilot.center.intro", language))
    if _TELEMETRY_CONSENT_KEY not in st.session_state:
        st.session_state[_TELEMETRY_CONSENT_KEY] = False
    st.toggle(
        t("pilot.center.telemetry", language),
        key=_TELEMETRY_CONSENT_KEY,
        help=t("pilot.center.telemetry_help", language),
    )
    st.caption(t("pilot.center.telemetry_caption", language))
    demo_tab, tasks_tab, feedback_tab = st.tabs(
        [
            t("pilot.center.tab.demo", language),
            t("pilot.center.tab.tasks", language),
            t("pilot.center.tab.feedback", language),
        ]
    )
    with demo_tab:
        _render_demo(language, data is not None and not data.empty)
    with tasks_tab:
        _render_tasks(language)
    with feedback_tab:
        _render_structured_feedback(
            version=version,
            recipient=recipient,
            language=language,
        )


__all__ = [
    "PILOT_TASK_IDS",
    "pilot_session_id",
    "record_pilot_page_visit",
    "render_onboarding_panel",
    "render_pilot_banner",
    "render_pilot_center",
    "telemetry_consent_enabled",
]
