from pathlib import Path
from unittest.mock import patch

from scripts.ingest import load_data
from tests.integration.conftest import TEST_QDRANT_COLLECTION

SAMPLE_DATA_PATH = Path(__file__).parent / "fixtures" / "sample_gems.json"


class TestLoadData:
    async def test_ingestion_is_idempotent(self, qdrant_client):
        with patch("app.config.settings.QDRANT_COLLECTION", TEST_QDRANT_COLLECTION):
            await load_data(SAMPLE_DATA_PATH)
            first_count = (await qdrant_client.count(TEST_QDRANT_COLLECTION)).count

            await load_data(SAMPLE_DATA_PATH)
            second_count = (await qdrant_client.count(TEST_QDRANT_COLLECTION)).count

        import json

        expected_count = len(json.loads(SAMPLE_DATA_PATH.read_text()))
        assert first_count == second_count == expected_count

        points = await qdrant_client.retrieve(
            TEST_QDRANT_COLLECTION, ids=[g["id"] for g in json.loads(SAMPLE_DATA_PATH.read_text())]
        )
        assert len(points) == expected_count
