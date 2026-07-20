from __future__ import annotations

from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from stock_explorer.domain.scenario_models import ScenarioShock
from stock_explorer.i18n import current_language, format_currency, format_number, format_percent, t
from stock_explorer.services.scenario_service import analyze_scenario, snapshot_from_row

PRESET_IDS = [
    "base",
    "recession",
    "rate_hike",
    "inflation",
    "margin_pressure",
    "dividend_cut",
    "deleveraging",
    "valuation_normalization",
    "currency_shock",
    "custom",
]


def _company_options(data: pd.DataFrame) -> tuple[list[str], dict[str, str]]:
    frame = data[["ticker_yahoo", "name"]].dropna(subset=["ticker_yahoo"]).drop_duplicates("ticker_yahoo")
    names = frame.set_index("ticker_yahoo")["name"].fillna("").astype(str).to_dict()
    options = sorted(
        frame["ticker_yahoo"].astype(str).tolist(),
        key=lambda item: names.get(item, item).lower(),
    )
    return options, names


def _history_for_ticker(ticker: str) -> pd.DataFrame | pd.Series | None:
    histories = st.session_state.get("histories", {})
    if isinstance(histories, dict):
        return histories.get(ticker)
    return None


def _translated_codes(prefix: str, codes: tuple[str, ...], language: str) -> list[str]:
    return [t(f"scenario.{prefix}.{code}", language) for code in codes]


def _outcome_frame(analysis: Any, language: str, currency: str) -> pd.DataFrame:
    rows = []
    for label_key, outcome in (
        ("scenario.weak", analysis.weak),
        ("scenario.base", analysis.base),
        ("scenario.strong", analysis.strong),
    ):
        rows.append(
            {
                t("scenario.column.scenario", language): t(label_key, language),
                t("scenario.column.eps", language): outcome.estimated_eps,
                t("scenario.column.target_pe", language): outcome.target_pe,
                t("scenario.column.model_price", language): outcome.estimated_price,
                t("scenario.column.dividends", language): outcome.estimated_dividends,
                t("scenario.column.total_return", language): outcome.estimated_total_return_pct,
                "_currency": currency,
            }
        )
    return pd.DataFrame(rows)


def _render_custom_controls(language: str) -> ScenarioShock:
    st.caption(t("scenario.custom_hint", language))
    col1, col2 = st.columns(2)
    growth = col1.slider(
        t("scenario.custom_growth_delta", language),
        -30.0,
        30.0,
        0.0,
        0.5,
        key="scenario_custom_growth_delta",
    )
    margin = col2.slider(
        t("scenario.custom_margin", language),
        -40.0,
        40.0,
        0.0,
        1.0,
        key="scenario_custom_margin_delta",
    )
    col3, col4 = st.columns(2)
    valuation = col3.slider(
        t("scenario.custom_valuation", language),
        -60.0,
        60.0,
        0.0,
        1.0,
        key="scenario_custom_valuation_delta",
    )
    dividend = col4.slider(
        t("scenario.custom_dividend", language),
        -100.0,
        50.0,
        0.0,
        5.0,
        key="scenario_custom_dividend_delta",
    )
    col5, col6, col7 = st.columns(3)
    financing = col5.slider(
        t("scenario.custom_financing", language),
        -30.0,
        30.0,
        0.0,
        1.0,
        key="scenario_custom_financing_delta",
    )
    sector = col6.slider(
        t("scenario.custom_sector", language),
        -40.0,
        40.0,
        0.0,
        1.0,
        key="scenario_custom_sector_delta",
    )
    fx = col7.slider(
        t("scenario.custom_fx", language),
        -30.0,
        30.0,
        0.0,
        1.0,
        key="scenario_custom_fx_delta",
    )
    return ScenarioShock(
        annual_growth_delta_pct=growth,
        margin_change_pct=margin,
        valuation_change_pct=valuation,
        dividend_change_pct=dividend,
        financing_earnings_impact_pct=financing,
        sector_earnings_impact_pct=sector,
        fx_earnings_impact_pct=fx,
    )


def render_scenario_engine(data: pd.DataFrame) -> None:
    language = current_language()
    st.subheader(t("scenario.title", language))
    st.caption(t("scenario.caption_v2", language))
    if data is None or data.empty:
        st.info(t("scenario.load_data", language))
        return

    options, names = _company_options(data)
    ticker = st.selectbox(
        t("common.select_company", language),
        options,
        format_func=lambda value: f"{names.get(value, value)} ({value})",
        key="scenario_ticker",
    )
    row = data.loc[data["ticker_yahoo"].astype(str) == ticker].iloc[0]
    snapshot = snapshot_from_row(row)
    currency = snapshot.currency or str(row.get("currency") or "") or "EUR"

    st.caption(
        f"{names.get(ticker, ticker)} · {ticker} · "
        f"{t('scenario.current_price', language, price=format_currency(snapshot.current_price, currency, 2, language))}"
    )
    metric_columns = st.columns(6)
    metric_columns[0].metric(
        t("scenario.derived_eps", language),
        format_number(snapshot.current_eps, 2, language),
    )
    metric_columns[1].metric(
        t("scenario.current_pe", language), format_number(snapshot.current_pe, 1, language)
    )
    metric_columns[2].metric(
        t("scenario.revenue_growth", language),
        format_percent(snapshot.revenue_growth_pct, 1, language, signed=True),
    )
    metric_columns[3].metric(
        t("scenario.operating_margin", language),
        format_percent(snapshot.operating_margin_pct, 1, language),
    )
    metric_columns[4].metric(
        t("scenario.dividend_yield", language),
        format_percent(snapshot.dividend_yield_pct, 1, language),
    )
    metric_columns[5].metric(
        t("scenario.net_debt", language),
        f"{format_number(snapshot.net_debt_ebitda, 2, language)}x"
        if snapshot.net_debt_ebitda is not None
        else "–",
    )

    control_left, control_right = st.columns([2, 1])
    preset_id = control_left.selectbox(
        t("scenario.preset", language),
        PRESET_IDS,
        format_func=lambda value: t(f"scenario.preset.{value}", language),
        key="scenario_preset_id",
    )
    years = control_right.slider(t("scenario.horizon", language), 1, 5, 3, key="scenario_years")

    custom_shock = None
    if preset_id == "custom":
        with st.expander(t("scenario.custom", language), expanded=True):
            custom_shock = _render_custom_controls(language)

    analysis = analyze_scenario(
        snapshot=snapshot,
        preset_id=preset_id,
        years=years,
        history=_history_for_ticker(ticker),
        custom_shock=custom_shock,
    )

    st.info(
        t(
            "scenario.sector_model",
            language,
            model=t(f"scenario.sector.{analysis.sector_category}", language),
        )
    )

    band_columns = st.columns(3)
    for column, label_key, outcome in zip(
        band_columns,
        ("scenario.weak", "scenario.base", "scenario.strong"),
        (analysis.weak, analysis.base, analysis.strong),
        strict=True,
    ):
        column.metric(
            t(label_key, language),
            format_percent(outcome.estimated_total_return_pct, 1, language, signed=True),
            help=t("scenario.band_help", language),
        )
        column.caption(
            t(
                "scenario.price_and_dividends",
                language,
                price=format_currency(outcome.estimated_price, currency, 2, language),
                dividends=format_currency(outcome.estimated_dividends, currency, 2, language),
            )
        )

    frame = _outcome_frame(analysis, language, currency)
    scenario_col = t("scenario.column.scenario", language)
    return_col = t("scenario.column.total_return", language)
    chart = (
        alt.Chart(frame)
        .mark_bar()
        .encode(
            x=alt.X(f"{scenario_col}:N", sort=frame[scenario_col].tolist(), title=None),
            y=alt.Y(f"{return_col}:Q", title=t("scenario.chart_return", language)),
            tooltip=[scenario_col, alt.Tooltip(f"{return_col}:Q", format="+.1f")],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, width="stretch")

    with st.expander(t("scenario.details", language), expanded=True):
        shock = analysis.preset.shock
        detail_frame = pd.DataFrame(
            [
                (t("scenario.assumption.growth_delta", language), shock.annual_growth_delta_pct, "%p"),
                (t("scenario.assumption.margin_delta", language), shock.margin_change_pct, "%"),
                (t("scenario.assumption.valuation_delta", language), shock.valuation_change_pct, "%"),
                (t("scenario.assumption.dividend_delta", language), shock.dividend_change_pct, "%"),
                (
                    t("scenario.assumption.financing_delta", language),
                    shock.financing_earnings_impact_pct,
                    "%",
                ),
                (t("scenario.assumption.sector_delta", language), shock.sector_earnings_impact_pct, "%"),
                (t("scenario.assumption.fx_delta", language), shock.fx_earnings_impact_pct, "%"),
            ],
            columns=[
                t("scenario.assumption", language),
                t("scenario.value", language),
                t("scenario.unit", language),
            ],
        )
        st.dataframe(
            detail_frame.style.format(
                {t("scenario.value", language): lambda value: format_number(value, 1, language)}
            ),
            hide_index=True,
            width="stretch",
        )

        assumptions, risks = st.columns(2)
        assumptions.markdown(f"**{t('scenario.assumptions', language)}**")
        for text in _translated_codes("assumption_code", analysis.preset.assumption_codes, language):
            assumptions.markdown(f"- {text}")
        risks.markdown(f"**{t('scenario.risks', language)}**")
        for text in _translated_codes("risk_code", analysis.preset.risk_codes, language):
            risks.markdown(f"- {text}")

    st.markdown(f"### {t('scenario.calibration.title', language)}")
    st.caption(t("scenario.calibration.caption", language))
    calibration = analysis.calibration
    calibration_columns = st.columns(6)
    calibration_columns[0].metric(t("scenario.calibration.samples", language), calibration.sample_count)
    calibration_columns[1].metric(
        t("scenario.calibration.weak", language),
        format_percent(calibration.weak_return_pct, 1, language, signed=True),
    )
    calibration_columns[2].metric(
        t("scenario.calibration.median", language),
        format_percent(calibration.median_return_pct, 1, language, signed=True),
    )
    calibration_columns[3].metric(
        t("scenario.calibration.strong", language),
        format_percent(calibration.strong_return_pct, 1, language, signed=True),
    )
    calibration_columns[4].metric(
        t("scenario.calibration.volatility", language),
        format_percent(calibration.annualized_volatility_pct, 1, language),
    )
    calibration_columns[5].metric(
        t("scenario.calibration.drawdown", language),
        format_percent(calibration.max_drawdown_pct, 1, language),
    )

    if calibration.sample_count < 20:
        st.warning(t("scenario.calibration.insufficient", language, count=calibration.sample_count))
    else:
        st.info(t(f"scenario.projection.{analysis.projection_assessment}", language))
    st.info(t(f"scenario.growth_assessment.{analysis.growth_assessment}", language))
    st.caption(t("scenario.disclaimer", language))
