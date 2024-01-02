"""Initialize client gateway."""

from contextlib import asynccontextmanager
import logging
from multiprocessing import Queue

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logging_loki import LokiQueueHandler
from prometheus_fastapi_instrumentator import Instrumentator

from .routes import router
from .settings import app_settings
from .database import initialize_pool
from .helpers import EndpointFilter

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database connection pool
    app.state.pool = await initialize_pool()
    yield


# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)
log.info("Initializing FastAPI app.")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
app.include_router(router)

# Add Prometheus instrumentation
Instrumentator().instrument(app).expose(app, tags=["monitoring"])
# Loki logging
loki_logs_handler = LokiQueueHandler(
    Queue(-1),
    url=app_settings.LOKI_ENDPOINT,
    tags={"application": "fastapi", "service": "bksys_transaction_ms"},
    version="1",
)

uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.addHandler(loki_logs_handler)

# Filter out health check endpoint from access logs
uvicorn_access_logger.addFilter(EndpointFilter("/service-status"))
uvicorn_access_logger.addFilter(EndpointFilter("/metrics"))


__all__ = ["app"]
