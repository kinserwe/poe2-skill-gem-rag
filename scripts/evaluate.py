import argparse
import asyncio
import json
import logging
from pathlib import Path

from app.logging_config import configure_logging
from app.rag.vector_store import search

_QUERIES_PATH = Path(__file__).parent.parent / "evals" / "queries.json"
_BASELINE_PATH = Path(__file__).parent.parent / "evals" / "baseline.json"
_RANK_LIMIT = 10
_REPORTED_CUTOFFS = (1, 3, 8)

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Measure retrieval quality against labelled queries"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=_QUERIES_PATH,
        help="Path to the labelled query file (default: evals/queries.json)",
    )
    parser.add_argument(
        "--save-baseline",
        action="store_true",
        help="Write the results to evals/baseline.json for future runs to compare against",
    )
    return parser.parse_args()


async def rank_of_expected(query: str, expected: list[str]) -> int | None:
    results = await search(query, _RANK_LIMIT)
    for position, result in enumerate(results, start=1):
        if result.name in expected:
            return position
    return None


def load_baseline(path: Path = _BASELINE_PATH) -> dict[str, int | None]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def summarise(ranks: dict[str, int | None]) -> dict[str, float]:
    total = len(ranks)
    found = [rank for rank in ranks.values() if rank is not None]
    summary = {f"recall@{k}": sum(r <= k for r in found) / total for k in _REPORTED_CUTOFFS}
    summary["mrr"] = sum(1 / r for r in found) / total
    return summary


def format_delta(current: int | None, previous: int | None, in_baseline: bool) -> str:
    if not in_baseline:
        return "  new query"
    if current == previous:
        return ""
    if previous is None:
        return f"  was missing -> {current} better"
    if current is None:
        return f"  {previous} -> missing WORSE"
    direction = "better" if current < previous else "WORSE"
    return f"  {previous} -> {current} {direction}"


async def evaluate(path: Path, save_baseline: bool) -> dict[str, float]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    baseline = load_baseline()
    ranks: dict[str, int | None] = {}

    for case in cases:
        query = case["q"]
        rank = await rank_of_expected(query, case["expect"])
        ranks[query] = rank
        shown = rank if rank is not None else f"not in top {_RANK_LIMIT}"
        delta = format_delta(rank, baseline.get(query), query in baseline)
        logger.info("rank %-18s %s%s", shown, query, delta)

    summary = summarise(ranks)
    logger.info(
        "%d queries | %s | mrr %.3f",
        len(cases),
        " ".join(f"{k} {v:.0%}" for k, v in summary.items() if k != "mrr"),
        summary["mrr"],
    )

    if save_baseline:
        _BASELINE_PATH.write_text(json.dumps(ranks, indent=2), encoding="utf-8")
        logger.info("Wrote baseline to %s", _BASELINE_PATH)

    return summary


def main() -> None:
    configure_logging()
    args = parse_args()
    asyncio.run(evaluate(args.path, args.save_baseline))


if __name__ == "__main__":
    main()
