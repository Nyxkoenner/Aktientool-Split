from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from stock_explorer.domain.portfolio_simulation import simulate_buy_and_hold
from stock_explorer.i18n import current_language, format_number, t


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


def render_portfolio_simulation(
    market_data: pd.DataFrame,
    histories: dict[str, pd.DataFrame],
    holdings: pd.DataFrame,
) -> None:
    language = current_language()
    st.subheader(t("portfolio_sim.title", language))
    st.caption(t("portfolio_sim.caption", language))
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
    )
    years = c2.slider(t("portfolio_sim.years", language), 1, 5, 3)
    fee_bps = c3.slider(t("portfolio_sim.fees", language), 0, 100, 10)
    frequency_keys = ["none", "monthly", "quarterly", "yearly"]
    frequency_key = c4.selectbox(
        t("portfolio_sim.rebalancing", language),
        frequency_keys,
        format_func=lambda value: t(f"portfolio_sim.{value}", language),
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
        f"{format_number(rebalanced.max_drawdown_pct, 1, language)} %",
    )
    metrics[3].metric(
        t("portfolio_sim.dividends", language),
        format_number(rebalanced.dividends_received, 0, language),
    )

    date_col = t("portfolio_sim.date", language)
    strategy_col = t("portfolio_sim.strategy", language)
    value_col = t("portfolio_sim.portfolio_value", language)
    hold_label = t("portfolio_sim.buy_hold", language)
    rebalance_label = t("portfolio_sim.rebalancing", language)
    chart_frame = (
        pd.concat(
            [
                hold.equity_curve.rename(hold_label),
                rebalanced.equity_curve.rename(rebalance_label),
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
    display = frame[["ticker_yahoo", "shares", "market_value", "weight"]].rename(
        columns={
            "ticker_yahoo": t("common.ticker", language),
            "shares": "Stück" if language == "de" else "Shares",
            "market_value": "Marktwert" if language == "de" else "Market value",
            "weight": "Gewicht" if language == "de" else "Weight",
        }
    )
    st.dataframe(
        display.style.format(
            {
                "Stück" if language == "de" else "Shares": lambda value: format_number(value, 4, language),
                "Marktwert" if language == "de" else "Market value": lambda value: format_number(
                    value, 2, language
                ),
                "Gewicht" if language == "de" else "Weight": lambda value: (
                    f"{format_number(float(value) * 100, 2, language)} %"
                ),
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.caption(
        t(
            "portfolio_sim.note",
            language,
            costs=format_number(rebalanced.transaction_costs, 2, language),
        )
    )
