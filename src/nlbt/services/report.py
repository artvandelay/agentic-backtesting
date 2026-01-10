from __future__ import annotations

import logging

from fastapi import FastAPI

from nlbt.services.observability import add_observability, configure_logging

SERVICE_NAME = "report"
configure_logging(SERVICE_NAME)
logger = logging.getLogger("nlbt.services.report")

app = FastAPI(title="NLBT Report Service")


@app.post("/report")
def report(payload: dict) -> dict:
    logger.info("report_received", extra={"context": {"keys": list(payload.keys())}})
    return {"status": "ok", "report_id": "placeholder-report"}


add_observability(app, SERVICE_NAME)
