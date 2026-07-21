"""UX-Grundlagen: Wissensmodus, Hilfen, Feedback und Datenvertrauen."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import cast
from urllib.parse import quote

import streamlit as st

from stock_explorer.content import glossary_entry, page_guide, search_glossary
from stock_explorer.domain.ux_preferences import (
    KnowledgeLevel,
    knowledge_level_from_state,
    normalize_knowledge_level,
    set_knowledge_level,
)
from stock_explorer.i18n import current_language, normalize_page_id, t, translation_key_for_page
from stock_explorer.ui.responsive import is_compact_layout

_KNOWLEDGE_WIDGET_KEY = "knowledge_level_selector"


@dataclass(frozen=True)
class DataTrustSnapshot:
    """Einheitliche Metadaten für Datenstand und Quellenvertrauen."""

    timestamp: str
    provider: str
    coverage_percent: float | None
    base_currency: str
    profile_name: str


def current_knowledge_level() -> KnowledgeLevel:
    """Liest die Wissensstufe aus dem Streamlit-Session-State."""
    return knowledge_level_from_state(st.session_state)


def _apply_knowledge_choice(widget_key: str) -> None:
    choice = st.session_state.get(widget_key)
    if choice is not None:
        set_knowledge_level(str(choice), st.session_state)


def render_knowledge_selector(
    *,
    language: str | None = None,
    key: str = _KNOWLEDGE_WIDGET_KEY,
) -> KnowledgeLevel:
    """Rendert die Wissensstufe mit getrenntem Widget- und Anwendungs-Key."""
    selected_language = language or current_language()
    selected = current_knowledge_level()
    options = list(KnowledgeLevel)
    option_values = [option.value for option in options]

    widget_value = st.session_state.get(key)
    if widget_value not in option_values:
        st.session_state[key] = selected.value

    choice = st.selectbox(
        t("ux.knowledge.label", selected_language),
        options=option_values,
        format_func=lambda value: t(f"ux.knowledge.{value}", selected_language),
        key=key,
        on_change=_apply_knowledge_choice,
        args=(key,),
        help=t("ux.knowledge.help", selected_language),
    )
    normalized = KnowledgeLevel(choice)
    if knowledge_level_from_state(st.session_state) != normalized:
        set_knowledge_level(normalized, st.session_state)
    st.caption(t(f"ux.knowledge.caption.{normalized.value}", selected_language))
    return normalized


def render_glossary_panel(*, language: str | None = None) -> None:
    """Rendert ein durchsuchbares Börsenlexikon in der Sidebar."""
    selected_language = language or current_language()
    with st.expander(t("ux.glossary.title", selected_language), expanded=False):
        st.caption(t("ux.glossary.caption", selected_language))
        query = st.text_input(
            t("ux.glossary.search", selected_language),
            key="ux_glossary_search",
            placeholder=t("ux.glossary.placeholder", selected_language),
        )
        entries = search_glossary(query, selected_language)
        if not entries:
            st.info(t("ux.glossary.no_results", selected_language))
            return
        visible_entries = entries[:8]
        visible_keys: tuple[str, ...] = tuple(entry.key for entry in visible_entries)
        if st.session_state.get("ux_glossary_selected") not in visible_keys:
            st.session_state["ux_glossary_selected"] = visible_keys[0]

        def _entry_title(key: str) -> str:
            item = glossary_entry(key)
            return item.title(selected_language) if item is not None else key

        selected_key = cast(
            str,
            st.selectbox(
                t("ux.glossary.more", selected_language),
                options=visible_keys,
                format_func=_entry_title,
                key="ux_glossary_selected",
            ),
        )
        entry = glossary_entry(selected_key)
        if entry is None:
            return
        st.write(entry.explanation(selected_language))
        st.markdown(
            f"**{t('ux.glossary.why', selected_language)}**  \n{entry.why_it_matters(selected_language)}"
        )
        st.markdown(
            f"**{t('ux.glossary.limits', selected_language)}**  \n{entry.limitations(selected_language)}"
        )
        for resource in entry.resources:
            st.markdown(f"[{resource.title(selected_language)}]({resource.url(selected_language)}) ↗")


def render_page_guidance(page_id: str, *, language: str | None = None) -> None:
    """Zeigt eine seitenspezifische Erklärung passend zur Wissensstufe."""
    selected_language = language or current_language()
    level = current_knowledge_level()
    guide = page_guide(page_id)
    expanded = level == KnowledgeLevel.BEGINNER

    with st.expander(
        f"💡 {guide.title(selected_language)}",
        expanded=expanded,
    ):
        st.write(guide.summary(selected_language, level))
        steps = guide.steps(selected_language)
        if level == KnowledgeLevel.BEGINNER and steps:
            st.markdown(f"**{t('ux.guide.steps', selected_language)}**")
            for number, step in enumerate(steps, start=1):
                st.write(f"{number}. {step}")

        if guide.glossary_keys:
            st.markdown(f"**{t('ux.guide.terms', selected_language)}**")
            for key in guide.glossary_keys:
                entry = glossary_entry(key)
                if entry is None:
                    continue
                st.markdown(f"**{entry.title(selected_language)}**")
                if level == KnowledgeLevel.EXPERT:
                    st.write(entry.explanation(selected_language))
                    st.caption(entry.limitations(selected_language))
                else:
                    st.write(entry.short(selected_language))
                    st.caption(entry.why_it_matters(selected_language))
                for resource in entry.resources:
                    st.markdown(f"[{resource.title(selected_language)}]({resource.url(selected_language)}) ↗")
        st.caption(t("ux.guide.external_notice", selected_language))


def quality_key_from_coverage(coverage_percent: float | None) -> str:
    """Ordnet Datenabdeckung einer transparenten Qualitätsklasse zu."""
    if coverage_percent is None:
        return "unknown"
    if coverage_percent >= 95.0:
        return "high"
    if coverage_percent >= 75.0:
        return "medium"
    return "low"


def render_data_trust_panel(
    snapshot: DataTrustSnapshot,
    *,
    language: str | None = None,
) -> None:
    """Zeigt Datenstand, Quelle, Abdeckung und Modellgrenzen einheitlich an."""
    selected_language = language or current_language()
    quality_key = quality_key_from_coverage(snapshot.coverage_percent)
    coverage = (
        t("common.none", selected_language)
        if snapshot.coverage_percent is None
        else f"{snapshot.coverage_percent:.1f} %"
    )
    st.caption(
        t(
            "ux.trust.summary",
            selected_language,
            timestamp=snapshot.timestamp or t("common.none", selected_language),
            provider=snapshot.provider,
            coverage=coverage,
            quality=t(f"ux.trust.quality.{quality_key}", selected_language),
        )
    )
    with st.expander(t("ux.trust.details", selected_language), expanded=False):
        source_text = t(
            "ux.trust.source_line",
            selected_language,
            provider=snapshot.provider,
            timestamp=snapshot.timestamp or t("common.none", selected_language),
        )
        context_text = t(
            "ux.trust.context_line",
            selected_language,
            coverage=coverage,
            currency=snapshot.base_currency,
            profile=snapshot.profile_name,
        )
        if is_compact_layout():
            st.markdown(source_text)
            st.markdown(context_text)
        else:
            left, right = st.columns(2)
            left.markdown(source_text)
            right.markdown(context_text)
        st.info(t("ux.trust.model_notice", selected_language))


def build_feedback_mailto(
    *,
    recipient: str,
    version: str,
    page_id: str,
    language: str,
    knowledge_level: KnowledgeLevel | str,
    category: str,
    message: str,
) -> str:
    """Erzeugt einen URL-kodierten Mailto-Link ohne sensible Portfoliodaten."""
    level = normalize_knowledge_level(knowledge_level)
    subject = f"Feedback Aktien Explorer V{version} – {category}"
    body = "\n".join(
        (
            f"App-Version: {version}",
            f"Bereich: {normalize_page_id(page_id)}",
            f"Sprache: {language}",
            f"Wissensmodus: {level.value}",
            f"Kategorie: {category}",
            "",
            "Feedback:",
            message.strip() or "Bitte hier Feedback ergänzen.",
            "",
            "Hinweis: Portfolio-, Dokument- und Modelldaten wurden nicht automatisch angehängt.",
        )
    )
    return f"mailto:{recipient}?subject={quote(subject)}&body={quote(body)}"


def render_feedback_panel(
    *,
    version: str,
    page_id: str,
    recipient: str,
    language: str | None = None,
) -> None:
    """Rendert einen globalen Feedback-Einstieg über das lokale E-Mail-Programm."""
    selected_language = language or current_language()
    with st.expander(t("ux.feedback.title", selected_language), expanded=False):
        st.caption(t("ux.feedback.caption", selected_language, recipient=recipient))
        from stock_explorer.ui.app_shell import request_navigation

        st.button(
            t("ux.feedback.structured", selected_language),
            key="ux_feedback_open_structured",
            on_click=request_navigation,
            args=("pilot_center",),
            use_container_width=True,
        )
        category_keys = ("bug", "idea", "question", "data")
        category = st.selectbox(
            t("ux.feedback.category", selected_language),
            options=category_keys,
            format_func=lambda value: t(f"ux.feedback.category.{value}", selected_language),
            key="ux_feedback_category",
        )
        message = st.text_area(
            t("ux.feedback.message", selected_language),
            key="ux_feedback_message",
            placeholder=t("ux.feedback.placeholder", selected_language),
            height=100,
        )
        link = build_feedback_mailto(
            recipient=recipient,
            version=version,
            page_id=page_id,
            language=selected_language,
            knowledge_level=current_knowledge_level(),
            category=t(f"ux.feedback.category.{category}", selected_language),
            message=message,
        )
        label = escape(t("ux.feedback.open_email", selected_language))
        safe_link = escape(link, quote=True)
        st.markdown(
            (
                '<a href="' + safe_link + '" '
                'style="display:block;text-align:center;padding:0.55rem 0.75rem;'
                "border:1px solid rgba(128,128,128,.45);border-radius:.5rem;"
                'text-decoration:none;font-weight:600;">' + label + "</a>"
            ),
            unsafe_allow_html=True,
        )
        st.caption(t("ux.feedback.privacy", selected_language))


def current_page_label(page_id: str, language: str | None = None) -> str:
    selected_language = language or current_language()
    return t(translation_key_for_page(normalize_page_id(page_id)), selected_language)


__all__ = [
    "DataTrustSnapshot",
    "build_feedback_mailto",
    "current_knowledge_level",
    "current_page_label",
    "quality_key_from_coverage",
    "render_data_trust_panel",
    "render_feedback_panel",
    "render_glossary_panel",
    "render_knowledge_selector",
    "render_page_guidance",
]
