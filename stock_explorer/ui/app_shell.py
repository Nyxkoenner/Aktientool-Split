from __future__ import annotations

import streamlit as st

from stock_explorer.i18n import SUPPORTED_LANGUAGES, current_language, set_language, t
from stock_explorer.i18n.navigation import (
    MAIN_NAVIGATION,
    legacy_page_label,
    normalize_page_id,
    translation_key_for_page,
)
from stock_explorer.ui.navigation_model import (
    ACTIVE_PAGE_KEY,
    GROUP_WIDGET_KEY,
    NAVIGATION_GROUPS,
    NAVIGATION_REQUEST_KEY,
    default_page_for_group,
    navigation_group,
    navigation_group_for_page,
    page_widget_key,
)
from stock_explorer.ui.responsive import current_display_mode, navigation_widget_style

_LANGUAGE_WIDGET_KEY = "app_language_selector"
_NAVIGATION_RENDER_MODE_KEY = "navigation_render_mode"


def _apply_language_choice(widget_key: str) -> None:
    """Copy the widget selection to the independent application language state."""
    choice = st.session_state.get(widget_key)
    if choice is not None:
        set_language(str(choice), st.session_state)


def render_language_selector(*, key: str = _LANGUAGE_WIDGET_KEY) -> str:
    """Render the language selector without mutating its widget key afterwards."""
    selected = current_language()
    codes = list(SUPPORTED_LANGUAGES)
    if selected not in codes:
        selected = codes[0]

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

    if current_language() != choice:
        set_language(choice, st.session_state)
    return choice


def render_header(version: str) -> None:
    language = current_language()
    st.title(t("app.title", language))
    st.caption(f"Version {version} · {t('app.subtitle', language)}")


def request_navigation(page_id: str) -> None:
    """Plant eine Navigation für den nächsten Streamlit-Durchlauf.

    Fachseiten können diese Funktion als Button-Callback verwenden, ohne bereits
    erzeugte Radio- oder Selectbox-Widget-Keys nachträglich zu verändern.
    """
    st.session_state[NAVIGATION_REQUEST_KEY] = normalize_page_id(page_id)


def _consume_navigation_request() -> str | None:
    if NAVIGATION_REQUEST_KEY not in st.session_state:
        return None
    requested = normalize_page_id(st.session_state[NAVIGATION_REQUEST_KEY])
    del st.session_state[NAVIGATION_REQUEST_KEY]
    return requested


def render_main_navigation(*, key: str = ACTIVE_PAGE_KEY) -> str:
    """Rendert fünf Hauptbereiche und darunter den jeweiligen Unterbereich."""
    language = current_language()
    requested = _consume_navigation_request()
    stored_page = st.session_state.get(key)
    current_page = requested or ("start" if stored_page is None else normalize_page_id(stored_page))
    requested_group = navigation_group_for_page(current_page)
    compact_navigation = navigation_widget_style(current_display_mode()) == "selectbox"

    group_ids = [group.group_id for group in NAVIGATION_GROUPS]
    group_widget_key = f"{GROUP_WIDGET_KEY}_compact" if compact_navigation else GROUP_WIDGET_KEY
    render_mode = "compact" if compact_navigation else "wide"
    mode_changed = st.session_state.get(_NAVIGATION_RENDER_MODE_KEY) != render_mode
    if requested is not None or mode_changed or st.session_state.get(group_widget_key) not in group_ids:
        st.session_state[group_widget_key] = requested_group
    st.session_state[_NAVIGATION_RENDER_MODE_KEY] = render_mode

    if compact_navigation:
        selected_group_id = str(
            st.selectbox(
                t("ux.nav.main_label", language),
                options=group_ids,
                format_func=lambda group_id: t(navigation_group(group_id).translation_key, language),
                key=group_widget_key,
            )
        )
    else:
        selected_group_id = str(
            st.radio(
                t("ux.nav.main_label", language),
                options=group_ids,
                format_func=lambda group_id: t(navigation_group(group_id).translation_key, language),
                horizontal=True,
                key=group_widget_key,
                label_visibility="collapsed",
            )
        )

    selected_group = navigation_group(selected_group_id)
    if navigation_group_for_page(current_page) != selected_group_id:
        current_page = default_page_for_group(selected_group_id)

    if len(selected_group.pages) == 1:
        active_page = selected_group.pages[0]
    else:
        base_subpage_key = page_widget_key(selected_group_id)
        subpage_key = f"{base_subpage_key}_compact" if compact_navigation else base_subpage_key
        if (requested is not None or mode_changed) and current_page in selected_group.pages:
            st.session_state[subpage_key] = current_page
        elif st.session_state.get(subpage_key) not in selected_group.pages:
            st.session_state[subpage_key] = current_page

        active_page = str(
            st.selectbox(
                t("ux.nav.subpage_label", language),
                options=selected_group.pages,
                format_func=lambda page_id: t(translation_key_for_page(page_id), language),
                key=subpage_key,
            )
        )

    st.session_state[key] = active_page
    return active_page


__all__ = [
    "MAIN_NAVIGATION",
    "legacy_page_label",
    "normalize_page_id",
    "render_header",
    "render_language_selector",
    "render_main_navigation",
    "request_navigation",
]
