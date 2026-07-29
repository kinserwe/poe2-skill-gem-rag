from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Depends
from google.genai.errors import APIError
from starlette import status

from app.api.dependencies import rate_limit
from app.api.schemas import SearchResult, AskResponse, AskRequest
from app.rag.genai_client import generate_answer
from app.rag.vector_store import search

router = APIRouter()


@router.get("/search", response_model=list[SearchResult])
async def search_qdrant(q: str, limit: Annotated[int, Query(ge=1, le=20)] = 3):
    return await search(q, limit)


@router.post("/ask", response_model=AskResponse, dependencies=[Depends(rate_limit)])
async def ask(request: AskRequest):
    results = await search(request.q, request.limit)
    try:
        return await generate_answer(request.q, results)
    except APIError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Answer generation is temporarily unavailable.",
        )
