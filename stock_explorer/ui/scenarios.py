from __future__ import annotations

from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from stock_explorer.domain.scenario_engine import ScenarioInput, run_scenario
from stock_explorer.i18n import current_language, format_number, t


def _number(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if pd.notna(result) else default
    except (TypeError, ValueError):
        return default


def _company_options(data: pd.DataFrame) -> tuple[list[str], dict[str, str]]:
    frame = data[["ticker_yahoo", "name"]].dropna(subset=["ticker_yahoo"]).drop_duplicates("ticker_yahoo")
    names = frame.set_index("ticker_yahoo")["name"].fillna("").astype(str).to_dict()
    options = sorted(
        frame["ticker_yahoo"].astype(str).tolist(),
        key=lambda item: names.get(item, item).lower(),
    )
    return options, names


def render_scenario_engine(data: pd.DataFrame) -> None:
    language = current_language()
    st.subheader(t("scenario.title", language))
    st.caption(t("scenario.caption", language))
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
    current_price = _number(row.get("last_price"))
    pe = _number(row.get("pe_ratio"))
    current_eps = current_price / pe if current_price > 0 and pe > 0 else None
    revenue_growth = _number(row.get("revenue_growth"))
    dividend_yield = _number(row.get("dividend_yield"))

    price_label = format_number(current_price, 2, language)
    st.caption(
        f"{names.get(ticker, ticker)} · {ticker} · {t('scenario.current_price', language, price=price_label)}"
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        t("scenario.derived_eps", language),
        format_number(current_eps, 2, language) if current_eps is not None else "–",
    )
    c2.metric(
        t("scenario.current_pe", language),
        format_number(pe, 1, language) if pe > 0 else "–",
    )
    c3.metric(
        t("scenario.revenue_growth", language),
        f"{format_number(revenue_growth, 1, language)} %",
    )
    c4.metric(
        t("scenario.dividend_yield", language),
        f"{format_number(dividend_yield, 1, language)} %",
    )

    years = st.slider(t("scenario.horizon", language), 1, 5, 3, key="scenario_years")
    preset_rows = [
        (t("scenario.weak", language), revenue_growth / 100 - 0.05, -10.0, max(pe * 0.75, 5.0)),
        (t("scenario.base", language), revenue_growth / 100, 0.0, max(pe, 5.0)),
        (t("scenario.strong", language), revenue_growth / 100 + 0.05, 10.0, max(pe * 1.15, 5.0)),
    ]
    results: list[dict[str, Any]] = []
    scenario_col = t("scenario.column.scenario", language)
    growth_col = t("scenario.column.growth", language)
    margin_col = t("scenario.column.margin", language)
    pe_col = t("scenario.column.target_pe", language)
    price_col = t("scenario.column.model_price", language)
    dividends_col = t("scenario.column.dividends", language)
    return_col = t("scenario.column.total_return", language)
    for label, growth, margin, target_pe in preset_rows:
        result = run_scenario(
            ScenarioInput(
                current_price=current_price,
                current_eps=current_eps,
                revenue_growth=growth,
                margin_change_pct=margin,
                target_pe=target_pe,
                dividend_yield_pct=dividend_yield,
                years=years,
            )
        )
        results.append(
            {
                scenario_col: label,
                growth_col: growth * 100,
                margin_col: margin,
                pe_col: target_pe,
                price_col: result.estimated_price,
                dividends_col: result.estimated_dividends,
                return_col: result.estimated_total_return_pct,
            }
        )
    frame = pd.DataFrame(results)
    st.dataframe(
        frame.style.format(
            {
                growth_col: lambda value: f"{format_number(value, 1, language)} %",
                margin_col: lambda value: f"{format_number(value, 1, language)} %",
                pe_col: lambda value: format_number(value, 1, language),
                price_col: lambda value: format_number(value, 2, language),
                dividends_col: lambda value: format_number(value, 2, language),
                return_col: lambda value: f"{format_number(value, 1, language)} %",
            },
            na_rep="–",
        ),
        hide_index=True,
        use_container_width=True,
    )
    chart_data = frame.dropna(subset=[return_col])
    if not chart_data.empty:
        chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                x=alt.X(f"{scenario_col}:N", sort=[row[0] for row in preset_rows]),
                y=alt.Y(f"{return_col}:Q", title=t("scenario.chart_return", language)),
                tooltip=[scenario_col, alt.Tooltip(f"{return_col}:Q", format="+.1f")],
            )
            .properties(height=320)
        )
        st.altair_chart(chart, use_container_width=True)

    with st.expander(t("scenario.custom", language)):
        growth = st.slider(
            t("scenario.custom_growth", language),
            -20.0,
            30.0,
            float(round(revenue_growth, 1)),
            0.5,
        )
        margin = st.slider(t("scenario.custom_margin", language), -30.0, 30.0, 0.0, 1.0)
        target_pe = st.slider(
            t("scenario.custom_pe", language),
            3.0,
            50.0,
            float(round(max(pe, 10.0), 1)),
            0.5,
        )
        custom = run_scenario(
            ScenarioInput(
                current_price=current_price,
                current_eps=current_eps,
                revenue_growth=growth / 100,
                margin_change_pct=margin,
                target_pe=target_pe,
                dividend_yield_pct=dividend_yield,
                years=years,
            )
        )
        m1, m2, m3 = st.columns(3)
        m1.metric(
            t("scenario.column.model_price", language),
            format_number(custom.estimated_price, 2, language) if custom.estimated_price is not None else "–",
        )
        m2.metric(
            t("scenario.accumulated_dividends", language),
            format_number(custom.estimated_dividends, 2, language),
        )
        m3.metric(
            t("scenario.model_total_return", language),
            f"{format_number(custom.estimated_total_return_pct, 1, language)} %"
            if custom.estimated_total_return_pct is not None
            else "–",
        )
