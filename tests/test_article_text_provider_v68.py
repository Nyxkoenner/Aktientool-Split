from __future__ import annotations

from typing import Any

from stock_explorer.providers.article_text import ArticleTextProvider
from stock_explorer.providers.http import HttpClient, HttpResponse


class FakeHttpClient(HttpClient):
    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int = 25,
    ) -> HttpResponse:
        del headers, params, timeout
        html = (
            b"<html><head><title>Release</title></head><body><article><p>"
            + b"A" * 80
            + b"</p></article></body></html>"
        )
        return HttpResponse(200, html, {"Content-Type": "text/html; charset=utf-8"}, url)


def test_article_text_is_extracted_on_demand() -> None:
    provider = ArticleTextProvider(http_client=FakeHttpClient())
    result = provider.fetch("https://example.com/release")
    assert result.status == "OK"
    assert result.title == "Release"
    assert result.chars >= 80
