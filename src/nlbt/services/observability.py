from __future__ import annotations

import json
import logging
import os
import time
from contextlib import contextmanager
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

_REQUEST_COUNT = Counter(
    "nlbt_requests_total",
    "Total HTTP requests",
    ["service", "method", "path", "status"],
)
_REQUEST_LATENCY = Histogram(
    "nlbt_request_latency_seconds",
    "Request latency in seconds",
    ["service", "method", "path"],
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": int(record.created),
        }
        if hasattr(record, "context"):
            payload["context"] = record.context
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(service_name: str, level: int = logging.INFO) -> None:
    env_level = os.getenv("LOG_LEVEL")
    if env_level:
        level = logging.getLevelName(env_level.upper())
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]
    logging.getLogger("uvicorn.access").handlers = [handler]
    logging.getLogger("uvicorn.error").handlers = [handler]
    logging.getLogger(service_name).setLevel(level)


def add_observability(
    app: FastAPI,
    service_name: str,
    readiness_check: Optional[Callable[[], bool]] = None,
) -> None:
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next: Callable[[Request], Response]):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        path = request.url.path
        _REQUEST_COUNT.labels(
            service=service_name,
            method=request.method,
            path=path,
            status=response.status_code,
        ).inc()
        _REQUEST_LATENCY.labels(
            service=service_name,
            method=request.method,
            path=path,
        ).observe(duration)
        return response

    @app.get("/metrics")
    def metrics() -> Response:
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz() -> dict[str, str]:
        ready = True if readiness_check is None else readiness_check()
        return {"status": "ready" if ready else "not_ready"}


@contextmanager
def log_context(logger: logging.Logger, **fields: str):
    extra = {"context": fields}
    try:
        logger.info("context_start", extra=extra)
        yield
    finally:
        logger.info("context_end", extra=extra)
