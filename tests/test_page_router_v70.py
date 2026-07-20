from __future__ import annotations

import pytest

from stock_explorer.ui.page_router import UnknownPageError, dispatch_page


def test_router_dispatches_requested_page() -> None:
    calls: list[str] = []

    selected = dispatch_page(
        "analysis",
        {
            "overview": lambda: calls.append("overview"),
            "analysis": lambda: calls.append("analysis"),
        },
    )

    assert selected == "analysis"
    assert calls == ["analysis"]


def test_router_uses_overview_fallback() -> None:
    calls: list[str] = []

    selected = dispatch_page("unknown", {"overview": lambda: calls.append("overview")})

    assert selected == "overview"
    assert calls == ["overview"]


def test_router_raises_when_fallback_is_missing() -> None:
    with pytest.raises(UnknownPageError):
        dispatch_page("unknown", {})
