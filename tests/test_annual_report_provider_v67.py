from typing import Any

import pandas as pd

from stock_explorer.providers.annual_reports import SecAnnualReportProvider, document_from_bytes
from stock_explorer.providers.http import HttpClient, HttpResponse
from stock_explorer.providers.models import ProviderDiagnostic
from stock_explorer.providers.sec import SecProvider


class FakeSecProvider(SecProvider):
    def company_map(self) -> tuple[dict[str, dict[str, Any]], str]:
        return {}, ""

    def recent_filings(self, ticker: str, days_back: int = 730) -> tuple[pd.DataFrame, ProviderDiagnostic]:
        frame = pd.DataFrame(
            [
                {
                    "filing_date": "2025-02-20",
                    "form": "10-K",
                    "document": "example-2025.htm",
                    "link": "https://example.test/example-2025.htm",
                }
            ]
        )
        return frame, ProviderDiagnostic(source="SEC", kind="filing", status="OK")

    def company_facts(self, ticker: str) -> tuple[dict[str, Any], ProviderDiagnostic]:
        return {}, ProviderDiagnostic(source="SEC", kind="facts", status="OK")


class FakeHttpClient(HttpClient):
    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int = 25,
    ) -> HttpResponse:
        html = b"<html><body><h1>Form 10-K</h1><h2>Risk Factors</h2><p>Cyber risk may affect us.</p></body></html>"
        return HttpResponse(200, html, {"content-type": "text/html"}, url)


def test_document_from_html_bytes_extracts_readable_text() -> None:
    document = document_from_bytes(
        "ABC",
        "annual.html",
        b"<html><body><h1>Annual Report 2025</h1><p>Business overview.</p></body></html>",
        content_type="text/html",
    )
    assert "Annual Report 2025" in document.text
    assert document.sha256
    assert document.content_type == "text/html"


def test_sec_annual_report_provider_loads_latest_filing() -> None:
    provider = SecAnnualReportProvider(FakeSecProvider(), http_client=FakeHttpClient())
    result = provider.fetch_latest("ABC")

    assert result.document is not None
    assert result.diagnostic.status == "OK"
    assert result.document.source == "SEC 10-K"
    assert "Cyber risk" in result.document.text
