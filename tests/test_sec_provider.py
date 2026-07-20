from __future__ import annotations

import json

from stock_explorer.providers.http import HttpClient, HttpResponse
from stock_explorer.providers.sec import SecEdgarProvider


class FakeSecHttpClient(HttpClient):
    def get(self, url, *, headers=None, params=None, timeout=25):
        if url.endswith("company_tickers.json"):
            payload = {"0": {"ticker": "AAA", "cik_str": 1234, "title": "Alpha Inc."}}
        else:
            payload = {
                "filings": {
                    "recent": {
                        "form": ["10-K"],
                        "filingDate": ["2026-01-31"],
                        "accessionNumber": ["0000001234-26-000001"],
                        "primaryDocument": ["alpha10k.htm"],
                        "primaryDocDescription": ["Annual report"],
                    }
                }
            }
        return HttpResponse(200, json.dumps(payload).encode(), {"Content-Type": "application/json"}, url)


def test_sec_provider_maps_ticker_and_returns_filing():
    provider = SecEdgarProvider(http_client=FakeSecHttpClient(), contact_email="test@example.com")

    company_map, error = provider.company_map()
    filings, diagnostic = provider.recent_filings("AAA", days_back=1000)

    assert error == ""
    assert company_map["AAA"]["cik"] == 1234
    assert len(filings) == 1
    assert filings.iloc[0]["form"] == "10-K"
    assert diagnostic.status == "OK"
