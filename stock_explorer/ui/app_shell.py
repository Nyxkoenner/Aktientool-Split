from __future__ import annotations

import streamlit as st

from stock_explorer.i18n import SUPPORTED_LANGUAGES, current_language, set_language, t
from stock_explorer.i18n.navigation import (
    MAIN_NAVIGATION,
    legacy_page_label,
    normalize_page_id,
    translation_key_for_page,
)

_LANGUAGE_WIDGET_KEY = "app_language_selector"


def _apply_language_choice(widget_key: str) -> None:
    """Copy the widget selection to the independent application language state."""
    choice = st.session_state.get(widget_key)
    if choice is not None:
        set_language(str(choice), st.session_state)


def render_language_selector(*, key: str = _LANGUAGE_WIDGET_KEY) -> str:
    """Render the language selector without mutating its widget key afterwards.

    Streamlit owns a widget's session-state key after the widget is instantiated.
    Therefore the selectbox uses ``app_language_selector`` while the selected
    application language remains stored separately under ``app_language``.
    """
    selected = current_language()
    codes = list(SUPPORTED_LANGUAGES)
    if selected not in codes:
        selected = codes[0]

    # Initialize the widget state only before the widget is created.
    widget_value = st.session_state.get(key)
    if widget_value not in codes:
        st.session_state[key] = selected

    choice = st.selectbox(
        t("language.label", selected),
        options=codes,
        format_func=lambda code: t(f"language.{code}", selected),
        key=key,
        on_change=_apply_language_choice,
        args=(key,),
    )

    # On the first run there is no callback yet. Updating the separate
    # application-language key is safe because it is not the widget key.
    if current_language() != choice:
        set_language(choice, st.session_state)
    return choice


def render_header(version: str) -> None:
    language = current_language()
    st.title(t("app.title", language))
    st.caption(f"Version {version} · {t('app.subtitle', language)}")


def render_main_navigation(*, key: str = "main_navigation") -> str:
    language = current_language()
    current = normalize_page_id(st.session_state.get(key))
    if st.session_state.get(key) != current:
        st.session_state[key] = current
    page_ids = [item.page_id for item in MAIN_NAVIGATION]
    return st.radio(
        t("nav.label", language),
        options=page_ids,
        format_func=lambda page_id: t(translation_key_for_page(page_id), language),
        horizontal=True,
        key=key,
        label_visibility="collapsed",
    )


__all__ = [
    "MAIN_NAVIGATION",
    "legacy_page_label",
    "normalize_page_id",
    "render_header",
    "render_language_selector",
    "render_main_navigation",
]
