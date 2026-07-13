import logging

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

from app.api.schemas import SearchResult
from app.config import settings
from app.rag.embeddings import embedding_model, get_embeddings

client = AsyncQdrantClient(settings.QDRANT_URL)

logger = logging.getLogger(__name__)


async def ensure_collection() -> None:
    if not await client.collection_exists(settings.QDRANT_COLLECTION):
        vector_size = embedding_model.get_sentence_embedding_dimension()

        await client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


async def search(query: str, limit: int = 3) -> list[SearchResult]:
    embeddings = (await get_embeddings([query]))[0]
    result = await client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=embeddings,
        with_payload=True,
        limit=limit,
    )
    return [SearchResult(**point.payload) for point in result.points]
