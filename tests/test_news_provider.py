from __future__ import annotations

from stock_explorer.providers.http import HttpClient, HttpResponse
from stock_explorer.providers.news import RssNewsProvider


class FakeHttpClient(HttpClient):
    def get(self, url, *, headers=None, params=None, timeout=25):
        payload = b"""<?xml version='1.0' encoding='UTF-8'?>
        <rss version='2.0'><channel><title>Test Feed</title><item>
        <title>Example AG raises guidance</title>
        <description>Quarterly update</description>
        <link>https://example.test/article</link>
        <pubDate>Mon, 20 Jul 2026 10:00:00 GMT</pubDate>
        </item></channel></rss>"""
        return HttpResponse(200, payload, {"Content-Type": "application/rss+xml"}, url)


def test_rss_provider_returns_normalized_entry():
    provider = RssNewsProvider(
        name="Test",
        url="https://example.test/rss",
        http_client=FakeHttpClient(),
    )

    result = provider.fetch()

    assert result.diagnostic is not None
    assert result.diagnostic.status == "OK"
    assert result.diagnostic.entries == 1
    assert result.entries[0].title == "Example AG raises guidance"
    assert result.entries[0].source == "Test"
