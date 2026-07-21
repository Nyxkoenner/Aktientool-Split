from pathlib import Path

from stock_explorer.ui.guided_analysis import GUIDED_ANALYSIS_STEPS
from stock_explorer.ui.navigation_model import all_grouped_pages


def test_guided_analysis_has_reproducible_five_step_order() -> None:
    assert [step.number for step in GUIDED_ANALYSIS_STEPS] == [1, 2, 3, 4, 5]
    assert [step.page_id for step in GUIDED_ANALYSIS_STEPS] == [
        "company_profiles",
        "fundamentals",
        "analysis",
        "news",
        "scenarios",
    ]
    assert len({step.page_id for step in GUIDED_ANALYSIS_STEPS}) == 5
    assert all(step.page_id in all_grouped_pages() for step in GUIDED_ANALYSIS_STEPS)


def test_runtime_registers_start_and_guided_hub_before_dispatch() -> None:
    source = Path("stock_explorer/app_runtime.py").read_text(encoding="utf-8")

    assert '"start": lambda: render_start_page(data)' in source
    assert '"analysis_hub": lambda: render_guided_analysis_hub(data)' in source
    assert 'if active_page in {"start", "pilot_center"}:' in source
    assert 't("ux.home.load_hint", language)' in source
