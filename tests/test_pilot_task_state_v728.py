from pathlib import Path

from stock_explorer.ui.pilot_readiness import (
    _set_task_completed,
    _task_is_completed,
    _task_state_key,
    _task_widget_key,
)


def test_pilot_task_state_is_separate_from_streamlit_widget_state() -> None:
    assert _task_state_key("send_feedback") == "pilot_task_state_send_feedback"
    assert _task_widget_key("send_feedback") == "pilot_task_widget_send_feedback"
    assert _task_state_key("send_feedback") != _task_widget_key("send_feedback")


def test_feedback_completion_only_updates_domain_task_state() -> None:
    state: dict[str, object] = {_task_widget_key("send_feedback"): False}

    _set_task_completed("send_feedback", True, state)

    assert _task_is_completed("send_feedback", state) is True
    assert state[_task_widget_key("send_feedback")] is False


def test_feedback_handler_does_not_assign_to_checkbox_widget_key() -> None:
    source = Path("stock_explorer/ui/pilot_readiness.py").read_text(encoding="utf-8")

    assert 'st.session_state[_task_key("send_feedback")] = True' not in source
    assert '_set_task_completed("send_feedback", True, st.session_state)' in source
