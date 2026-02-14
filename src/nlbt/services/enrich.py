from __future__ import annotations

import logging

from fastapi import FastAPI

from nlbt.services.observability import add_observability, configure_logging

SERVICE_NAME = "enrich"
configure_logging(SERVICE_NAME)
logger = logging.getLogger("nlbt.services.enrich")

app = FastAPI(title="NLBT Enrich Service")


@app.post("/enrich")
def enrich(payload: dict) -> dict:
    logger.info("enrich_received", extra={"context": {"keys": list(payload.keys())}})
    return {"status": "ok", "enriched": payload}


add_observability(app, SERVICE_NAME)
