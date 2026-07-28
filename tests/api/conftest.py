import pytest
from unittest.mock import patch

from httpx import AsyncClient, ASGITransport

from app.main import app
from app.rag.vector_store import ensure_collection, client
from app.rag.embeddings import get_embeddings
from app.api.schemas import GemPayload
from qdrant_client.models import PointStruct

from app.rate_limiter import get_limiter, RateLimiter
from tests.conftest import TEST_QDRANT_COLLECTION


@pytest.fixture(autouse=True)
def fresh_rate_limiter():
    app.dependency_overrides[get_limiter] = lambda: RateLimiter(capacity=1000)
    yield
    app.dependency_overrides.pop(get_limiter, None)


@pytest.fixture
def rate_limited():
    app.dependency_overrides[get_limiter] = lambda: RateLimiter(capacity=0)
    yield
    app.dependency_overrides.pop(get_limiter, None)


@pytest.fixture
async def seeded_search_collection(sample_gems):
    with patch("app.config.settings.QDRANT_COLLECTION", TEST_QDRANT_COLLECTION):
        await ensure_collection()

        descriptions = [g["description"] for g in sample_gems]
        vectors = await get_embeddings(descriptions)
        points = [
            PointStruct(id=g["id"], vector=v, payload=GemPayload(**g).model_dump())
            for g, v in zip(sample_gems, vectors)
        ]
        await client.upsert(collection_name=TEST_QDRANT_COLLECTION, wait=True, points=points)

        yield

        await client.delete_collection(TEST_QDRANT_COLLECTION)


@pytest.fixture
async def api_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
