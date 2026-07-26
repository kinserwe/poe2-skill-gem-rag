import argparse
import asyncio
import json
import logging
from pathlib import Path

from qdrant_client.models import PointStruct

from app.api.schemas import GemPayload
from app.config import settings
from app.logging_config import configure_logging
from app.rag.embeddings import get_embeddings
from app.rag.vector_store import client, ensure_collection

DATA_PATH = Path(__file__).parent.parent / "data" / "skills.json"

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Ingest gem data into Qdrant")
    parser.add_argument(
        "--path",
        type=Path,
        default=DATA_PATH,
        help="Path to the gems JSON file (default: data/skills.json)",
    )
    return parser.parse_args()


async def load_data(path: Path):
    with open(path, "r") as f:
        data = json.load(f)

    logger.info("Loaded %d gems from %s", len(data), path)

    await ensure_collection()

    descriptions = [gem["description"] for gem in data]
    vectors = await get_embeddings(descriptions)
    points = []
    for gem, vector in zip(data, vectors):
        payload = GemPayload(**gem)
        points.append(PointStruct(id=payload.id, vector=vector, payload=payload.model_dump()))

    result = await client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        wait=True,
        points=points,
    )
    logger.info("Upserted %d gems into %s", len(points), settings.QDRANT_COLLECTION)
    return result


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    asyncio.run(load_data(args.path))
