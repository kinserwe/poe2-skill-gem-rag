import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.concurrency import run_in_threadpool

from app.api.router import router
from app.logging_config import configure_logging
from app.rag.embeddings import get_embedding_model
from app.rag.vector_store import ensure_collection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await run_in_threadpool(get_embedding_model)
    await ensure_collection()
    yield
    logger.info("Shutting down")


app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
