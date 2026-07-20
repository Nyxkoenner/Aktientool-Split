from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from stock_explorer.domain.report_analysis import ReportAnalysis, analyze_report_text
from stock_explorer.providers.annual_reports import (
    AnnualReportDocument,
    AnnualReportFetchResult,
    AnnualReportProvider,
    document_from_bytes,
)
from stock_explorer.providers.models import ProviderDiagnostic

SEGMENT_COLUMNS = [
    "ticker_yahoo",
    "segment",
    "revenue",
    "revenue_share_pct",
    "operating_profit",
    "currency",
    "fiscal_year",
    "source",
    "notes",
]
REGION_COLUMNS = [
    "ticker_yahoo",
    "region",
    "revenue",
    "revenue_share_pct",
    "currency",
    "fiscal_year",
    "source",
    "notes",
]
PROFILE_COLUMNS = [
    "ticker_yahoo",
    "business_model",
    "moat",
    "brands",
    "competitors",
    "key_customers",
    "suppliers",
    "opportunities",
    "risks",
    "catalysts",
    "ir_url",
    "source_note",
    "updated_at",
]


@dataclass(slots=True)
class ReportAnalysisBundle:
    document: AnnualReportDocument
    analysis: ReportAnalysis
    diagnostic: ProviderDiagnostic


class CompanyReportService:
    def __init__(
        self,
        *,
        data_dir: Path,
        annual_report_provider: AnnualReportProvider | None = None,
    ) -> None:
        self._data_dir = Path(data_dir)
        self._report_dir = self._data_dir / "company_documents"
        self._segments_path = self._data_dir / "company_segments.csv"
        self._regions_path = self._data_dir / "company_regions.csv"
        self._profiles_path = self._data_dir / "company_profiles.csv"
        self._provider = annual_report_provider
        self._report_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _symbol(ticker: str) -> str:
        return str(ticker or "").strip().upper().replace("$", "")

    @staticmethod
    def _diagnostic(source: str, status: str, message: str = "") -> ProviderDiagnostic:
        return ProviderDiagnostic(source=source, kind="annual_report", status=status, message=message)

    def analyze_upload(
        self,
        ticker: str,
        filename: str,
        payload: bytes,
        *,
        content_type: str = "",
    ) -> ReportAnalysisBundle:
        document = document_from_bytes(
            ticker,
            filename,
            payload,
            source="Local upload",
            content_type=content_type,
        )
        analysis = analyze_report_text(document.text)
        diagnostic = self._diagnostic("Local upload", "OK" if document.text.strip() else "Kein Text")
        diagnostic.entries = document.page_count or 1
        diagnostic.matches = len(document.text)
        diagnostic.content_type = document.content_type
        return ReportAnalysisBundle(document, analysis, diagnostic)

    def fetch_latest_official(self, ticker: str) -> ReportAnalysisBundle | None:
        if self._provider is None:
            return None
        result: AnnualReportFetchResult = self._provider.fetch_latest(ticker)
        if result.document is None:
            return None
        analysis = analyze_report_text(result.document.text)
        return ReportAnalysisBundle(result.document, analysis, result.diagnostic)

    def fetch_latest_official_result(
        self,
        ticker: str,
    ) -> tuple[ReportAnalysisBundle | None, ProviderDiagnostic]:
        if self._provider is None:
            diagnostic = self._diagnostic("Annual report provider", "Nicht konfiguriert")
            return None, diagnostic
        result = self._provider.fetch_latest(ticker)
        if result.document is None:
            return None, result.diagnostic
        return ReportAnalysisBundle(
            result.document, analyze_report_text(result.document.text), result.diagnostic
        ), result.diagnostic

    def _snapshot_directory(self, bundle: ReportAnalysisBundle) -> Path:
        symbol = self._symbol(bundle.document.ticker).replace(".", "_")
        year = bundle.analysis.fiscal_year or "unknown"
        return self._report_dir / symbol / f"{year}_{bundle.document.sha256[:12]}"

    @staticmethod
    def _atomic_write_text(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
        temp_path.write_text(content, encoding="utf-8")
        last_error: OSError | None = None
        for attempt in range(6):
            try:
                os.replace(temp_path, path)
                return
            except OSError as error:
                last_error = error
                time.sleep(0.08 * (attempt + 1))
        temp_path.unlink(missing_ok=True)
        if last_error is not None:
            raise last_error

    def save_snapshot(self, bundle: ReportAnalysisBundle) -> Path:
        directory = self._snapshot_directory(bundle)
        metadata = {
            "document": bundle.document.to_dict(include_text=False),
            "diagnostic": bundle.diagnostic.to_dict(),
        }
        self._atomic_write_text(directory / "document.txt", bundle.document.text)
        self._atomic_write_text(
            directory / "analysis.json",
            json.dumps(bundle.analysis.to_dict(), ensure_ascii=False, indent=2),
        )
        self._atomic_write_text(
            directory / "metadata.json",
            json.dumps(metadata, ensure_ascii=False, indent=2, default=str),
        )
        return directory

    def list_snapshots(self, ticker: str) -> pd.DataFrame:
        symbol = self._symbol(ticker).replace(".", "_")
        root = self._report_dir / symbol
        rows: list[dict[str, Any]] = []
        if not root.exists():
            return pd.DataFrame()
        for directory in sorted(root.iterdir(), reverse=True):
            metadata_path = directory / "metadata.json"
            analysis_path = directory / "analysis.json"
            if not metadata_path.exists() or not analysis_path.exists():
                continue
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            document = dict(metadata.get("document", {}))
            rows.append(
                {
                    "snapshot_id": directory.name,
                    "fiscal_year": analysis.get("fiscal_year"),
                    "report_type": analysis.get("report_type"),
                    "source": document.get("source"),
                    "filename": document.get("filename"),
                    "retrieved_at": document.get("retrieved_at"),
                    "coverage_pct": analysis.get("coverage_pct"),
                    "path": str(directory),
                }
            )
        return pd.DataFrame(rows)

    def load_snapshot(self, path: str | Path) -> ReportAnalysisBundle:
        directory = Path(path)
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        analysis_payload = json.loads((directory / "analysis.json").read_text(encoding="utf-8"))
        text = (directory / "document.txt").read_text(encoding="utf-8")
        document_payload = dict(metadata.get("document", {}))
        document = AnnualReportDocument(text=text, **document_payload)
        diagnostic_payload = dict(metadata.get("diagnostic", {}))
        allowed = ProviderDiagnostic.__dataclass_fields__.keys()
        diagnostic = ProviderDiagnostic(
            **{key: value for key, value in diagnostic_payload.items() if key in allowed}
        )
        return ReportAnalysisBundle(document, ReportAnalysis.from_dict(analysis_payload), diagnostic)

    @staticmethod
    def segment_candidates(bundle: ReportAnalysisBundle) -> pd.DataFrame:
        rows = []
        for candidate in bundle.analysis.segments:
            rows.append(
                {
                    "include": candidate.confidence >= 0.65,
                    "segment": candidate.label,
                    "revenue": candidate.amount,
                    "revenue_share_pct": candidate.share_pct,
                    "operating_profit": None,
                    "currency": candidate.currency,
                    "fiscal_year": candidate.fiscal_year,
                    "source": bundle.document.source_url or bundle.document.filename,
                    "notes": f"Konfidenz {candidate.confidence:.0%} · {candidate.evidence}",
                    "confidence": candidate.confidence,
                    "evidence": candidate.evidence,
                }
            )
        return pd.DataFrame(rows)

    @staticmethod
    def region_candidates(bundle: ReportAnalysisBundle) -> pd.DataFrame:
        rows = []
        for candidate in bundle.analysis.regions:
            rows.append(
                {
                    "include": candidate.confidence >= 0.65,
                    "region": candidate.label,
                    "revenue": candidate.amount,
                    "revenue_share_pct": candidate.share_pct,
                    "currency": candidate.currency,
                    "fiscal_year": candidate.fiscal_year,
                    "source": bundle.document.source_url or bundle.document.filename,
                    "notes": f"Konfidenz {candidate.confidence:.0%} · {candidate.evidence}",
                    "confidence": candidate.confidence,
                    "evidence": candidate.evidence,
                }
            )
        return pd.DataFrame(rows)

    @staticmethod
    def _read_csv(path: Path, columns: list[str]) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame(columns=columns)
        try:
            frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        except Exception:
            return pd.DataFrame(columns=columns)
        for column in columns:
            if column not in frame.columns:
                frame[column] = ""
        return frame[columns].copy()

    @classmethod
    def _write_csv(cls, path: Path, frame: pd.DataFrame, columns: list[str]) -> None:
        clean = frame.copy()
        for column in columns:
            if column not in clean.columns:
                clean[column] = ""
        content = clean[columns].fillna("").to_csv(index=False, lineterminator="\n")
        cls._atomic_write_text(path, content)

    def _merge_candidates(
        self,
        ticker: str,
        edited: pd.DataFrame,
        *,
        path: Path,
        columns: list[str],
        label_column: str,
    ) -> int:
        symbol = self._symbol(ticker)
        incoming = edited.copy() if isinstance(edited, pd.DataFrame) else pd.DataFrame()
        if incoming.empty:
            return 0
        if "include" in incoming.columns:
            incoming = incoming[incoming["include"].fillna(False).astype(bool)].copy()
        incoming = incoming[incoming.get(label_column, pd.Series(dtype=str)).astype(str).str.strip().ne("")]
        if incoming.empty:
            return 0
        incoming["ticker_yahoo"] = symbol
        for column in columns:
            if column not in incoming.columns:
                incoming[column] = ""
        incoming = incoming[columns].fillna("")
        current = self._read_csv(path, columns)
        if not current.empty:
            incoming_keys = {
                (
                    symbol,
                    str(row[label_column]).strip().lower(),
                    str(row.get("fiscal_year", "")).strip(),
                )
                for _, row in incoming.iterrows()
            }
            keep = []
            for _, row in current.iterrows():
                key = (
                    self._symbol(str(row.get("ticker_yahoo", ""))),
                    str(row.get(label_column, "")).strip().lower(),
                    str(row.get("fiscal_year", "")).strip(),
                )
                keep.append(key not in incoming_keys)
            current = current[pd.Series(keep, index=current.index)]
        combined = pd.concat([current, incoming], ignore_index=True)
        self._write_csv(path, combined, columns)
        return len(incoming)

    def save_segments(self, ticker: str, edited: pd.DataFrame) -> int:
        return self._merge_candidates(
            ticker,
            edited,
            path=self._segments_path,
            columns=SEGMENT_COLUMNS,
            label_column="segment",
        )

    def save_regions(self, ticker: str, edited: pd.DataFrame) -> int:
        return self._merge_candidates(
            ticker,
            edited,
            path=self._regions_path,
            columns=REGION_COLUMNS,
            label_column="region",
        )

    @staticmethod
    def _join_unique(existing: str, values: list[str]) -> str:
        items = [item.strip() for item in str(existing or "").split("|") if item.strip()]
        seen = {item.lower() for item in items}
        for value in values:
            compact = " ".join(str(value).split()).strip()
            if compact and compact.lower() not in seen:
                items.append(compact)
                seen.add(compact.lower())
        return " | ".join(items)

    def update_qualitative_profile(self, ticker: str, bundle: ReportAnalysisBundle) -> None:
        symbol = self._symbol(ticker)
        frame = self._read_csv(self._profiles_path, PROFILE_COLUMNS)
        match = (
            frame[frame["ticker_yahoo"].map(self._symbol).eq(symbol)] if not frame.empty else pd.DataFrame()
        )
        row = {column: "" for column in PROFILE_COLUMNS}
        if not match.empty:
            row.update({column: str(match.iloc[-1].get(column, "") or "") for column in PROFILE_COLUMNS})
            frame = frame[~frame["ticker_yahoo"].map(self._symbol).eq(symbol)].copy()
        row["ticker_yahoo"] = symbol
        if bundle.analysis.summary and not row["business_model"].strip():
            row["business_model"] = bundle.analysis.summary
        row["brands"] = self._join_unique(row["brands"], bundle.analysis.brands_and_subsidiaries)
        row["risks"] = self._join_unique(row["risks"], [item.evidence for item in bundle.analysis.risks[:10]])
        row["opportunities"] = self._join_unique(
            row["opportunities"],
            [item.evidence for item in bundle.analysis.opportunities[:8]],
        )
        row["suppliers"] = self._join_unique(
            row["suppliers"],
            [item.evidence for item in bundle.analysis.dependencies[:8]],
        )
        source = bundle.document.source_url or bundle.document.filename
        note = f"Automatische Berichtsanalyse {bundle.analysis.fiscal_year or ''}: {source}".strip()
        row["source_note"] = self._join_unique(row["source_note"], [note])
        row["updated_at"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
        combined = pd.concat([frame, pd.DataFrame([row])], ignore_index=True)
        self._write_csv(self._profiles_path, combined, PROFILE_COLUMNS)
