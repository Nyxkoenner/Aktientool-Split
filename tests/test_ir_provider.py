from __future__ import annotations

from pathlib import Path

import pandas as pd

from stock_explorer.providers.http import HttpClient, HttpResponse
from stock_explorer.providers.ir import IrRegistryEventProvider, parse_ics_payload


class FakeHttpClient(HttpClient):
    def get(self, url, *, headers=None, params=None, timeout=25):
        payload = b"""BEGIN:VCALENDAR\nBEGIN:VEVENT\nDTSTART:20270130T090000Z\nSUMMARY:Quarterly Results\nDESCRIPTION:Official earnings date\nURL:https://example.com/results\nEND:VEVENT\nEND:VCALENDAR\n"""
        return HttpResponse(200, payload, {"Content-Type": "text/calendar"}, url)


def test_parse_ics_payload():
    events = parse_ics_payload(
        b"BEGIN:VCALENDAR\nBEGIN:VEVENT\nDTSTART:20270130\nSUMMARY:Annual Meeting\nEND:VEVENT\nEND:VCALENDAR"
    )
    assert events[0]["SUMMARY"] == "Annual Meeting"


def test_ir_registry_provider_reads_calendar(tmp_path: Path):
    path = tmp_path / "ir_sources.csv"
    pd.DataFrame(
        [
            {
                "ticker_yahoo": "AAA",
                "source_name": "Alpha IR",
                "source_type": "ics",
                "feed_url": "https://example.com/calendar.ics",
                "source_url": "https://example.com/ir",
                "verification_level": "official_ir",
                "enabled": "true",
                "notes": "",
            }
        ]
    ).to_csv(path, index=False)
    provider = IrRegistryEventProvider(path, http_client=FakeHttpClient())
    result = provider.fetch("AAA", "Alpha Inc.", days_back=30, days_forward=1000)
    assert len(result.events) == 1
    assert result.events.iloc[0]["verification_score"] == 95
    assert result.diagnostics.iloc[0]["status"] == "OK"
