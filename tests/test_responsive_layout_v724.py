from stock_explorer.domain.ux_preferences import DisplayMode
from stock_explorer.ui.responsive import (
    build_responsive_css,
    is_compact_layout,
    navigation_widget_style,
)


def test_auto_css_contains_mobile_breakpoint_and_touch_targets() -> None:
    css = build_responsive_css(DisplayMode.AUTO)
    assert "@media (max-width: 768px)" in css
    assert "min-height: 44px" in css
    assert 'data-testid="stDataFrame"' in css
    assert "flex-wrap: wrap" in css


def test_compact_css_applies_without_media_query() -> None:
    css = build_responsive_css(DisplayMode.COMPACT)
    assert "@media (max-width: 768px)" not in css
    assert "min-width: min(100%, 19rem)" in css
    assert is_compact_layout(DisplayMode.COMPACT)


def test_desktop_keeps_wide_navigation() -> None:
    css = build_responsive_css(DisplayMode.DESKTOP)
    assert "@media (max-width: 768px)" not in css
    assert navigation_widget_style(DisplayMode.DESKTOP) == "radio"
    assert navigation_widget_style(DisplayMode.AUTO) == "radio"
    assert navigation_widget_style(DisplayMode.COMPACT) == "selectbox"
