"""Responsive Layout-Grundlage für Desktop, Tablet und Smartphone."""

from __future__ import annotations

from typing import Literal

import streamlit as st

from stock_explorer.domain.ux_preferences import (
    DisplayMode,
    display_mode_from_state,
    normalize_display_mode,
    set_display_mode,
)
from stock_explorer.i18n import current_language, t

_DISPLAY_WIDGET_KEY = "display_mode_selector"


def current_display_mode() -> DisplayMode:
    """Liest den aktuellen Anzeigemodus aus dem Streamlit-Session-State."""
    return display_mode_from_state(st.session_state)


def is_compact_layout(mode: DisplayMode | str | None = None) -> bool:
    """Gibt zurück, ob die explizit kompakte Darstellung aktiv ist."""
    selected = current_display_mode() if mode is None else normalize_display_mode(mode)
    return selected == DisplayMode.COMPACT


def navigation_widget_style(mode: DisplayMode | str) -> Literal["radio", "selectbox"]:
    """Wählt ein breites oder kompaktes Navigations-Widget."""
    return "selectbox" if normalize_display_mode(mode) == DisplayMode.COMPACT else "radio"


def _apply_display_choice(widget_key: str) -> None:
    choice = st.session_state.get(widget_key)
    if choice is not None:
        set_display_mode(str(choice), st.session_state)


def render_display_mode_selector(
    *,
    language: str | None = None,
    key: str = _DISPLAY_WIDGET_KEY,
) -> DisplayMode:
    """Rendert Auto-, Kompakt- und Desktopdarstellung mit getrenntem State-Key."""
    selected_language = language or current_language()
    selected = current_display_mode()
    option_values = [mode.value for mode in DisplayMode]

    if st.session_state.get(key) not in option_values:
        st.session_state[key] = selected.value

    choice = st.selectbox(
        t("ux.display.label", selected_language),
        options=option_values,
        format_func=lambda value: t(f"ux.display.{value}", selected_language),
        key=key,
        on_change=_apply_display_choice,
        args=(key,),
        help=t("ux.display.help", selected_language),
    )
    normalized = normalize_display_mode(choice)
    if display_mode_from_state(st.session_state) != normalized:
        set_display_mode(normalized, st.session_state)
    st.caption(t(f"ux.display.caption.{normalized.value}", selected_language))
    return normalized


def build_responsive_css(mode: DisplayMode | str) -> str:
    """Erzeugt CSS für Touch-Ziele, Tabellen und mobile Umbrüche."""
    selected = normalize_display_mode(mode)
    compact_globally = selected == DisplayMode.COMPACT
    mobile_rules = """
[data-testid="stAppViewContainer"] .main .block-container {
    padding-left: 0.85rem;
    padding-right: 0.85rem;
    padding-top: 1rem;
}
[data-testid="stHorizontalBlock"] {
    flex-wrap: wrap;
    gap: 0.7rem;
}
[data-testid="stHorizontalBlock"] > [data-testid="column"] {
    min-width: min(100%, 19rem) !important;
    flex: 1 1 100% !important;
    width: 100% !important;
}
[data-testid="stMetric"] {
    padding: 0.75rem;
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-radius: 0.7rem;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
    overflow-x: auto;
    max-width: 100%;
}
[data-testid="stDataFrame"] iframe {
    min-width: 38rem;
}
.stTabs [data-baseweb="tab-list"] {
    overflow-x: auto;
    flex-wrap: nowrap;
    scrollbar-width: thin;
}
.stTabs [data-baseweb="tab"] {
    min-width: max-content;
}
div[role="radiogroup"] {
    flex-wrap: wrap;
    gap: 0.35rem 0.8rem;
}
.stButton > button,
.stDownloadButton > button,
[data-testid="stLinkButton"] a {
    min-height: 44px;
    width: 100%;
}
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
textarea {
    min-height: 44px;
}
[data-testid="stExpander"] details > summary {
    min-height: 44px;
}
h1 { font-size: clamp(1.65rem, 8vw, 2.5rem) !important; }
h2 { font-size: clamp(1.35rem, 6vw, 2rem) !important; }
h3 { font-size: clamp(1.1rem, 5vw, 1.55rem) !important; }
""".strip()

    base_rules = """
[data-testid="stDataFrame"], [data-testid="stTable"] {
    border-radius: 0.55rem;
}
[data-testid="stMetric"] label {
    line-height: 1.2;
}
.stButton > button,
.stDownloadButton > button,
[data-testid="stLinkButton"] a {
    touch-action: manipulation;
}
""".strip()

    if compact_globally:
        responsive_rules = mobile_rules
    elif selected == DisplayMode.AUTO:
        responsive_rules = f"@media (max-width: 768px) {{\n{mobile_rules}\n}}"
    else:
        responsive_rules = ""

    return f"<style>\n{base_rules}\n{responsive_rules}\n</style>"


def apply_responsive_layout(mode: DisplayMode | str | None = None) -> DisplayMode:
    """Injiziert die zum Anzeigemodus passenden responsiven Styles."""
    selected = current_display_mode() if mode is None else normalize_display_mode(mode)
    st.markdown(build_responsive_css(selected), unsafe_allow_html=True)
    return selected


__all__ = [
    "apply_responsive_layout",
    "build_responsive_css",
    "current_display_mode",
    "is_compact_layout",
    "navigation_widget_style",
    "render_display_mode_selector",
]
