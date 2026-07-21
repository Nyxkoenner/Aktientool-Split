from __future__ import annotations

from stock_explorer.services.pilot_store import PilotStore, verify_admin_pin


def test_pilot_store_saves_feedback_and_builds_summary(tmp_path) -> None:
    store = PilotStore(tmp_path / "pilot")
    feedback = store.save_feedback(
        category="usability",
        rating=4,
        message="Die Navigation war verständlich, aber die Tabelle ist zu breit.",
        contact_email="tester@example.com",
        page_id="pilot_center",
        app_version="7.2.7",
        language="de",
        knowledge_level="beginner",
        display_mode="compact",
        session_id="session-1",
    )
    store.save_event(
        event_type="page_view",
        page_id="pilot_center",
        app_version="7.2.7",
        language="de",
        knowledge_level="beginner",
        display_mode="compact",
        session_id="session-1",
        metadata={"action": "open", "portfolio_value": "must-not-be-stored"},
    )

    assert feedback.reference_id.startswith("FB-")
    summary = store.summary()
    assert summary.feedback_count == 1
    assert summary.event_count == 1
    assert summary.average_rating == 4.0
    assert summary.category_counts == {"usability": 1}
    assert summary.page_counts == {"pilot_center": 1}

    event = store.event_records()[0]
    assert event["metadata"] == {"action": "open"}
    assert b"tester@example.com" in store.feedback_csv_bytes()


def test_pilot_store_rejects_empty_feedback_and_invalid_rating(tmp_path) -> None:
    store = PilotStore(tmp_path)
    common = {
        "category": "idea",
        "contact_email": "",
        "page_id": "start",
        "app_version": "7.2.7",
        "language": "de",
        "knowledge_level": "intermediate",
        "display_mode": "auto",
        "session_id": "session-2",
    }

    try:
        store.save_feedback(rating=4, message="x", **common)
    except ValueError as exc:
        assert "mindestens drei" in str(exc)
    else:
        raise AssertionError("Zu kurzes Feedback muss abgelehnt werden.")

    try:
        store.save_feedback(rating=7, message="Ausreichend langer Text", **common)
    except ValueError as exc:
        assert "zwischen 1 und 5" in str(exc)
    else:
        raise AssertionError("Ungültige Bewertungen müssen abgelehnt werden.")


def test_admin_pin_requires_a_configured_secret() -> None:
    assert verify_admin_pin("1234", None) is False
    assert verify_admin_pin("1234", "1234") is True
    assert verify_admin_pin("123", "1234") is False
