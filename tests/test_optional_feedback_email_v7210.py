from pathlib import Path
from urllib.parse import parse_qs, urlparse

from stock_explorer.ui.pilot_readiness import _build_pilot_feedback_message
from stock_explorer.ui.ux_foundation import build_feedback_mailto


def test_pilot_feedback_message_contains_rating_contact_and_text() -> None:
    message = _build_pilot_feedback_message(
        rating=5,
        message="Die Navigation ist jetzt deutlich verständlicher.",
        contact_email="tester@example.com",
        language="de",
    )

    assert "Bewertung: 5/5" in message
    assert "tester@example.com" in message
    assert "deutlich verständlicher" in message


def test_feedback_mailto_targets_configured_recipient() -> None:
    link = build_feedback_mailto(
        recipient="nykoenner@gmail.com",
        version="7.2.10",
        page_id="pilot_center",
        language="de",
        knowledge_level="beginner",
        category="Bedienung",
        message="Bewertung: 4/5\n\nGutes Pilot-Feedback",
    )
    parsed = urlparse(link)
    query = parse_qs(parsed.query)

    assert parsed.scheme == "mailto"
    assert parsed.path == "nykoenner@gmail.com"
    assert "7.2.10" in query["subject"][0]
    assert "Gutes Pilot-Feedback" in query["body"][0]


def test_pilot_feedback_is_not_saved_locally_and_admin_tab_is_hidden() -> None:
    source = Path("stock_explorer/ui/pilot_readiness.py").read_text(encoding="utf-8")

    assert "store.save_feedback(" not in source
    assert "admin_tab" not in source
    assert "_render_admin" not in source
    assert 't("pilot.feedback.open_email", language)' in source
