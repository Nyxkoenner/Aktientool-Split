from inspect import signature

from stock_explorer.ui.app_shell import render_language_selector


def test_language_selector_uses_independent_widget_key() -> None:
    parameter = signature(render_language_selector).parameters["key"]
    assert parameter.default == "app_language_selector"
