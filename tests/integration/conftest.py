import pytest
from qdrant_client import AsyncQdrantClient

from app.config import settings

from tests.conftest import TEST_QDRANT_COLLECTION


@pytest.fixture
async def qdrant_client():
    client = AsyncQdrantClient(settings.QDRANT_URL)
    yield client

    if await client.collection_exists(TEST_QDRANT_COLLECTION):
        await client.delete_collection(TEST_QDRANT_COLLECTION)
