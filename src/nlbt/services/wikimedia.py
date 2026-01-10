from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger("nlbt.services.wikimedia")


@dataclass
class RateLimiter:
    max_requests: int
    per_seconds: float

    def __post_init__(self) -> None:
        self._tokens = self.max_requests
        self._last_refill = time.monotonic()

    def acquire(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        refill = elapsed * (self.max_requests / self.per_seconds)
        if refill > 0:
            self._tokens = min(self.max_requests, self._tokens + refill)
            self._last_refill = now
        if self._tokens < 1:
            sleep_time = (1 - self._tokens) * (self.per_seconds / self.max_requests)
            logger.warning("rate_limit_sleep", extra={"context": {"sleep": sleep_time}})
            time.sleep(sleep_time)
            self._tokens = max(0, self._tokens - 1)
        else:
            self._tokens -= 1


@dataclass
class CircuitBreaker:
    failure_threshold: int
    recovery_seconds: float

    def __post_init__(self) -> None:
        self._failures = 0
        self._opened_at: Optional[float] = None

    def allow(self) -> bool:
        if self._opened_at is None:
            return True
        if time.monotonic() - self._opened_at >= self.recovery_seconds:
            self._opened_at = None
            self._failures = 0
            return True
        return False

    def record_success(self) -> None:
        self._failures = 0
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._opened_at = time.monotonic()
            logger.error("circuit_breaker_open", extra={"context": {"failures": self._failures}})


class WikimediaClient:
    def __init__(
        self,
        base_url: str,
        rate_limiter: RateLimiter,
        circuit_breaker: CircuitBreaker,
        timeout: float = 10.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._rate_limiter = rate_limiter
        self._circuit_breaker = circuit_breaker
        self._client = httpx.Client(timeout=timeout)

    def fetch_recent_changes(self) -> dict:
        if not self._circuit_breaker.allow():
            raise RuntimeError("Circuit breaker open; Wikimedia API temporarily unavailable")
        self._rate_limiter.acquire()
        url = f"{self._base_url}/w/api.php"
        params = {
            "action": "query",
            "list": "recentchanges",
            "rcprop": "title|timestamp|user",
            "format": "json",
        }
        try:
            response = self._client.get(url, params=params)
            response.raise_for_status()
            self._circuit_breaker.record_success()
            return response.json()
        except httpx.HTTPError as exc:
            self._circuit_breaker.record_failure()
            logger.exception("wikimedia_api_error", extra={"context": {"error": str(exc)}})
            raise

    def close(self) -> None:
        self._client.close()
