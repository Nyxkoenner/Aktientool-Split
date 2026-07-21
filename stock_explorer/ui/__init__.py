"""Streamlit-Oberflächenmodule des Aktien Explorers."""

from .ai_lab import render_ai_lab
from .annual_report_automation import render_annual_report_automation
from .app_shell import (
    MAIN_NAVIGATION,
    legacy_page_label,
    normalize_page_id,
    render_header,
    render_language_selector,
    render_main_navigation,
    request_navigation,
)
from .company_select import company_selectbox
from .guided_analysis import (
    GUIDED_ANALYSIS_STEPS,
    render_analysis_next_steps,
    render_guided_analysis_hub,
    render_start_page,
)
from .news_intelligence import render_news_intelligence
from .page_router import UnknownPageError, dispatch_page
from .portfolio_simulation import render_portfolio_simulation
from .profile_automation import render_profile_automation
from .responsive import (
    apply_responsive_layout,
    build_responsive_css,
    current_display_mode,
    is_compact_layout,
    navigation_widget_style,
    render_display_mode_selector,
)
from .scenarios import render_scenario_engine
from .sidebar import SidebarCallbacks, render_sidebar
from .source_monitor import render_source_monitor
from .ux_foundation import (
    DataTrustSnapshot,
    build_feedback_mailto,
    current_knowledge_level,
    quality_key_from_coverage,
    render_data_trust_panel,
    render_feedback_panel,
    render_glossary_panel,
    render_knowledge_selector,
    render_page_guidance,
)

__all__ = [
    "GUIDED_ANALYSIS_STEPS",
    "render_analysis_next_steps",
    "render_guided_analysis_hub",
    "render_start_page",
    "request_navigation",
    "render_page_guidance",
    "render_knowledge_selector",
    "render_glossary_panel",
    "render_feedback_panel",
    "render_data_trust_panel",
    "quality_key_from_coverage",
    "current_knowledge_level",
    "build_feedback_mailto",
    "DataTrustSnapshot",
    "apply_responsive_layout",
    "build_responsive_css",
    "current_display_mode",
    "is_compact_layout",
    "navigation_widget_style",
    "render_display_mode_selector",
    "MAIN_NAVIGATION",
    "SidebarCallbacks",
    "UnknownPageError",
    "company_selectbox",
    "dispatch_page",
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
    "render_sidebar",
    "render_ai_lab",
]
