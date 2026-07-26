import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.config import settings
from app.logging_config import configure_logging
from app.rag.vector_store import ensure_collection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting up with embedding model %s", settings.EMBEDDING_MODEL)
    await ensure_collection()
    yield
    logger.info("Shutting down")


app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
