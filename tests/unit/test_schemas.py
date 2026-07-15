import pytest
from pydantic import ValidationError

from app.api.schemas import GemPayload, SearchResult


class TestGemPayload:
    def test_valid_payload(self):
        payload = GemPayload(
            id=1,
            name="Boneshatter",
            tags=["attack", "melee", "physical"],
            description="...",
        )
        assert payload.id == 1
        assert payload.name == "Boneshatter"
        assert "melee" in payload.tags

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            GemPayload(
                id=1,
                name="Boneshatter",
                tags=["attack"],
            )

    def test_wrong_type_id_raises(self):
        with pytest.raises(ValidationError):
            GemPayload(id="not-an-int", name="Boneshatter", tags=["attack"], description="...")

    def test_tags_must_be_list(self):
        with pytest.raises(ValidationError):
            GemPayload(
                id=1,
                name="Boneshatter",
                tags="attack, melee, physical",
                description="...",
            )

    def test_extra_fields_are_ignored(self):
        payload = GemPayload(
            id=1,
            name="Boneshatter",
            tags=["attack", "melee", "physical"],
            description="...",
            level_requirement=12,
        )
        assert not hasattr(payload, "level_requirement")


class TestSearchResult:
    def test_valid_result(self):
        result = SearchResult(
            id=1,
            name="Boneshatter",
            tags=["attack", "melee"],
            description="...",
        )
        assert result.id == 1

    def test_constructed_from_qdrant_style_payload_dict(self):
        payload_dict = {
            "id": 2,
            "name": "Fireball",
            "tags": ["spell", "fire", "projectile"],
            "description": "...",
        }
        result = SearchResult(**payload_dict)
        assert result.name == "Fireball"

    def test_missing_field_raises(self):
        with pytest.raises(ValidationError):
            SearchResult(id=1, name="Fireball", tags=["fire"])
