"""Streamlit-Oberflächenmodule des Aktien Explorers."""

from .annual_report_automation import render_annual_report_automation
from .app_shell import (
    MAIN_NAVIGATION,
    legacy_page_label,
    normalize_page_id,
    render_header,
    render_language_selector,
    render_main_navigation,
)
from .news_intelligence import render_news_intelligence
from .portfolio_simulation import render_portfolio_simulation
from .profile_automation import render_profile_automation
from .scenarios import render_scenario_engine
from .source_monitor import render_source_monitor

__all__ = [
    "MAIN_NAVIGATION",
    "legacy_page_label",
    "normalize_page_id",
    "render_annual_report_automation",
    "render_header",
    "render_language_selector",
    "render_main_navigation",
    "render_news_intelligence",
    "render_portfolio_simulation",
    "render_profile_automation",
    "render_scenario_engine",
    "render_source_monitor",
]
