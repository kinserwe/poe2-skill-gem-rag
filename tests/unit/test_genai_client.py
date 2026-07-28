from unittest.mock import AsyncMock, patch

from app.api.schemas import SearchResult
from app.rag.genai_client import generate_answer, build_prompt


class TestGenerateAnswer:
    async def test_generate_answer(self):
        context = [
            SearchResult(
                id=1,
                name="Boneshatter",
                tags=["AoE", "Melee", "Strike"],
                description="Attack enemies with a melee Strike. The Strike will cause a Heavy Stun on enemies that are Primed for Stun. Upon causing a Heavy Stun it will also create a Shockwave, dealing a large amount of damage in an area.",
            ),
        ]

        expected_answer = "Boneshatter stuns and explodes"

        mock_response = AsyncMock()
        mock_response.text = expected_answer

        with patch("app.rag.genai_client.client") as mock_client:
            mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

            result = await generate_answer("stuns and explodes", context)

        assert result.answer == expected_answer
        assert result.sources == context

    async def test_generate_answer_none_text_falls_back(self):
        context = [
            SearchResult(
                id=1,
                name="Boneshatter",
                tags=["AoE", "Melee", "Strike"],
                description="Attack enemies with a melee Strike.",
            ),
        ]

        mock_response = AsyncMock()
        mock_response.text = None

        with patch("app.rag.genai_client.client") as mock_client:
            mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

            result = await generate_answer("stuns and explodes", context)

        assert result.answer == "No answer could be generated for this question."
        assert result.sources == context


class TestBuildPrompt:
    def test_includes_query_and_gem_text(self):
        query = "Skill that stuns and explodes"
        context = [
            SearchResult(
                id=1,
                name="Boneshatter",
                tags=["AoE", "Melee", "Strike"],
                description="Attack enemies with a melee Strike. The Strike will cause a Heavy Stun on enemies that are Primed for Stun. Upon causing a Heavy Stun it will also create a Shockwave, dealing a large amount of damage in an area.",
            ),
        ]

        prompt = build_prompt(query, context)
        assert query in prompt
        assert all(gem.name in prompt for gem in context)
        assert all(gem.description in prompt for gem in context)
