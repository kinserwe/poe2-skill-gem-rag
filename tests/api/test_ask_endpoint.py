from unittest.mock import patch, AsyncMock

from starlette import status

from app.api.schemas import AskResponse


class TestAskEndpoint:
    async def test_ask_returns_relevant_answer(self, seeded_search_collection, api_client):
        mock_response = AskResponse(
            answer="Boneshatter stuns nearby enemies and explodes.", sources=[]
        )

        with patch(
            "app.api.router.generate_answer",
            new=AsyncMock(return_value=mock_response),
        ) as mock_generate:
            response = await api_client.post(
                "/ask",
                json={"q": "stuns and explodes"},
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["answer"] == mock_response.answer

        mock_generate.assert_awaited_once()

    async def test_ask_rejects_invalid_limit(self, api_client):
        response = await api_client.post("/ask", json={"q": "stuns and explodes", "limit": 0})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
