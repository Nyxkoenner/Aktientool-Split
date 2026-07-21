from stock_explorer.domain.pilot_models import safe_event_metadata, sanitize_text


def test_event_metadata_has_an_explicit_allowlist() -> None:
    metadata = safe_event_metadata(
        {
            "action": "open_analysis",
            "target": "fundamentals",
            "portfolio_value": "250000",
            "uploaded_document": "annual_report.pdf",
        }
    )

    assert metadata == {"action": "open_analysis", "target": "fundamentals"}


def test_pilot_text_is_bounded_and_control_characters_are_removed() -> None:
    assert sanitize_text(" a\x00b ") == "a b"
    assert len(sanitize_text("x" * 200, max_length=40)) == 40
