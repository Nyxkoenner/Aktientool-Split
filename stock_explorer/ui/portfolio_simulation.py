from __future__ import annotations

from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from stock_explorer.domain.portfolio_simulation import simulate_buy_and_hold
from stock_explorer.i18n import current_language, format_currency, format_number, format_percent, t
from stock_explorer.providers.base import MarketDataProvider
from stock_explorer.providers.fx import FxProvider
from stock_explorer.services.portfolio_simulation_service import (
    PortfolioSimulationBundle,
    PortfolioSimulationService,
)


def _close_series(history: pd.DataFrame) -> pd.Series | None:
    if history is None or history.empty:
        return None
    for column in ("Adj Close", "Close", "Kurs"):
        if column in history.columns:
            series = pd.to_numeric(history[column], errors="coerce").dropna()
            if not series.empty:
                series.index = pd.to_datetime(series.index).tz_localize(None)
                return series
    return None


def _transaction_template() -> bytes:
    frame = pd.DataFrame(
        [
            {
                "date": "2026-01-15",
                "ticker_yahoo": "ALV.DE",
                "type": "BUY",
                "shares": 10,
                "price": 245.50,
                "currency": "EUR",
                "fees": 4.90,
                "cash_amount": "",
                "comment": "Example purchase",
            },
            {
                "date": "2026-02-01",
                "ticker_yahoo": "",
                "type": "DEPOSIT",
                "shares": "",
                "price": "",
                "currency": "EUR",
                "fees": "",
                "cash_amount": 1000,
                "comment": "Optional cash deposit",
            },
        ]
    )
    return frame.to_csv(index=False).encode("utf-8-sig")


def _render_weight_model(
    market_data: pd.DataFrame,
    histories: dict[str, pd.DataFrame],
    holdings: pd.DataFrame,
    language: str,
) -> None:
    st.markdown(f"### {t('portfolio_sim.weight_model', language)}")
    st.caption(t("portfolio_sim.weight_model_caption", language))
    if holdings is None or holdings.empty:
        st.info(t("portfolio_sim.no_holdings", language))
        return
    frame = holdings.copy()
    frame["ticker_yahoo"] = frame["ticker_yahoo"].astype(str)
    frame["shares"] = pd.to_numeric(frame.get("shares"), errors="coerce").fillna(0.0)
    price_map = (
        market_data.drop_duplicates("ticker_yahoo")
        .set_index("ticker_yahoo")
        .get("last_price", pd.Series(dtype=float))
    )
    frame["market_value"] = frame.apply(
        lambda row: row["shares"] * float(price_map.get(row["ticker_yahoo"], 0.0) or 0.0),
        axis=1,
    )
    frame = frame[frame["market_value"] > 0].copy()
    if frame.empty:
        st.warning(t("portfolio_sim.no_values", language))
        return
    frame["weight"] = frame["market_value"] / frame["market_value"].sum()
    series_map: dict[str, pd.Series] = {}
    for ticker in frame["ticker_yahoo"]:
        series = _close_series(histories.get(ticker, pd.DataFrame()))
        if series is not None:
            series_map[ticker] = series
    if not series_map:
        st.warning(t("portfolio_sim.no_history", language))
        return
    prices = pd.concat(series_map, axis=1).dropna()
    weights = frame.set_index("ticker_yahoo")["weight"].to_dict()
    weights = {ticker: weight for ticker, weight in weights.items() if ticker in prices.columns}
    if not weights:
        st.warning(t("portfolio_sim.no_match", language))
        return

    c1, c2, c3, c4 = st.columns(4)
    initial_capital = c1.number_input(
        t("portfolio_sim.initial_capital", language),
        1_000.0,
        10_000_000.0,
        10_000.0,
        1_000.0,
        key="weight_model_initial_capital",
    )
    years = c2.slider(t("portfolio_sim.years", language), 1, 10, 3, key="weight_model_years")
    fee_bps = c3.slider(t("portfolio_sim.fees", language), 0, 100, 10, key="weight_model_fees")
    frequency_keys = ["none", "monthly", "quarterly", "yearly"]
    frequency_key = c4.selectbox(
        t("portfolio_sim.rebalancing", language),
        frequency_keys,
        format_func=lambda value: t(f"portfolio_sim.{value}", language),
        key="weight_model_frequency",
    )
    frequency_map = {"none": None, "monthly": "M", "quarterly": "Q", "yearly": "Y"}
    cutoff = prices.index.max() - pd.DateOffset(years=years)
    prices = prices.loc[prices.index >= cutoff]
    yield_map: dict[str, float] = {}
    if "dividend_yield" in market_data.columns:
        yield_map = (
            market_data.drop_duplicates("ticker_yahoo")
            .set_index("ticker_yahoo")["dividend_yield"]
            .fillna(0.0)
            .to_dict()
        )
    hold = simulate_buy_and_hold(prices, weights, initial_capital, None, fee_bps, yield_map)
    rebalanced = simulate_buy_and_hold(
        prices,
        weights,
        initial_capital,
        frequency_map[frequency_key],
        fee_bps,
        yield_map,
    )
    metrics = st.columns(4)
    metrics[0].metric(
        t("portfolio_sim.buy_hold_value", language),
        format_number(hold.final_value, 0, language),
    )
    metrics[1].metric(
        t("portfolio_sim.rebalanced_value", language),
        format_number(rebalanced.final_value, 0, language),
        format_number(rebalanced.final_value - hold.final_value, 0, language),
    )
    metrics[2].metric(
        t("portfolio_sim.max_drawdown", language),
        format_percent(rebalanced.max_drawdown_pct, 1, language),
    )
    metrics[3].metric(
        t("portfolio_sim.dividends", language),
        format_number(rebalanced.dividends_received, 0, language),
    )
    date_col = t("portfolio_sim.date", language)
    strategy_col = t("portfolio_sim.strategy", language)
    value_col = t("portfolio_sim.portfolio_value", language)
    chart_frame = (
        pd.concat(
            [
                hold.equity_curve.rename(t("portfolio_sim.buy_hold", language)),
                rebalanced.equity_curve.rename(t("portfolio_sim.rebalancing", language)),
            ],
            axis=1,
        )
        .reset_index(names=date_col)
        .melt(date_col, var_name=strategy_col, value_name=value_col)
    )
    chart = (
        alt.Chart(chart_frame)
        .mark_line()
        .encode(
            x=alt.X(f"{date_col}:T"),
            y=alt.Y(f"{value_col}:Q"),
            color=f"{strategy_col}:N",
            tooltip=[
                f"{date_col}:T",
                f"{strategy_col}:N",
                alt.Tooltip(f"{value_col}:Q", format=",.0f"),
            ],
        )
        .properties(height=380)
    )
    st.altair_chart(chart, use_container_width=True)


def _benchmark_options(language: str) -> dict[str, str]:
    return {
        t("portfolio_sim.benchmark_none", language): "",
        "DAX": "^GDAXI",
        "S&P 500": "^GSPC",
        "MSCI World ETF (URTH)": "URTH",
    }


def _result_chart(bundle: PortfolioSimulationBundle, language: str) -> None:
    result = bundle.result
    date_col = t("portfolio_sim.date", language)
    strategy_col = t("portfolio_sim.strategy", language)
    value_col = t("portfolio_sim.portfolio_value", language)
    curves: list[pd.Series] = [
        result.equity_curve.rename(t("portfolio_sim.actual_portfolio", language)),
        result.cash_curve.rename(t("portfolio_sim.cash", language)),
    ]
    if bundle.benchmark is not None:
        curves.append(
            bundle.benchmark.equity_curve.rename(
                f"{t('portfolio_sim.benchmark', language)} {bundle.benchmark_ticker or ''}".strip()
            )
        )
    chart_frame = (
        pd.concat(curves, axis=1)
        .reset_index(names=date_col)
        .melt(date_col, var_name=strategy_col, value_name=value_col)
        .dropna(subset=[value_col])
    )
    chart = (
        alt.Chart(chart_frame)
        .mark_line()
        .encode(
            x=alt.X(f"{date_col}:T", title=date_col),
            y=alt.Y(f"{value_col}:Q", title=value_col),
            color=alt.Color(f"{strategy_col}:N", title=strategy_col),
            tooltip=[
                alt.Tooltip(f"{date_col}:T", title=date_col),
                alt.Tooltip(f"{strategy_col}:N", title=strategy_col),
                alt.Tooltip(f"{value_col}:Q", title=value_col, format=",.2f"),
            ],
        )
        .properties(height=420)
    )
    st.altair_chart(chart, use_container_width=True)


def _render_ledger_model(
    market_data: pd.DataFrame,
    histories: dict[str, pd.DataFrame],
    transactions_path: Path | None,
    market_provider: MarketDataProvider | None,
    fx_provider: FxProvider | None,
    base_currency: str,
    language: str,
) -> None:
    st.markdown(f"### {t('portfolio_sim.ledger_model', language)}")
    st.caption(t("portfolio_sim.ledger_caption", language))
    st.download_button(
        t("portfolio_sim.download_template", language),
        _transaction_template(),
        file_name="transactions_v2_template.csv",
        mime="text/csv",
        key="portfolio_sim_download_template",
    )
    if transactions_path is None or market_provider is None or fx_provider is None:
        st.warning(t("portfolio_sim.ledger_not_configured", language))
        return
    service = PortfolioSimulationService(market_provider, fx_provider)
    try:
        transactions = service.read_transactions(transactions_path)
    except Exception as error:
        st.error(str(error))
        return
    if transactions.empty:
        st.info(t("portfolio_sim.empty_ledger", language, path=str(transactions_path)))
        return
    with st.expander(t("portfolio_sim.transaction_preview", language), expanded=False):
        st.dataframe(transactions, hide_index=True, use_container_width=True)
        st.caption(t("portfolio_sim.transaction_types", language))

    c1, c2, c3, c4 = st.columns(4)
    initial_cash = c1.number_input(
        t("portfolio_sim.initial_cash", language),
        min_value=0.0,
        max_value=100_000_000.0,
        value=0.0,
        step=1000.0,
        key="ledger_initial_cash",
    )
    auto_fund = c2.checkbox(
        t("portfolio_sim.auto_fund", language),
        value=True,
        help=t("portfolio_sim.auto_fund_help", language),
        key="ledger_auto_fund",
    )
    use_dividends = c3.checkbox(
        t("portfolio_sim.actual_dividends", language),
        value=True,
        key="ledger_use_dividends",
    )
    reinvest = c4.checkbox(
        t("portfolio_sim.reinvest_dividends", language),
        value=False,
        key="ledger_reinvest_dividends",
    )
    d1, d2, d3 = st.columns(3)
    tax_pct = d1.slider(
        t("portfolio_sim.dividend_tax", language),
        0.0,
        50.0,
        0.0,
        0.5,
        key="ledger_dividend_tax",
    )
    extra_cost_bps = d2.slider(
        t("portfolio_sim.extra_costs", language),
        0.0,
        100.0,
        0.0,
        1.0,
        key="ledger_extra_costs",
    )
    benchmarks = _benchmark_options(language)
    benchmark_label = d3.selectbox(
        t("portfolio_sim.benchmark", language),
        list(benchmarks),
        key="ledger_benchmark",
    )
    custom_benchmark = st.text_input(
        t("portfolio_sim.custom_benchmark", language),
        value="",
        placeholder="^GDAXI, ^GSPC, URTH …",
        key="ledger_custom_benchmark",
    )
    benchmark_ticker = custom_benchmark.strip().upper() or benchmarks[benchmark_label]

    if st.button(
        t("portfolio_sim.run_ledger", language),
        type="primary",
        key="run_transaction_ledger",
    ):
        with st.spinner(t("portfolio_sim.loading_ledger", language)):
            try:
                bundle = service.run(
                    transactions_path=transactions_path,
                    market_data=market_data,
                    existing_histories=histories,
                    base_currency=base_currency,
                    initial_cash=float(initial_cash),
                    auto_fund=auto_fund,
                    use_provider_dividends=use_dividends,
                    reinvest_dividends=reinvest,
                    dividend_tax_pct=float(tax_pct),
                    extra_transaction_cost_bps=float(extra_cost_bps),
                    benchmark_ticker=benchmark_ticker,
                )
                st.session_state["portfolio_ledger_bundle"] = bundle
            except Exception as error:
                st.error(t("portfolio_sim.simulation_error", language, error=str(error)))

    bundle_value: Any = st.session_state.get("portfolio_ledger_bundle")
    if not isinstance(bundle_value, PortfolioSimulationBundle):
        st.info(t("portfolio_sim.run_prompt", language))
        return
    bundle = bundle_value
    result = bundle.result
    metrics1 = st.columns(5)
    metrics1[0].metric(
        t("portfolio_sim.final_value", language),
        format_currency(result.final_value, base_currency, language=language),
    )
    metrics1[1].metric(
        t("portfolio_sim.net_contributions", language),
        format_currency(result.net_contributions, base_currency, language=language),
    )
    metrics1[2].metric(
        t("portfolio_sim.twr", language),
        format_percent(result.time_weighted_return_pct, 2, language),
    )
    metrics1[3].metric(
        t("portfolio_sim.mwr", language),
        format_percent(result.money_weighted_return_pct, 2, language),
    )
    metrics1[4].metric(
        t("portfolio_sim.max_drawdown", language),
        format_percent(result.max_drawdown_pct, 2, language),
    )
    metrics2 = st.columns(4)
    metrics2[0].metric(
        t("portfolio_sim.final_cash", language),
        format_currency(result.final_cash, base_currency, language=language),
    )
    metrics2[1].metric(
        t("portfolio_sim.dividends", language),
        format_currency(result.dividends_received, base_currency, language=language),
    )
    metrics2[2].metric(
        t("portfolio_sim.total_fees", language),
        format_currency(result.fees_paid, base_currency, language=language),
    )
    metrics2[3].metric(
        t("portfolio_sim.taxes", language),
        format_currency(result.taxes_paid, base_currency, language=language),
    )
    if bundle.benchmark is not None:
        st.caption(
            t(
                "portfolio_sim.benchmark_summary",
                language,
                ticker=bundle.benchmark_ticker or "",
                value=format_currency(bundle.benchmark.final_value, base_currency, language=language),
                mwr=format_percent(bundle.benchmark.money_weighted_return_pct, 2, language),
            )
        )
    _result_chart(bundle, language)
    if result.warnings:
        with st.expander(t("portfolio_sim.warnings", language), expanded=True):
            for warning in result.warnings:
                st.warning(warning)
    if not result.positions.empty:
        st.markdown(f"#### {t('portfolio_sim.final_positions', language)}")
        st.dataframe(result.positions, hide_index=True, use_container_width=True)
    st.caption(t("portfolio_sim.ledger_note", language))


def render_portfolio_simulation(
    market_data: pd.DataFrame,
    histories: dict[str, pd.DataFrame],
    holdings: pd.DataFrame,
    *,
    transactions_path: Path | None = None,
    market_provider: MarketDataProvider | None = None,
    fx_provider: FxProvider | None = None,
    base_currency: str = "EUR",
) -> None:
    language = current_language()
    st.subheader(t("portfolio_sim.title", language))
    st.caption(t("portfolio_sim.caption", language))
    modes = ["ledger", "weights"]
    mode = st.radio(
        t("portfolio_sim.mode", language),
        modes,
        format_func=lambda value: t(f"portfolio_sim.mode_{value}", language),
        horizontal=True,
        key="portfolio_simulation_mode",
    )
    if mode == "ledger":
        _render_ledger_model(
            market_data,
            histories,
            transactions_path,
            market_provider,
            fx_provider,
            base_currency,
            language,
        )
    else:
        _render_weight_model(market_data, histories, holdings, language)
