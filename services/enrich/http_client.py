"""HTTP utilities with retry and backoff for MediaWiki API calls."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass
class HttpResponse:
    status: int
    data: Dict[str, Any]
    headers: Dict[str, str]


class HttpClient:
    def __init__(self, user_agent: str, max_retries: int = 5, base_backoff: float = 1.0) -> None:
        self.user_agent = user_agent
        self.max_retries = max_retries
        self.base_backoff = base_backoff

    def get_json(self, base_url: str, params: Dict[str, Any]) -> HttpResponse:
        attempt = 0
        while True:
            attempt += 1
            try:
                url = f"{base_url}?{urlencode(params)}"
                request = Request(url, headers={"User-Agent": self.user_agent})
                with urlopen(request, timeout=30) as response:
                    payload = response.read().decode("utf-8")
                    return HttpResponse(
                        status=response.status,
                        data=json.loads(payload),
                        headers=dict(response.headers),
                    )
            except HTTPError as exc:
                if not self._should_retry(exc.code, exc.headers, attempt):
                    raise
            except URLError:
                if attempt >= self.max_retries:
                    raise
                self._sleep_with_backoff(attempt, None)

    def _should_retry(self, status: int, headers: Optional[Dict[str, str]], attempt: int) -> bool:
        if status not in {429, 500, 502, 503, 504}:
            return False
        if attempt >= self.max_retries:
            return False
        retry_after = None
        if headers is not None:
            retry_after = headers.get("Retry-After")
        self._sleep_with_backoff(attempt, retry_after)
        return True

    def _sleep_with_backoff(self, attempt: int, retry_after: Optional[str]) -> None:
        if retry_after:
            try:
                delay = float(retry_after)
            except ValueError:
                delay = self.base_backoff * (2 ** (attempt - 1))
        else:
            delay = self.base_backoff * (2 ** (attempt - 1))
        time.sleep(delay)
