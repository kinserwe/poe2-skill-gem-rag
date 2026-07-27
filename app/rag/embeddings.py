import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer
from starlette.concurrency import run_in_threadpool

from app.config import settings


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
    return SentenceTransformer(settings.EMBEDDING_MODEL)


async def get_embeddings(to_embed: list[str]) -> list[list[float]]:
    embedding_model = get_embedding_model()
    embeddings = await run_in_threadpool(
        embedding_model.encode, to_embed, normalize_embeddings=True
    )
    return embeddings.tolist()
