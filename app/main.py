from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.rag.vector_store import ensure_collection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_collection()


app = FastAPI(lifespan=lifespan)

app.include_router(router)
