from unittest.mock import patch

from app.rag import vector_store
from tests.integration.conftest import TEST_QDRANT_COLLECTION


class TestEnsureCollection:
    async def test_creates_collection_when_missing(self, qdrant_client):
        assert not await qdrant_client.collection_exists(TEST_QDRANT_COLLECTION)

        with patch("app.config.settings.QDRANT_COLLECTION", TEST_QDRANT_COLLECTION):
            await vector_store.ensure_collection()

        assert await qdrant_client.collection_exists(TEST_QDRANT_COLLECTION)

    async def test_is_idempotent_when_already_exists(self, qdrant_client):
        with patch("app.config.settings.QDRANT_COLLECTION", TEST_QDRANT_COLLECTION):
            await vector_store.ensure_collection()
            await vector_store.ensure_collection()

        assert await qdrant_client.collection_exists(TEST_QDRANT_COLLECTION)
