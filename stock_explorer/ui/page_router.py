"""Expliziter Seiten-Router ohne lange ``if/elif``-Kette."""

from __future__ import annotations

from collections.abc import Callable, Mapping

PageRenderer = Callable[[], None]


class UnknownPageError(KeyError):
    """Wird ausgelöst, wenn Navigation und registrierte Seiten auseinanderlaufen."""


def dispatch_page(
    active_page: str,
    routes: Mapping[str, PageRenderer],
    *,
    fallback_page: str = "overview",
) -> str:
    """Rendert eine Seite und liefert die tatsächlich verwendete Seiten-ID zurück."""
    selected = active_page if active_page in routes else fallback_page
    renderer = routes.get(selected)
    if renderer is None:
        raise UnknownPageError(
            f"Weder die Seite {active_page!r} noch die Fallback-Seite {fallback_page!r} ist registriert."
        )
    renderer()
    return selected


__all__ = ["PageRenderer", "UnknownPageError", "dispatch_page"]
