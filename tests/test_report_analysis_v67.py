from stock_explorer.domain.report_analysis import analyze_report_text

REPORT_TEXT = """
Annual Report 2025

Business Overview
Example Group develops industrial software and services for global customers. The company earns recurring
subscription revenue and provides implementation services.

Operating Segments
Cloud Software 55%
Professional Services EUR 420 million 30%
Hardware 15%

Geographical Information
Europe 48%
North America USD 600 million 37%
Asia-Pacific 15%

Risk Factors
Cyber attacks and data breaches could adversely affect operations and customer trust.
Higher interest rates and refinancing requirements may increase financing costs.
Raw material and supplier shortages could disrupt production.

Growth Strategy and Opportunities
The company expects growth from cloud expansion, innovation and higher market share.

Supply Chain and Customer Concentration
A single supplier provides critical components and two key customers represent a material share of revenue.

Brands and Subsidiaries
Example Cloud
Example Services GmbH
"""


def test_report_analysis_detects_core_profile_information() -> None:
    analysis = analyze_report_text(REPORT_TEXT)

    assert analysis.fiscal_year == 2025
    assert analysis.report_type == "Annual Report"
    assert analysis.language == "en"
    assert analysis.coverage_pct >= 75
    assert len(analysis.risks) >= 2
    assert any(item.label == "Cloud Software" for item in analysis.segments)
    assert any("Europe" in item.label for item in analysis.regions)
    assert analysis.opportunities
    assert analysis.dependencies
    assert "Example Cloud" in analysis.brands_and_subsidiaries


def test_report_analysis_serialization_roundtrip() -> None:
    analysis = analyze_report_text(REPORT_TEXT)
    restored = type(analysis).from_dict(analysis.to_dict())

    assert restored.fiscal_year == analysis.fiscal_year
    assert restored.segments[0].label == analysis.segments[0].label
    assert restored.risks[0].evidence == analysis.risks[0].evidence
