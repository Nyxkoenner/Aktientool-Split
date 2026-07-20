from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(slots=True)
class HttpResponse:
    status_code: int
    content: bytes
    headers: dict[str, str]
    url: str

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")

    def json(self) -> Any:
        return json.loads(self.text)


class HttpClient(ABC):
    @abstractmethod
    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int = 25,
    ) -> HttpResponse:
        raise NotImplementedError


class RequestsHttpClient(HttpClient):
    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int = 25,
    ) -> HttpResponse:
        response = self._session.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        return HttpResponse(
            status_code=response.status_code,
            content=response.content,
            headers={str(key): str(value) for key, value in response.headers.items()},
            url=str(response.url),
        )
