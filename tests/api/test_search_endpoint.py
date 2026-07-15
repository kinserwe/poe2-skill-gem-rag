from unittest.mock import patch

from starlette import status

from tests.api.conftest import TEST_QDRANT_COLLECTION


class TestSearchEndpoint:
    async def test_search_returns_relevant_gem(self, seeded_search_collection, api_client):
        with patch("app.config.settings.QDRANT_COLLECTION", TEST_QDRANT_COLLECTION):
            response = await api_client.get(
                "/search", params={"q": "stuns and explodes", "limit": 3}
            )

        assert response.status_code == status.HTTP_200_OK
        names = [gem["name"] for gem in response.json()]
        assert "Boneshatter" in names

    async def test_search_rejects_invalid_limit(self, seeded_search_collection, api_client):
        with patch("app.config.settings.QDRANT_COLLECTION", TEST_QDRANT_COLLECTION):
            response = await api_client.get("/search", params={"q": "fire", "limit": 0})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
