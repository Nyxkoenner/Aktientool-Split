from __future__ import annotations

from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from stock_explorer.domain.scenario_engine import ScenarioInput, run_scenario


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
        frame["ticker_yahoo"].astype(str).tolist(), key=lambda item: names.get(item, item).lower()
    )
    return options, names


def render_scenario_engine(data: pd.DataFrame) -> None:
    st.subheader("Szenario- & Prognose-Engine")
    st.caption(
        "Berechnet transparente Wenn-dann-Szenarien aus Gewinn, Wachstum, Marge, Bewertung und Dividende. "
        "Die Ergebnisse sind Modellrechnungen und keine Kursziele."
    )
    if data is None or data.empty:
        st.info("Für die Szenarioanalyse müssen zunächst Marktdaten geladen werden.")
        return

    options, names = _company_options(data)
    ticker = st.selectbox(
        "Aktie auswählen",
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

    st.caption(f"{names.get(ticker, ticker)} · {ticker} · aktueller Kurs {current_price:,.2f}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Abgeleitetes EPS", f"{current_eps:.2f}" if current_eps is not None else "–")
    c2.metric("Aktuelles KGV", f"{pe:.1f}" if pe > 0 else "–")
    c3.metric("Umsatzwachstum", f"{revenue_growth:.1f} %")
    c4.metric("Dividendenrendite", f"{dividend_yield:.1f} %")

    years = st.slider("Szenariohorizont in Jahren", 1, 5, 3, key="scenario_years")
    preset_rows = [
        ("Schwach", revenue_growth / 100 - 0.05, -10.0, max(pe * 0.75, 5.0)),
        ("Basis", revenue_growth / 100, 0.0, max(pe, 5.0)),
        ("Stark", revenue_growth / 100 + 0.05, 10.0, max(pe * 1.15, 5.0)),
    ]
    results: list[dict[str, Any]] = []
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
                "Szenario": label,
                "Wachstum p.a.": growth * 100,
                "Margeneffekt": margin,
                "Ziel-KGV": target_pe,
                "Modellpreis": result.estimated_price,
                "Dividenden": result.estimated_dividends,
                "Gesamtrendite": result.estimated_total_return_pct,
            }
        )
    frame = pd.DataFrame(results)
    st.dataframe(
        frame.style.format(
            {
                "Wachstum p.a.": "{:+.1f} %",
                "Margeneffekt": "{:+.1f} %",
                "Ziel-KGV": "{:.1f}",
                "Modellpreis": "{:,.2f}",
                "Dividenden": "{:,.2f}",
                "Gesamtrendite": "{:+.1f} %",
            },
            na_rep="–",
        ),
        hide_index=True,
        use_container_width=True,
    )
    chart_data = frame.dropna(subset=["Gesamtrendite"])
    if not chart_data.empty:
        chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                x=alt.X("Szenario:N", sort=["Schwach", "Basis", "Stark"]),
                y=alt.Y("Gesamtrendite:Q", title="Modellhafte Gesamtrendite (%)"),
                tooltip=["Szenario", alt.Tooltip("Gesamtrendite:Q", format="+.1f")],
            )
            .properties(height=320)
        )
        st.altair_chart(chart, use_container_width=True)

    with st.expander("Eigenes Szenario"):
        growth = st.slider("Umsatz-/Gewinnwachstum p.a.", -20.0, 30.0, float(round(revenue_growth, 1)), 0.5)
        margin = st.slider("Margenänderung relativ", -30.0, 30.0, 0.0, 1.0)
        target_pe = st.slider("Ziel-KGV", 3.0, 50.0, float(round(max(pe, 10.0), 1)), 0.5)
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
            "Modellpreis", f"{custom.estimated_price:,.2f}" if custom.estimated_price is not None else "–"
        )
        m2.metric("Kumulierte Dividenden", f"{custom.estimated_dividends:,.2f}")
        m3.metric(
            "Modellhafte Gesamtrendite",
            f"{custom.estimated_total_return_pct:+.1f} %"
            if custom.estimated_total_return_pct is not None
            else "–",
        )
