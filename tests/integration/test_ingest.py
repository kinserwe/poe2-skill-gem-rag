from unittest.mock import patch

from scripts.ingest import load_data
from tests.conftest import SAMPLE_DATA_PATH, TEST_QDRANT_COLLECTION


class TestLoadData:
    async def test_ingestion_is_idempotent(self, qdrant_client, sample_gems):
        with patch("app.config.settings.QDRANT_COLLECTION", TEST_QDRANT_COLLECTION):
            await load_data(SAMPLE_DATA_PATH)
            first_count = (await qdrant_client.count(TEST_QDRANT_COLLECTION)).count

            await load_data(SAMPLE_DATA_PATH)
            second_count = (await qdrant_client.count(TEST_QDRANT_COLLECTION)).count

        expected_count = len(sample_gems)
        assert first_count == second_count == expected_count

        points = await qdrant_client.retrieve(
            TEST_QDRANT_COLLECTION, ids=[g["id"] for g in sample_gems]
        )
        assert len(points) == expected_count
