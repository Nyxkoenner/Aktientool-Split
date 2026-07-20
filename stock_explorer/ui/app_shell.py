from __future__ import annotations

import streamlit as st

from stock_explorer.i18n import SUPPORTED_LANGUAGES, current_language, set_language, t
from stock_explorer.i18n.navigation import (
    MAIN_NAVIGATION,
    legacy_page_label,
    normalize_page_id,
    translation_key_for_page,
)


def render_language_selector(*, key: str = "app_language") -> str:
    selected = current_language()
    codes = list(SUPPORTED_LANGUAGES)
    if selected not in codes:
        selected = codes[0]
    choice = st.selectbox(
        t("language.label", selected),
        options=codes,
        index=codes.index(selected),
        format_func=lambda code: t(f"language.{code}", selected),
        key=key,
    )
    return set_language(choice, st.session_state)


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
