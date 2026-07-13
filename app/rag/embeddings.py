import logging

from sentence_transformers import SentenceTransformer
from starlette.concurrency import run_in_threadpool

from app.config import settings

embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

logger = logging.getLogger(__name__)


async def get_embeddings(to_embed: list[str]) -> list[list[float]]:
    embeddings = await run_in_threadpool(
        embedding_model.encode, to_embed, normalize_embeddings=True
    )
    return embeddings.tolist()
