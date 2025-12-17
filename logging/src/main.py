import logging
import os

from fastapi import FastAPI
from fluent.handler import FluentHandler
from fluent.handler import FluentRecordFormatter


logger = logging.getLogger("app")
logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

fluent_host = os.getenv("FLUENTD_HOST", "fluentd")
fluent_port = int(os.getenv("FLUENTD_PORT", "24224"))

if not any(isinstance(h, FluentHandler) for h in logger.handlers):
    fluent_handler = FluentHandler(
        "app.logs",
        host=fluent_host,
        port=fluent_port,
    )
    fluent_handler.setFormatter(
        FluentRecordFormatter(
            {
                "level": "%(levelname)s",
                "message": "%(message)s",
                "logger": "%(name)s",
                "pathname": "%(pathname)s",
                "lineno": "%(lineno)d",
                "function": "%(funcName)s",
            }
        )
    )
    logger.addHandler(fluent_handler)


app = FastAPI()


@app.get("/")
async def healthcheck():
    logger.info("healthcheck called", extra={"endpoint": "/", "status": "ok"})
    return {"status": "ok"}


@app.get("/ping")
async def ping():
    logger.info("ping called", extra={"endpoint": "/ping", "message": "pong"})
    return {"message": "pong"}
