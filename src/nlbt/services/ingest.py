from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException

from nlbt.services.observability import add_observability, configure_logging
from nlbt.services.wikimedia import CircuitBreaker, RateLimiter, WikimediaClient

SERVICE_NAME = "ingest"
configure_logging(SERVICE_NAME)
logger = logging.getLogger("nlbt.services.ingest")

app = FastAPI(title="NLBT Ingest Service")

_rate_limiter = RateLimiter(
    max_requests=int(os.getenv("WIKIMEDIA_RATE_LIMIT", "60")),
    per_seconds=float(os.getenv("WIKIMEDIA_RATE_WINDOW", "60")),
)
_circuit_breaker = CircuitBreaker(
    failure_threshold=int(os.getenv("WIKIMEDIA_FAILURE_THRESHOLD", "5")),
    recovery_seconds=float(os.getenv("WIKIMEDIA_RECOVERY_SECONDS", "30")),
)
_wikimedia_client = WikimediaClient(
    base_url=os.getenv("WIKIMEDIA_BASE_URL", "https://en.wikipedia.org"),
    rate_limiter=_rate_limiter,
    circuit_breaker=_circuit_breaker,
)


@app.post("/ingest")
def ingest() -> dict:
    try:
        data = _wikimedia_client.fetch_recent_changes()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("ingest_failed")
        raise HTTPException(status_code=502, detail="Failed to fetch Wikimedia data") from exc
    return {"status": "ok", "items": data.get("query", {}).get("recentchanges", [])}


add_observability(app, SERVICE_NAME)
