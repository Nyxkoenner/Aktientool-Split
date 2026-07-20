from __future__ import annotations

import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from stock_explorer.domain.data_quality import HistoryQualityReport, assess_price_history
from stock_explorer.domain.rl_qlearning import QLearningConfig
from stock_explorer.i18n import current_language, format_number, format_percent, t
from stock_explorer.services.ai_lab_service import (
    AILabPlan,
    AILabResult,
    WalkForwardConfig,
    plan_ai_lab,
    run_ai_lab,
    save_ai_lab_run,
)
from stock_explorer.services.runtime_control import (
    ProgressUpdate,
    RunLimits,
    runtime_profile,
)

LOGGER = logging.getLogger("stock_explorer.ai_lab")
_STRATEGY_ORDER = ["buy_hold", "momentum", "recovery", "combined", "q_learning"]
_PROFILE_IDS = ["quick", "standard", "intensive", "custom"]


@st.cache_data(show_spinner=False, max_entries=16)
def _cached_plan(
    history: pd.DataFrame | pd.Series,
    walk_forward: WalkForwardConfig,
    q_learning: QLearningConfig,
    score_items: tuple[tuple[str, float | None], ...],
) -> AILabPlan:
    return plan_ai_lab(
        history,
        walk_forward=walk_forward,
        q_learning=q_learning,
        current_scores=dict(score_items),
    )


def _company_options(data: pd.DataFrame) -> tuple[list[str], dict[str, str]]:
    frame = data[["ticker_yahoo", "name"]].dropna(subset=["ticker_yahoo"]).drop_duplicates("ticker_yahoo")
    names = frame.set_index("ticker_yahoo")["name"].fillna("").astype(str).to_dict()
    options = sorted(
        frame["ticker_yahoo"].astype(str).tolist(), key=lambda value: names.get(value, value).lower()
    )
    return options, names


def _score_context(row: pd.Series) -> dict[str, float | None]:
    mapping = {
        "quality": row.get("total_score"),
        "value": row.get("value_profile_score", row.get("value_score")),
        "growth": row.get("growth_score"),
        "momentum": row.get("momentum_score"),
        "safety": row.get("safety_score"),
        "deep_value": row.get("special_situation_score"),
    }
    result: dict[str, float | None] = {}
    for key, value in mapping.items():
        numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
        result[key] = float(numeric) if pd.notna(numeric) else None
    return result


def _metrics_frame(result: AILabResult, language: str) -> pd.DataFrame:
    rows = []
    for strategy_id in _STRATEGY_ORDER:
        strategy = result.strategies[strategy_id]
        metrics = strategy.metrics
        rows.append(
            {
                t("ai.column.strategy", language): t(f"ai.strategy.{strategy_id}", language),
                t("ai.column.total_return", language): metrics.total_return_pct,
                t("ai.column.annualized", language): metrics.annualized_return_pct,
                t("ai.column.volatility", language): metrics.annualized_volatility_pct,
                t("ai.column.sharpe", language): metrics.sharpe_ratio,
                t("ai.column.drawdown", language): metrics.max_drawdown_pct,
                t("ai.column.exposure", language): metrics.exposure_pct,
                t("ai.column.trades", language): metrics.trades,
                t("ai.column.turnover", language): metrics.turnover,
            }
        )
    return pd.DataFrame(rows)


def _equity_frame(result: AILabResult, language: str) -> pd.DataFrame:
    frames = []
    for strategy_id in _STRATEGY_ORDER:
        series = result.strategies[strategy_id].equity_curve
        frames.append(
            pd.DataFrame(
                {
                    t("ai.column.date", language): series.index,
                    t("ai.column.equity", language): series.values,
                    t("ai.column.strategy", language): t(f"ai.strategy.{strategy_id}", language),
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


def _load_history(ticker: str) -> pd.DataFrame | pd.Series | None:
    key = f"ai_lab_history_{ticker}"
    cached = st.session_state.get(key)
    if isinstance(cached, (pd.DataFrame, pd.Series)) and not cached.empty:
        return cached
    histories = st.session_state.get("histories", {})
    if isinstance(histories, dict):
        current = histories.get(ticker)
        if isinstance(current, (pd.DataFrame, pd.Series)) and not current.empty:
            return current
    return None


def _trim_history(
    history: pd.DataFrame | pd.Series,
    history_years: int,
) -> pd.DataFrame | pd.Series:
    if history_years <= 0 or history.empty:
        return history.copy()
    result = history.copy()
    result.index = pd.to_datetime(result.index, errors="coerce")
    result = result.loc[~result.index.isna()].sort_index()
    cutoff = pd.Timestamp(result.index.max()) - pd.DateOffset(years=history_years)
    return result.loc[result.index >= cutoff]


def _format_duration(seconds: float, language: str) -> str:
    value = max(float(seconds), 0.0)
    if value < 60:
        return t("ai.duration.seconds", language, value=max(int(round(value)), 1))
    if value < 3600:
        return t("ai.duration.minutes", language, value=max(int(round(value / 60)), 1))
    return t("ai.duration.hours", language, value=round(value / 3600, 1))


def _apply_runtime_profile() -> None:
    profile_id = str(st.session_state.get("ai_runtime_mode", "standard"))
    if profile_id == "custom":
        return
    profile = runtime_profile(profile_id)
    values = {
        "ai_history_years": profile.history_years,
        "ai_training_years": profile.training_years,
        "ai_test_months": profile.test_months,
        "ai_step_months": profile.step_months,
        "ai_episodes": profile.episodes,
        "ai_max_folds": profile.max_folds,
        "ai_max_minutes": profile.max_minutes,
    }
    for key, value in values.items():
        st.session_state[key] = value


def _ensure_runtime_defaults() -> None:
    st.session_state.setdefault("ai_runtime_mode", "standard")
    profile_id = str(st.session_state["ai_runtime_mode"])
    if profile_id not in _PROFILE_IDS:
        profile_id = "standard"
        st.session_state["ai_runtime_mode"] = profile_id
    if profile_id == "custom":
        profile_id = "standard"
    profile = runtime_profile(profile_id)
    defaults = {
        "ai_history_years": profile.history_years,
        "ai_training_years": profile.training_years,
        "ai_test_months": profile.test_months,
        "ai_step_months": profile.step_months,
        "ai_episodes": profile.episodes,
        "ai_max_folds": profile.max_folds,
        "ai_max_minutes": profile.max_minutes,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _quality_label(report: HistoryQualityReport, language: str) -> str:
    return t(f"ai.quality.level.{report.level}", language)


def _render_quality(report: HistoryQualityReport, language: str) -> None:
    columns = st.columns(4)
    columns[0].metric(t("ai.quality.score", language), f"{report.score}/100")
    columns[1].metric(t("ai.quality.level", language), _quality_label(report, language))
    columns[2].metric(t("ai.quality.observations", language), report.observations)
    columns[3].metric(t("ai.quality.years", language), format_number(report.years, 1, language))
    if report.issues:
        labels = [t(f"ai.quality.issue.{issue}", language) for issue in report.issues]
        st.caption(t("ai.quality.issues", language, issues=" · ".join(labels)))


def _render_workload(plan: AILabPlan, max_folds: int, language: str) -> None:
    estimate = plan.estimate
    fraction = min(max(max_folds, 1), estimate.folds) / max(estimate.folds, 1)
    effective_steps = int(round(estimate.training_steps * fraction))
    low = estimate.estimated_seconds_low * fraction
    high = estimate.estimated_seconds_high * fraction
    columns = st.columns(4)
    columns[0].metric(t("ai.workload.folds", language), f"{min(max_folds, estimate.folds)}/{estimate.folds}")
    columns[1].metric(t("ai.workload.steps", language), f"{effective_steps:,}".replace(",", "."))
    columns[2].metric(
        t("ai.workload.estimate", language),
        f"{_format_duration(low, language)} – {_format_duration(high, language)}",
    )
    columns[3].metric(
        t("ai.workload.risk", language),
        t(f"ai.workload.risk.{estimate.risk_level}", language),
    )
    st.caption(t("ai.workload.notice", language))


def render_ai_lab(
    data: pd.DataFrame,
    *,
    market_provider: Any,
    storage_dir: Path,
) -> None:
    language = current_language()
    st.subheader(t("ai.title", language))
    st.caption(t("ai.caption", language))
    st.warning(t("ai.research_warning", language))
    if data is None or data.empty:
        st.info(t("ai.load_data", language))
        return

    options, names = _company_options(data)
    ticker = st.selectbox(
        t("common.select_company", language),
        options,
        format_func=lambda value: f"{names.get(value, value)} ({value})",
        key="ai_lab_ticker",
    )
    row = data.loc[data["ticker_yahoo"].astype(str) == ticker].iloc[0]
    history = _load_history(ticker)

    source_columns = st.columns([2, 1])
    source_columns[0].caption(t("ai.history_hint", language))
    if source_columns[1].button(t("ai.load_max_history", language), key="ai_load_max_history"):
        try:
            with st.spinner(t("ai.loading_history", language)):
                downloaded = market_provider.download_price_histories((ticker,), period="max")
            loaded = downloaded.get(ticker)
            if isinstance(loaded, pd.DataFrame) and not loaded.empty:
                st.session_state[f"ai_lab_history_{ticker}"] = loaded
                history = loaded
                _cached_plan.clear()
                st.success(t("ai.history_loaded", language, count=len(loaded)))
            else:
                st.error(t("ai.history_error", language))
        except Exception as error:
            LOGGER.exception("Maximum history download failed for %s", ticker)
            st.error(t("ai.history_error_detail", language, error=error))

    if history is None or len(history) < 260:
        st.info(t("ai.no_history", language))
        return

    _ensure_runtime_defaults()
    st.selectbox(
        t("ai.runtime_mode", language),
        _PROFILE_IDS,
        format_func=lambda value: t(f"ai.runtime_mode.{value}", language),
        key="ai_runtime_mode",
        on_change=_apply_runtime_profile,
    )

    with st.expander(t("ai.settings", language), expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        history_years = col1.selectbox(
            t("ai.history_years", language),
            [5, 10, 15, 20, 0],
            format_func=lambda value: (
                t("ai.history_all", language) if value == 0 else t("ai.history_value", language, years=value)
            ),
            key="ai_history_years",
        )
        training_years = col2.slider(t("ai.training_years", language), 1, 8, key="ai_training_years")
        test_months = col3.select_slider(
            t("ai.test_months", language),
            options=[3, 6, 12],
            key="ai_test_months",
        )
        step_options = [value for value in (3, 6, 12) if value >= int(test_months)]
        if st.session_state.get("ai_step_months") not in step_options:
            st.session_state["ai_step_months"] = step_options[0]
        step_months = col4.select_slider(
            t("ai.step_months", language), options=step_options, key="ai_step_months"
        )

        col5, col6, col7 = st.columns(3)
        episodes = col5.slider(t("ai.episodes", language), 25, 1200, 25, key="ai_episodes")
        costs = col6.slider(t("ai.costs", language), 0.0, 50.0, 10.0, 1.0, key="ai_costs")
        downside_penalty = col7.slider(
            t("ai.downside_penalty", language),
            0.0,
            2.0,
            0.25,
            0.05,
            key="ai_downside_penalty",
        )

        col8, col9, col10 = st.columns(3)
        max_folds = col8.number_input(
            t("ai.max_folds", language), min_value=1, max_value=200, step=1, key="ai_max_folds"
        )
        max_minutes = col9.number_input(
            t("ai.max_minutes", language), min_value=1, max_value=240, step=1, key="ai_max_minutes"
        )
        seed = col10.number_input(t("ai.seed", language), min_value=0, max_value=1_000_000, value=42, step=1)
        st.caption(t("ai.limits_notice", language))

    selected_history = _trim_history(history, int(history_years))
    quality = assess_price_history(selected_history)
    with st.expander(t("ai.quality.title", language), expanded=quality.level != "good"):
        _render_quality(quality, language)

    walk_forward = WalkForwardConfig(
        training_years=int(training_years),
        test_months=int(test_months),
        step_months=int(step_months),
        min_training_days=max(int(training_years * 180), 180),
    )
    q_learning = QLearningConfig(
        episodes=int(episodes),
        transaction_cost_bps=float(costs),
        downside_penalty=float(downside_penalty),
        seed=int(seed),
    )
    score_context = _score_context(row)
    try:
        plan = _cached_plan(
            selected_history,
            walk_forward,
            q_learning,
            tuple(sorted(score_context.items())),
        )
    except Exception as error:
        st.error(t("ai.plan_error", language, error=error))
        return

    st.subheader(t("ai.workload.title", language))
    _render_workload(plan, int(max_folds), language)
    if st.button(t("ai.clear_cache", language), key="ai_clear_cache"):
        _cached_plan.clear()
        st.success(t("ai.cache_cleared", language))

    run_key = f"ai_lab_result_{ticker}"
    running_key = f"ai_lab_running_{ticker}"
    is_running = bool(st.session_state.get(running_key, False))
    if st.button(t("ai.run", language), type="primary", key="ai_run", disabled=is_running):
        progress_bar = st.progress(0.0)
        progress_text = st.empty()

        def update_progress(update: ProgressUpdate) -> None:
            progress_bar.progress(update.fraction)
            if update.fold is None:
                progress_text.caption(t(f"ai.progress.{update.stage}", language))
            else:
                progress_text.caption(
                    t(
                        f"ai.progress.{update.stage}",
                        language,
                        fold=update.fold,
                        total=update.total_folds,
                        elapsed=_format_duration(update.elapsed_seconds, language),
                    )
                )

        st.session_state[running_key] = True
        try:
            generated_result = run_ai_lab(
                selected_history,
                walk_forward=walk_forward,
                q_learning=q_learning,
                current_scores=score_context,
                plan=plan,
                limits=RunLimits(
                    max_seconds=float(max_minutes) * 60.0,
                    max_folds=int(max_folds),
                ),
                progress_callback=update_progress,
            )
            st.session_state[run_key] = generated_result
            progress_bar.progress(1.0)
        except Exception as error:
            LOGGER.exception("AI lab run failed for %s", ticker)
            st.error(t("ai.error", language, error=error))
        finally:
            st.session_state[running_key] = False

    stored_result = st.session_state.get(run_key)
    if not isinstance(stored_result, AILabResult):
        st.info(t("ai.run_prompt", language))
        return
    result = stored_result

    if not result.completed:
        reason = result.stop_reason or "unknown"
        st.warning(
            t(
                "ai.partial_result",
                language,
                completed=result.completed_folds,
                planned=result.planned_folds,
                reason=t(f"ai.stop_reason.{reason}", language),
            )
        )

    best_id = max(
        _STRATEGY_ORDER,
        key=lambda item: result.strategies[item].metrics.total_return_pct,
    )
    metric_columns = st.columns(6)
    metric_columns[0].metric(
        t("ai.metric.folds", language), f"{result.completed_folds}/{result.planned_folds}"
    )
    metric_columns[1].metric(
        t("ai.metric.period", language),
        f"{result.out_of_sample_start:%Y-%m-%d} – {result.out_of_sample_end:%Y-%m-%d}",
    )
    metric_columns[2].metric(t("ai.metric.best", language), t(f"ai.strategy.{best_id}", language))
    metric_columns[3].metric(t("ai.metric.q_states", language), result.q_states)
    metric_columns[4].metric(
        t("ai.metric.q_return", language),
        format_percent(result.strategies["q_learning"].metrics.total_return_pct, 1, language, signed=True),
    )
    metric_columns[5].metric(
        t("ai.metric.runtime", language), _format_duration(result.elapsed_seconds, language)
    )

    st.subheader(t("ai.comparison", language))
    metrics = _metrics_frame(result, language)
    percent_columns = [
        t("ai.column.total_return", language),
        t("ai.column.annualized", language),
        t("ai.column.volatility", language),
        t("ai.column.drawdown", language),
        t("ai.column.exposure", language),
    ]
    formats = {column: "{:+.1f}%" for column in percent_columns}
    formats[t("ai.column.sharpe", language)] = "{:.2f}"
    formats[t("ai.column.turnover", language)] = "{:.1f}x"
    st.dataframe(metrics.style.format(formats, na_rep="–"), width="stretch", hide_index=True)

    equity_frame = _equity_frame(result, language)
    date_col = t("ai.column.date", language)
    equity_col = t("ai.column.equity", language)
    strategy_col = t("ai.column.strategy", language)
    chart = (
        alt.Chart(equity_frame)
        .mark_line()
        .encode(
            x=alt.X(f"{date_col}:T", title=t("ai.column.date", language)),
            y=alt.Y(f"{equity_col}:Q", title=t("ai.chart_equity", language)),
            color=alt.Color(f"{strategy_col}:N", title=t("ai.column.strategy", language)),
            tooltip=[date_col, strategy_col, alt.Tooltip(f"{equity_col}:Q", format=".2f")],
        )
        .properties(height=380)
    )
    st.altair_chart(chart, width="stretch")

    st.subheader(t("ai.folds", language))
    fold_frame = pd.DataFrame([asdict(fold) for fold in result.folds])
    fold_frame = fold_frame.rename(
        columns={
            "fold": t("ai.fold.number", language),
            "train_start": t("ai.fold.train_start", language),
            "train_end": t("ai.fold.train_end", language),
            "test_start": t("ai.fold.test_start", language),
            "test_end": t("ai.fold.test_end", language),
            "train_rows": t("ai.fold.train_rows", language),
            "test_rows": t("ai.fold.test_rows", language),
            "q_learning_return_pct": t("ai.fold.q_return", language),
            "buy_hold_return_pct": t("ai.fold.buy_hold", language),
            "momentum_return_pct": t("ai.fold.momentum", language),
        }
    )
    st.dataframe(fold_frame, width="stretch", hide_index=True)

    with st.expander(t("ai.explanation", language)):
        st.markdown(t("ai.explanation_text", language))
        action_frame = pd.DataFrame(
            {
                t("ai.action", language): [
                    t("ai.action.sell", language),
                    t("ai.action.hold", language),
                    t("ai.action.buy", language),
                ],
                t("ai.action.count", language): [
                    result.q_action_counts.get("sell", 0),
                    result.q_action_counts.get("hold", 0),
                    result.q_action_counts.get("buy", 0),
                ],
            }
        )
        st.dataframe(action_frame, width="stretch", hide_index=True)
        st.caption(t("ai.no_fundamental_leakage", language))
        st.json({key: format_number(value, 1, language) for key, value in score_context.items()})

    parameters = {
        "runtime_mode": st.session_state.get("ai_runtime_mode"),
        "history_years": history_years,
        "training_years": training_years,
        "test_months": test_months,
        "step_months": step_months,
        "episodes": episodes,
        "transaction_cost_bps": costs,
        "downside_penalty": downside_penalty,
        "max_folds": max_folds,
        "max_minutes": max_minutes,
        "seed": int(seed),
    }
    if st.button(t("ai.save", language), key="ai_save_run"):
        path = save_ai_lab_run(result, ticker=ticker, directory=storage_dir, parameters=parameters)
        st.success(t("ai.saved", language, path=path))

    st.caption(t("ai.disclaimer", language))
