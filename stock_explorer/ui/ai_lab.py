from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from stock_explorer.domain.rl_qlearning import QLearningConfig
from stock_explorer.i18n import current_language, format_number, format_percent, t
from stock_explorer.services.ai_lab_service import (
    AILabResult,
    WalkForwardConfig,
    run_ai_lab,
    save_ai_lab_run,
)

_STRATEGY_ORDER = ["buy_hold", "momentum", "recovery", "combined", "q_learning"]


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


def _load_history(ticker: str, market_provider: Any) -> pd.DataFrame | pd.Series | None:
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
    history = _load_history(ticker, market_provider)

    source_columns = st.columns([2, 1])
    source_columns[0].caption(t("ai.history_hint", language))
    if source_columns[1].button(t("ai.load_max_history", language), key="ai_load_max_history"):
        with st.spinner(t("ai.loading_history", language)):
            downloaded = market_provider.download_price_histories((ticker,), period="max")
        loaded = downloaded.get(ticker)
        if isinstance(loaded, pd.DataFrame) and not loaded.empty:
            st.session_state[f"ai_lab_history_{ticker}"] = loaded
            history = loaded
            st.success(t("ai.history_loaded", language, count=len(loaded)))
        else:
            st.error(t("ai.history_error", language))

    if history is None or len(history) < 260:
        st.info(t("ai.no_history", language))
        return

    with st.expander(t("ai.settings", language), expanded=True):
        col1, col2, col3 = st.columns(3)
        training_years = col1.slider(t("ai.training_years", language), 1, 6, 3, key="ai_training_years")
        test_months = col2.select_slider(
            t("ai.test_months", language),
            options=[3, 6, 12],
            value=6,
            key="ai_test_months",
        )
        step_options = [value for value in (3, 6, 12) if value >= int(test_months)]
        current_step = st.session_state.get("ai_step_months")
        if current_step not in step_options:
            st.session_state["ai_step_months"] = step_options[0]
        step_months = col3.select_slider(
            t("ai.step_months", language),
            options=step_options,
            key="ai_step_months",
        )
        col4, col5, col6 = st.columns(3)
        episodes = col4.slider(t("ai.episodes", language), 50, 1200, 300, 50, key="ai_episodes")
        costs = col5.slider(t("ai.costs", language), 0.0, 50.0, 10.0, 1.0, key="ai_costs")
        downside_penalty = col6.slider(
            t("ai.downside_penalty", language), 0.0, 2.0, 0.25, 0.05, key="ai_downside_penalty"
        )
        seed = st.number_input(t("ai.seed", language), min_value=0, max_value=1_000_000, value=42, step=1)

    run_key = f"ai_lab_result_{ticker}"
    if st.button(t("ai.run", language), type="primary", key="ai_run"):
        with st.spinner(t("ai.running", language)):
            try:
                generated_result = run_ai_lab(
                    history,
                    walk_forward=WalkForwardConfig(
                        training_years=int(training_years),
                        test_months=int(test_months),
                        step_months=int(step_months),
                        min_training_days=max(int(training_years * 180), 180),
                    ),
                    q_learning=QLearningConfig(
                        episodes=int(episodes),
                        transaction_cost_bps=float(costs),
                        downside_penalty=float(downside_penalty),
                        seed=int(seed),
                    ),
                    current_scores=_score_context(row),
                )
                st.session_state[run_key] = generated_result
            except Exception as error:
                st.error(t("ai.error", language, error=error))

    stored_result = st.session_state.get(run_key)
    if not isinstance(stored_result, AILabResult):
        st.info(t("ai.run_prompt", language))
        return
    result = stored_result

    best_id = max(
        _STRATEGY_ORDER,
        key=lambda item: result.strategies[item].metrics.total_return_pct,
    )
    metric_columns = st.columns(5)
    metric_columns[0].metric(t("ai.metric.folds", language), len(result.folds))
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
        score_context = _score_context(row)
        st.caption(t("ai.no_fundamental_leakage", language))
        st.json({key: format_number(value, 1, language) for key, value in score_context.items()})

    parameters = {
        "training_years": training_years,
        "test_months": test_months,
        "step_months": step_months,
        "episodes": episodes,
        "transaction_cost_bps": costs,
        "downside_penalty": downside_penalty,
        "seed": int(seed),
    }
    if st.button(t("ai.save", language), key="ai_save_run"):
        path = save_ai_lab_run(result, ticker=ticker, directory=storage_dir, parameters=parameters)
        st.success(t("ai.saved", language, path=path))

    st.caption(t("ai.disclaimer", language))
