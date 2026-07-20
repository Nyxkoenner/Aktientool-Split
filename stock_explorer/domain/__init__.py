"""Pure domain models and calculations."""

from .market_reaction import compute_market_reactions
from .news_intelligence import (
    ImpactAssessment,
    SourceAssessment,
    assess_source,
    assess_stock_impact,
    classify_detailed_event,
    cluster_news,
    enrich_news_intelligence,
    source_health_summary,
)
from .report_analysis import ReportAnalysis, StructuredCandidate, TextFinding, analyze_report_text
from .scenario_calibration import HistoricalCalibration, calibrate_history
from .scenario_models import (
    CompanyScenarioSnapshot,
    ScenarioOutcome,
    ScenarioPreset,
    ScenarioShock,
    classify_sector,
    run_sector_scenario,
    sector_adjusted_preset,
)

__all__ = [
    "CompanyScenarioSnapshot",
    "HistoricalCalibration",
    "ImpactAssessment",
    "ReportAnalysis",
    "ScenarioOutcome",
    "ScenarioPreset",
    "ScenarioShock",
    "SourceAssessment",
    "StructuredCandidate",
    "TextFinding",
    "analyze_report_text",
    "assess_source",
    "assess_stock_impact",
    "calibrate_history",
    "classify_detailed_event",
    "classify_sector",
    "cluster_news",
    "compute_market_reactions",
    "enrich_news_intelligence",
    "run_sector_scenario",
    "sector_adjusted_preset",
    "source_health_summary",
]
