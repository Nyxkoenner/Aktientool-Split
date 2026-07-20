from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .http import HttpClient, RequestsHttpClient


@dataclass(frozen=True, slots=True)
class ArticleTextResult:
    url: str
    status: str
    title: str = ""
    text: str = ""
    content_type: str = ""
    message: str = ""

    @property
    def chars(self) -> int:
        return len(self.text)


class ArticleTextProvider:
    """On-demand text extraction for a single article or official release.

    The provider deliberately does not crawl pages in bulk. It extracts a limited
    text excerpt only after an explicit user action and does not persist the full
    third-party article in the event database.
    """

    def __init__(
        self,
        *,
        http_client: HttpClient | None = None,
        headers: dict[str, str] | None = None,
        max_chars: int = 18_000,
    ) -> None:
        self._http = http_client or RequestsHttpClient()
        self._headers = headers or {}
        self._max_chars = max(2_000, int(max_chars))

    def fetch(self, url: str) -> ArticleTextResult:
        target = str(url or "").strip()
        if not target.startswith(("http://", "https://")):
            return ArticleTextResult(target, "Fehler", message="Ungultige HTTP-Adresse")
        try:
            response = self._http.get(target, headers=self._headers, timeout=20)
        except Exception as error:
            return ArticleTextResult(target, "Fehler", message=f"{type(error).__name__}: {error}")

        content_type = str(response.headers.get("Content-Type", "")).casefold()
        if response.status_code < 200 or response.status_code >= 300:
            return ArticleTextResult(
                target,
                "Fehler",
                content_type=content_type,
                message=f"HTTP {response.status_code}",
            )
        if "html" not in content_type and "xml" not in content_type and "text" not in content_type:
            return ArticleTextResult(
                target,
                "Nicht unterstutzt",
                content_type=content_type,
                message="Nur HTML-, XML- und Textseiten werden in diesem Modul extrahiert.",
            )

        encoding = "utf-8"
        match = re.search(r"charset=([\w-]+)", content_type)
        if match:
            encoding = match.group(1)
        text = response.content.decode(encoding, errors="replace")
        soup = BeautifulSoup(text, "lxml")
        for element in soup(["script", "style", "nav", "footer", "noscript", "svg", "form"]):
            element.decompose()
        title = soup.title.get_text(" ", strip=True) if soup.title else urlparse(target).netloc

        preferred = soup.find("article") or soup.find("main") or soup.body or soup
        paragraphs = [node.get_text(" ", strip=True) for node in preferred.find_all(["p", "h1", "h2", "li"])]
        normalized = "\n".join(line for line in paragraphs if len(line) >= 30)
        normalized = re.sub(r"[ \t]+", " ", normalized)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
        if not normalized:
            return ArticleTextResult(
                target,
                "Leer",
                title=title,
                content_type=content_type,
                message="Kein brauchbarer Fliesstext erkannt.",
            )
        return ArticleTextResult(
            target,
            "OK",
            title=title,
            text=normalized[: self._max_chars],
            content_type=content_type,
        )
