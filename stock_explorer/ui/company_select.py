"""Wiederverwendbare Streamlit-Auswahl für Unternehmen."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def company_selectbox(
    label: str,
    frame: pd.DataFrame,
    key: str,
    *,
    ticker_col: str = "ticker_yahoo",
    name_col: str = "name",
    sort_by_name: bool = True,
    **selectbox_kwargs: Any,
) -> str:
    """Zeigt Firmenname und Ticker, gibt intern aber nur den Ticker zurück."""
    if frame is None or frame.empty or ticker_col not in frame.columns:
        raise ValueError("Für die Aktienauswahl sind keine Ticker verfügbar.")

    columns = [ticker_col]
    if name_col in frame.columns:
        columns.append(name_col)

    choices = frame[columns].copy()
    choices[ticker_col] = choices[ticker_col].fillna("").astype(str).str.strip()
    choices = choices[choices[ticker_col].ne("")].drop_duplicates(subset=[ticker_col])
    if choices.empty:
        raise ValueError("Für die Aktienauswahl sind keine gültigen Ticker verfügbar.")

    if name_col not in choices.columns:
        choices[name_col] = choices[ticker_col]
    else:
        choices[name_col] = choices[name_col].fillna("").astype(str).str.strip()
        missing_name = choices[name_col].eq("")
        choices.loc[missing_name, name_col] = choices.loc[missing_name, ticker_col]

    if sort_by_name:
        choices = choices.assign(_sort_name=choices[name_col].str.casefold()).sort_values(
            ["_sort_name", ticker_col], kind="stable"
        )

    options = choices[ticker_col].tolist()
    labels = {
        row[ticker_col]: (
            f"{row[name_col]} ({row[ticker_col]})" if row[name_col] != row[ticker_col] else row[ticker_col]
        )
        for _, row in choices.iterrows()
    }

    if key in st.session_state and st.session_state[key] not in options:
        del st.session_state[key]

    return str(
        st.selectbox(
            label,
            options=options,
            format_func=lambda ticker: labels.get(ticker, str(ticker)),
            key=key,
            **selectbox_kwargs,
        )
    )


__all__ = ["company_selectbox"]
