from app.api.schemas import SearchResult
from app.rag.genai_client import build_prompt


class TestBuildPrompt:
    def test_build_prompt(self):
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
