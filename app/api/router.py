from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Query

from app.rag.vector_store import search

router = APIRouter()


@router.get("/search")
async def search_qdrant(q: str, limit: Annotated[int, Query(ge=1, le=20)] = 3):
    return await search(q, limit)
