from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from stock_explorer.i18n import current_language, format_number, t


def _human_amount(value: Any, language: str) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "–"
    absolute = abs(float(numeric))
    if absolute >= 1e12:
        suffix = "Bio." if language == "de" else "tn"
        return f"{format_number(float(numeric) / 1e12, 2, language)} {suffix}"
    if absolute >= 1e9:
        suffix = "Mrd." if language == "de" else "bn"
        return f"{format_number(float(numeric) / 1e9, 2, language)} {suffix}"
    if absolute >= 1e6:
        suffix = "Mio." if language == "de" else "m"
        return f"{format_number(float(numeric) / 1e6, 2, language)} {suffix}"
    return format_number(numeric, 0, language)


def render_profile_automation(ticker: str, enrichment: dict[str, Any]) -> None:
    language = current_language()
    st.markdown(f"#### {t('profile_auto.title', language)}")
    st.caption(t("profile_auto.caption", language))

    provider_status = enrichment.get("provider_status", pd.DataFrame())
    if isinstance(provider_status, pd.DataFrame) and not provider_status.empty:
        st.dataframe(provider_status, hide_index=True, use_container_width=True)

    trend = enrichment.get("official_financials", pd.DataFrame())
    if not isinstance(trend, pd.DataFrame) or trend.empty:
        st.info(t("profile_auto.no_sec", language))
    else:
        entity = str(enrichment.get("sec_entity_name") or ticker)
        cik = str(enrichment.get("sec_cik") or "–")
        st.success(t("profile_auto.available", language, entity=entity, cik=cik))
        display = trend.copy()
        fiscal_year = t("profile_auto.fiscal_year", language)
        display[fiscal_year] = pd.to_datetime(display["fiscal_date"], errors="coerce").dt.year
        columns = [
            fiscal_year,
            "revenue",
            "net_income",
            "operating_cashflow",
            "capex",
            "free_cashflow",
            "assets",
            "liabilities",
            "total_debt",
            "dividends_paid",
            "source",
        ]
        labels = {
            "revenue": t("profile_auto.revenue", language),
            "net_income": t("profile_auto.net_income", language),
            "operating_cashflow": t("profile_auto.operating_cashflow", language),
            "capex": t("profile_auto.capex", language),
            "free_cashflow": t("profile_auto.free_cashflow", language),
            "assets": t("profile_auto.assets", language),
            "liabilities": t("profile_auto.liabilities", language),
            "total_debt": t("profile_auto.total_debt", language),
            "dividends_paid": t("profile_auto.dividends_paid", language),
            "source": t("common.source", language),
        }
        table = display[[column for column in columns if column in display.columns]].rename(columns=labels)
        formatters = {
            column: (lambda value, lang=language: _human_amount(value, lang))
            for column in table.columns
            if column not in {fiscal_year, t("common.source", language)}
        }
        st.dataframe(
            table.style.format(formatters, na_rep="–"),
            hide_index=True,
            use_container_width=True,
        )
        st.download_button(
            t("profile_auto.download", language),
            data=trend.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{ticker.replace('.', '_')}_sec_companyfacts.csv",
            mime="text/csv",
        )

    warnings = enrichment.get("provider_warnings", [])
    if warnings:
        with st.expander(t("profile_auto.warnings", language)):
            for warning in warnings:
                st.write(f"- {warning}")
