from __future__ import annotations

import logging

from fastapi import FastAPI

from nlbt.services.observability import add_observability, configure_logging

SERVICE_NAME = "detect"
configure_logging(SERVICE_NAME)
logger = logging.getLogger("nlbt.services.detect")

app = FastAPI(title="NLBT Detect Service")


@app.post("/detect")
def detect(payload: dict) -> dict:
    logger.info("detect_received", extra={"context": {"keys": list(payload.keys())}})
    findings = [{"rule": "placeholder", "severity": "low"}]
    return {"status": "ok", "findings": findings}


add_observability(app, SERVICE_NAME)
