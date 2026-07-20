from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from stock_explorer.domain.portfolio_simulation import simulate_buy_and_hold


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
    st.subheader("Portfolio-Simulation")
    st.caption(
        "Vergleicht Buy-and-Hold mit regelmäßigem Rebalancing. Gebühren und Dividenden werden als transparente "
        "Näherung berücksichtigt; Steuern und historische Wechselkurse sind nicht enthalten."
    )
    if holdings is None or holdings.empty:
        st.info("Für die Simulation werden Bestände aus data/transactions.csv oder portfolio.csv benötigt.")
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
        lambda row: row["shares"] * float(price_map.get(row["ticker_yahoo"], 0.0) or 0.0), axis=1
    )
    frame = frame[frame["market_value"] > 0].copy()
    if frame.empty:
        st.warning("Für die Bestände fehlen aktuelle Marktwerte.")
        return
    frame["weight"] = frame["market_value"] / frame["market_value"].sum()

    series_map: dict[str, pd.Series] = {}
    for ticker in frame["ticker_yahoo"]:
        series = _close_series(histories.get(ticker, pd.DataFrame()))
        if series is not None:
            series_map[ticker] = series
    if len(series_map) < 1:
        st.warning("Für die Portfolio-Titel fehlen historische Kursreihen.")
        return
    prices = pd.concat(series_map, axis=1).dropna()
    weights = frame.set_index("ticker_yahoo")["weight"].to_dict()
    weights = {ticker: weight for ticker, weight in weights.items() if ticker in prices.columns}
    if not weights:
        st.warning("Bestände und verfügbare Kursreihen konnten nicht zusammengeführt werden.")
        return

    c1, c2, c3, c4 = st.columns(4)
    initial_capital = c1.number_input("Startkapital", 1_000.0, 10_000_000.0, 10_000.0, 1_000.0)
    years = c2.slider("Historie in Jahren", 1, 5, 3)
    fee_bps = c3.slider("Handelskosten je Umschichtung (Basispunkte)", 0, 100, 10)
    frequency_label = c4.selectbox(
        "Rebalancing", ["Kein Rebalancing", "Monatlich", "Quartalsweise", "Jährlich"]
    )
    frequency_map = {"Kein Rebalancing": None, "Monatlich": "M", "Quartalsweise": "Q", "Jährlich": "Y"}
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
        prices, weights, initial_capital, frequency_map[frequency_label], fee_bps, yield_map
    )

    metrics = st.columns(4)
    metrics[0].metric("Buy & Hold Endwert", f"{hold.final_value:,.0f}")
    metrics[1].metric(
        "Rebalancing Endwert",
        f"{rebalanced.final_value:,.0f}",
        f"{rebalanced.final_value - hold.final_value:+,.0f}",
    )
    metrics[2].metric("Max. Drawdown Rebalancing", f"{rebalanced.max_drawdown_pct:.1f} %")
    metrics[3].metric("Geschätzte Dividenden", f"{rebalanced.dividends_received:,.0f}")

    chart_frame = (
        pd.concat(
            [hold.equity_curve.rename("Buy & Hold"), rebalanced.equity_curve.rename("Rebalancing")], axis=1
        )
        .reset_index(names="Datum")
        .melt("Datum", var_name="Strategie", value_name="Depotwert")
    )
    chart = (
        alt.Chart(chart_frame)
        .mark_line()
        .encode(
            x=alt.X("Datum:T"),
            y=alt.Y("Depotwert:Q"),
            color="Strategie:N",
            tooltip=["Datum:T", "Strategie:N", alt.Tooltip("Depotwert:Q", format=",.0f")],
        )
        .properties(height=380)
    )
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(
        frame[["ticker_yahoo", "shares", "market_value", "weight"]].style.format(
            {"shares": "{:,.4f}", "market_value": "{:,.2f}", "weight": "{:.2%}"}
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.caption(
        f"Modellierte Handelskosten Rebalancing: {rebalanced.transaction_costs:,.2f}. "
        "Dividenden werden gleichmäßig über Handelstage verteilt; reale Zahlungstermine weichen ab."
    )
