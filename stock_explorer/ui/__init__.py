"""Streamlit-Oberflächenmodule des Aktien Explorers."""

from .portfolio_simulation import render_portfolio_simulation
from .profile_automation import render_profile_automation
from .scenarios import render_scenario_engine
from .source_monitor import render_source_monitor

__all__ = [
    "render_portfolio_simulation",
    "render_profile_automation",
    "render_scenario_engine",
    "render_source_monitor",
]
