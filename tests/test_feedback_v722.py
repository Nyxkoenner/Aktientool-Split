from urllib.parse import parse_qs, unquote, urlparse

from stock_explorer.domain.ux_preferences import KnowledgeLevel
from stock_explorer.ui.ux_foundation import build_feedback_mailto, quality_key_from_coverage


def test_feedback_mailto_contains_safe_context() -> None:
    link = build_feedback_mailto(
        recipient="nykoenner@gmail.com",
        version="7.2.2",
        page_id="ai_lab",
        language="de",
        knowledge_level=KnowledgeLevel.BEGINNER,
        category="Verbesserungsidee",
        message="Bitte die Erklärung vereinfachen.",
    )

    parsed = urlparse(link)
    query = parse_qs(parsed.query)
    subject = unquote(query["subject"][0])
    body = unquote(query["body"][0])

    assert parsed.scheme == "mailto"
    assert parsed.path == "nykoenner@gmail.com"
    assert "V7.2.2" in subject
    assert "Bereich: ai_lab" in body
    assert "Wissensmodus: beginner" in body
    assert "Portfolio-, Dokument- und Modelldaten wurden nicht automatisch angehängt" in body


def test_coverage_quality_bands_are_explicit() -> None:
    assert quality_key_from_coverage(None) == "unknown"
    assert quality_key_from_coverage(70.0) == "low"
    assert quality_key_from_coverage(75.0) == "medium"
    assert quality_key_from_coverage(95.0) == "high"
