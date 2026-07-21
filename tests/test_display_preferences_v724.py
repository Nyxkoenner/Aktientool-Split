from stock_explorer.domain.ux_preferences import (
    DEFAULT_DISPLAY_MODE,
    DisplayMode,
    display_mode_from_state,
    normalize_display_mode,
    set_display_mode,
)


def test_display_mode_defaults_and_normalization() -> None:
    assert normalize_display_mode(None) == DEFAULT_DISPLAY_MODE
    assert normalize_display_mode("compact") == DisplayMode.COMPACT
    assert normalize_display_mode("DESKTOP") == DisplayMode.DESKTOP
    assert normalize_display_mode("unsupported") == DisplayMode.AUTO


def test_display_mode_round_trip_through_state() -> None:
    state: dict[str, object] = {}
    selected = set_display_mode(DisplayMode.COMPACT, state)
    assert selected == DisplayMode.COMPACT
    assert state["display_mode"] == "compact"
    assert display_mode_from_state(state) == DisplayMode.COMPACT
