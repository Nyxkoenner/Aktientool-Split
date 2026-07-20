from __future__ import annotations

import os
from typing import Any, Protocol

from .translations import DEFAULT_LANGUAGE, normalize_language, translate

SESSION_KEY = "app_language"
ENVIRONMENT_KEY = "AKTIEN_EXPLORER_LANGUAGE"


class SessionStateLike(Protocol):
    """Minimal protocol shared by dicts and Streamlit's SessionStateProxy."""

    def __contains__(self, key: object) -> bool: ...

    def __getitem__(self, key: str) -> Any: ...

    def __setitem__(self, key: str, value: Any) -> None: ...


def language_from_state(state: SessionStateLike | None = None) -> str:
    if state is not None and SESSION_KEY in state:
        return normalize_language(str(state[SESSION_KEY]))
    return normalize_language(os.getenv(ENVIRONMENT_KEY, DEFAULT_LANGUAGE))


def current_language() -> str:
    try:
        import streamlit as st

        return language_from_state(st.session_state)
    except (ImportError, RuntimeError):
        return language_from_state()


def set_language(language: str, state: SessionStateLike | None = None) -> str:
    selected = normalize_language(language)
    if state is not None:
        state[SESSION_KEY] = selected
        return selected
    try:
        import streamlit as st

        st.session_state[SESSION_KEY] = selected
    except (ImportError, RuntimeError):
        pass
    return selected


def t(key: str, language: str | None = None, **values: object) -> str:
    return translate(key, language or current_language(), **values)
