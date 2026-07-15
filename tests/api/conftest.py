import pytest
from unittest.mock import patch

from httpx import AsyncClient, ASGITransport

from app.main import app
from app.rag.vector_store import ensure_collection, client
from app.rag.embeddings import get_embeddings
from app.api.schemas import GemPayload
from qdrant_client.models import PointStruct

TEST_QDRANT_COLLECTION = "poe2-skill-gems-test"

SAMPLE_GEMS = [
    {
        "id": 1,
        "name": "Boneshatter",
        "tags": ["attack", "melee", "physical"],
        "description": "Stuns nearby enemies and explodes, dealing physical damage.",
    },
    {
        "id": 2,
        "name": "Fireball",
        "tags": ["spell", "fire", "projectile"],
        "description": "Launches a fireball that explodes on impact, dealing fire damage.",
    },
    {
        "id": 3,
        "name": "Raise Zombie",
        "tags": ["minion", "physical"],
        "description": "Summons a zombie minion to fight alongside you.",
    },
]


@pytest.fixture
async def seeded_search_collection():
    with patch("app.config.settings.QDRANT_COLLECTION", TEST_QDRANT_COLLECTION):
        await ensure_collection()

        descriptions = [g["description"] for g in SAMPLE_GEMS]
        vectors = await get_embeddings(descriptions)
        points = [
            PointStruct(id=g["id"], vector=v, payload=GemPayload(**g).model_dump())
            for g, v in zip(SAMPLE_GEMS, vectors)
        ]
        await client.upsert(collection_name=TEST_QDRANT_COLLECTION, wait=True, points=points)

        yield

        await client.delete_collection(TEST_QDRANT_COLLECTION)


@pytest.fixture
async def api_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
