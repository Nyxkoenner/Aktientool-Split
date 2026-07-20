from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from stock_explorer.i18n import current_language, format_number, format_percent, t
from stock_explorer.services.report_service import CompanyReportService, ReportAnalysisBundle


def _state_key(ticker: str) -> str:
    return f"annual_report_bundle_{str(ticker).replace('.', '_').upper()}"


def _finding_frame(items: list[Any], language: str) -> pd.DataFrame:
    rows = []
    for item in items:
        rows.append(
            {
                t("report.column.category", language): item.category,
                t("report.column.confidence", language): item.confidence,
                t("report.column.evidence", language): item.evidence,
            }
        )
    return pd.DataFrame(rows)


def _render_diagnostic(bundle: ReportAnalysisBundle, language: str) -> None:
    diagnostic = bundle.diagnostic
    if diagnostic.status == "OK":
        st.success(t("report.loaded", language, source=bundle.document.source))
    elif diagnostic.message:
        st.warning(diagnostic.message)
    rows = pd.DataFrame(
        [
            {
                t("common.source", language): diagnostic.source,
                t("common.status", language): diagnostic.status,
                "HTTP": diagnostic.http_status,
                t("report.content_type", language): diagnostic.content_type or bundle.document.content_type,
                t("report.duration", language): diagnostic.duration_ms,
                t("common.message", language): diagnostic.message,
            }
        ]
    )
    st.dataframe(rows, hide_index=True, use_container_width=True)


def _render_summary(bundle: ReportAnalysisBundle, language: str) -> None:
    analysis = bundle.analysis
    document = bundle.document
    columns = st.columns(5)
    columns[0].metric(t("report.metric.year", language), str(analysis.fiscal_year or "–"))
    columns[1].metric(t("report.metric.type", language), analysis.report_type)
    columns[2].metric(t("report.metric.pages", language), str(document.page_count or "–"))
    columns[3].metric(t("report.metric.characters", language), format_number(len(document.text), 0, language))
    columns[4].metric(
        t("report.metric.coverage", language), format_percent(analysis.coverage_pct, 0, language)
    )
    if analysis.summary:
        st.markdown(f"#### {t('report.summary', language)}")
        st.write(analysis.summary)
    if analysis.warnings:
        for warning in analysis.warnings:
            st.warning(warning)


def _render_findings(bundle: ReportAnalysisBundle, language: str) -> None:
    tabs = st.tabs(
        [
            t("report.tab.risks", language),
            t("report.tab.opportunities", language),
            t("report.tab.dependencies", language),
            t("report.tab.sections", language),
        ]
    )
    collections = [
        bundle.analysis.risks,
        bundle.analysis.opportunities,
        bundle.analysis.dependencies,
    ]
    for tab, items in zip(tabs[:3], collections, strict=False):
        with tab:
            frame = _finding_frame(items, language)
            if frame.empty:
                st.info(t("common.no_data", language))
            else:
                confidence_column = t("report.column.confidence", language)
                st.dataframe(
                    frame.style.format({confidence_column: "{:.0%}"}),
                    hide_index=True,
                    use_container_width=True,
                )
    with tabs[3]:
        if not bundle.analysis.sections:
            st.info(t("common.no_data", language))
        else:
            for section, text in bundle.analysis.sections.items():
                with st.expander(section.title()):
                    st.text(text[:12000])


def _candidate_editor(
    frame: pd.DataFrame,
    *,
    key: str,
    label_column: str,
    language: str,
) -> pd.DataFrame:
    if frame.empty:
        st.info(t("report.no_candidates", language))
        return frame
    return st.data_editor(
        frame,
        key=key,
        hide_index=True,
        use_container_width=True,
        disabled=["confidence", "evidence"],
        column_config={
            "include": st.column_config.CheckboxColumn(t("report.column.include", language)),
            label_column: st.column_config.TextColumn(
                t("report.column.segment", language)
                if label_column == "segment"
                else t("report.column.region", language)
            ),
            "revenue": st.column_config.NumberColumn(t("report.column.revenue", language)),
            "revenue_share_pct": st.column_config.NumberColumn(
                t("report.column.share", language), min_value=0.0, max_value=100.0, format="%.1f"
            ),
            "fiscal_year": st.column_config.NumberColumn(t("report.metric.year", language), format="%d"),
            "confidence": st.column_config.ProgressColumn(
                t("report.column.confidence", language), min_value=0.0, max_value=1.0, format="%.0f%%"
            ),
            "evidence": st.column_config.TextColumn(t("report.column.evidence", language), width="large"),
        },
    )


def _render_candidates(
    ticker: str,
    bundle: ReportAnalysisBundle,
    service: CompanyReportService,
    language: str,
) -> None:
    st.caption(t("report.review_hint", language))
    segment_frame = service.segment_candidates(bundle)
    region_frame = service.region_candidates(bundle)
    segment_tab, region_tab = st.tabs([t("report.tab.segments", language), t("report.tab.regions", language)])
    symbol_key = str(ticker).replace(".", "_").upper()
    with segment_tab:
        edited_segments = _candidate_editor(
            segment_frame,
            key=f"report_segments_{symbol_key}_{bundle.document.sha256[:8]}",
            label_column="segment",
            language=language,
        )
        if not edited_segments.empty and st.button(
            t("report.save_segments", language), key=f"report_save_segments_{symbol_key}"
        ):
            count = service.save_segments(ticker, edited_segments)
            st.success(t("report.saved_rows", language, count=count))
    with region_tab:
        edited_regions = _candidate_editor(
            region_frame,
            key=f"report_regions_{symbol_key}_{bundle.document.sha256[:8]}",
            label_column="region",
            language=language,
        )
        if not edited_regions.empty and st.button(
            t("report.save_regions", language), key=f"report_save_regions_{symbol_key}"
        ):
            count = service.save_regions(ticker, edited_regions)
            st.success(t("report.saved_rows", language, count=count))


def _render_snapshots(ticker: str, service: CompanyReportService, language: str) -> None:
    snapshots = service.list_snapshots(ticker)
    if snapshots.empty:
        st.caption(t("report.no_snapshots", language))
        return
    st.markdown(f"#### {t('report.snapshots', language)}")
    display = snapshots.drop(columns=["path"], errors="ignore")
    st.dataframe(display, hide_index=True, use_container_width=True)
    options = snapshots["path"].astype(str).tolist()
    labels = {
        str(
            row["path"]
        ): f"{row.get('fiscal_year') or '–'} · {row.get('report_type') or '–'} · {row.get('source') or '–'}"
        for _, row in snapshots.iterrows()
    }
    selected = st.selectbox(
        t("report.snapshot_select", language),
        options=options,
        format_func=lambda value: labels.get(value, value),
        key=f"report_snapshot_select_{str(ticker).replace('.', '_')}",
    )
    if st.button(t("report.snapshot_load", language), key=f"report_snapshot_load_{ticker}"):
        st.session_state[_state_key(ticker)] = service.load_snapshot(selected)
        st.rerun()


def render_annual_report_automation(
    ticker: str,
    company_name: str,
    service: CompanyReportService,
) -> None:
    language = current_language()
    st.divider()
    st.markdown(f"### {t('report.title', language)}")
    st.caption(t("report.caption", language))

    upload_tab, official_tab = st.tabs([t("report.tab.upload", language), t("report.tab.official", language)])
    with upload_tab:
        upload = st.file_uploader(
            t("report.upload", language),
            type=["pdf", "txt", "html", "htm"],
            key=f"annual_report_upload_{str(ticker).replace('.', '_')}",
            help=t("report.upload_help", language),
        )
        if upload is not None and st.button(
            t("report.analyze_upload", language),
            type="primary",
            key=f"annual_report_analyze_{str(ticker).replace('.', '_')}",
        ):
            try:
                upload_bundle = service.analyze_upload(
                    ticker,
                    upload.name,
                    upload.getvalue(),
                    content_type=upload.type or "",
                )
                st.session_state[_state_key(ticker)] = upload_bundle
            except Exception as error:
                st.error(f"{type(error).__name__}: {error}")
    with official_tab:
        st.write(t("report.official_hint", language, company=company_name, ticker=ticker))
        if st.button(
            t("report.load_official", language),
            key=f"annual_report_official_{str(ticker).replace('.', '_')}",
        ):
            with st.spinner(t("report.loading", language)):
                official_bundle, diagnostic = service.fetch_latest_official_result(ticker)
            if official_bundle is None:
                st.warning(diagnostic.message or diagnostic.status)
            else:
                st.session_state[_state_key(ticker)] = official_bundle

    bundle = st.session_state.get(_state_key(ticker))
    if not isinstance(bundle, ReportAnalysisBundle):
        _render_snapshots(ticker, service, language)
        return

    _render_diagnostic(bundle, language)
    _render_summary(bundle, language)
    overview_tab, findings_tab, candidates_tab, text_tab = st.tabs(
        [
            t("report.tab.overview", language),
            t("report.tab.findings", language),
            t("report.tab.candidates", language),
            t("report.tab.text", language),
        ]
    )
    with overview_tab:
        brands = bundle.analysis.brands_and_subsidiaries
        if brands:
            st.markdown(f"**{t('report.brands', language)}**")
            st.write(" · ".join(f"`{item}`" for item in brands[:30]))
        st.write(t("report.source_document", language, filename=bundle.document.filename))
        if bundle.document.source_url:
            st.link_button(t("report.open_source", language), bundle.document.source_url)
    with findings_tab:
        _render_findings(bundle, language)
    with candidates_tab:
        _render_candidates(ticker, bundle, service, language)
    with text_tab:
        query = st.text_input(
            t("report.search_text", language), key=f"report_text_search_{str(ticker).replace('.', '_')}"
        )
        text = bundle.document.text
        if query.strip():
            lines = [line for line in text.splitlines() if query.lower() in line.lower()]
            st.text("\n".join(lines[:250]) or t("report.search_empty", language))
        else:
            st.text_area(
                t("report.extracted_text", language),
                value=text[:150000],
                height=500,
                disabled=True,
            )
        st.download_button(
            t("report.download_text", language),
            data=text.encode("utf-8"),
            file_name=f"{str(ticker).replace('.', '_')}_{bundle.analysis.fiscal_year or 'report'}.txt",
            mime="text/plain",
        )

    action_columns = st.columns(2)
    if action_columns[0].button(
        t("report.save_snapshot", language), key=f"report_save_snapshot_{str(ticker).replace('.', '_')}"
    ):
        path = service.save_snapshot(bundle)
        st.success(t("report.snapshot_saved", language, path=str(path)))
    if action_columns[1].button(
        t("report.transfer_profile", language), key=f"report_transfer_profile_{str(ticker).replace('.', '_')}"
    ):
        service.update_qualitative_profile(ticker, bundle)
        st.success(t("report.profile_updated", language))

    _render_snapshots(ticker, service, language)
