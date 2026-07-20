"""Pure domain models and calculations."""

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
    "ReportAnalysis",
    "StructuredCandidate",
    "TextFinding",
    "analyze_report_text",
    "CompanyScenarioSnapshot",
    "HistoricalCalibration",
    "ScenarioOutcome",
    "ScenarioPreset",
    "ScenarioShock",
    "calibrate_history",
    "classify_sector",
    "run_sector_scenario",
    "sector_adjusted_preset",
]
