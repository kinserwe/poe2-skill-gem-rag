# PoE2 Skill Gem RAG

A small Retrieval-Augmented Generation (RAG) app for searching Path of Exile 2 skill gems
using natural language, built with FastAPI + Qdrant + sentence-transformers.

## Stack
- **FastAPI** — API layer
- **Qdrant** — vector database for storing gem embeddings
- **sentence-transformers** (`all-MiniLM-L6-v2`) — local embedding model, runs in-process
- **Gemini** (`google-genai`) — answer generation for `/ask`
- **BeautifulSoup** — scrapes the gem dataset from poe2db.tw
- **uv** — dependency management
- **Docker Compose** — app + Qdrant, runs locally with one command

## Setup

Copy the example environment file and fill in a Gemini API key:
```bash
cp .env.example .env
```

`GEMINI_API_KEY` is **required** — the app reads settings at import time and will not
start without it. The remaining variables have working defaults.

| Variable | Default | Notes |
|---|---|---|
| `QDRANT_URL` | `http://localhost:6333` | Compose overrides this to `http://qdrant:6333` |
| `QDRANT_HOST_PORT` | `6333` | Compose only — host port Qdrant is published on |
| `QDRANT_COLLECTION` | `poe2-skill-gems` | |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Also baked into the Docker image at build time |
| `GEMINI_API_KEY` | — | Required |
| `GEMINI_MODEL` | `gemini-3.1-flash-lite` | |

## Running locally

```bash
docker compose up --build
```

- API: http://localhost:8003
- Qdrant dashboard: http://localhost:6333/dashboard (or `QDRANT_HOST_PORT`)

The collection starts empty. Populate it before querying:

```bash
docker compose exec app python -m scripts.ingest
```

Endpoints: `GET /search`, `POST /ask`, `GET /health`.

## Usage

### Refreshing the dataset

`data/skills.json` is committed, so this is only needed when the game patches:

```bash
uv run python -m scripts.parser
```

Scrapes [poe2db.tw](https://poe2db.tw/us/Skill_Gems) in a single request and rewrites
`data/skills.json`. Re-run the ingest afterwards.

### Ingesting

```bash
uv run python -m scripts.ingest             # local
docker compose exec app python -m scripts.ingest   # in compose
```

Accepts `--path` to ingest a different JSON file.

Ingestion is idempotent — gems are upserted under a stable id derived from their
poe2db slug, so re-running updates in place. It does **not** delete points that are
no longer in the dataset; drop the collection first if you need a clean rebuild.

### Search

```bash
curl "http://localhost:8003/search?q=chaining+lightning+bow&limit=3"
```

Returns matching gems ranked by semantic similarity, e.g.:
```json
[
  {
    "id": 98517804654556,
    "name": "Lightning Arrow",
    "tags": ["Attack", "AoE", "Projectile", "Lightning", "Chaining", "Repeatable"],
    "weapons": ["Bow"],
    "description": "Fire a charged arrow at the target. On hitting an enemy or wall, the arrow will fire Chaining Lightning beams at nearby enemies."
  }
]
```

### Ask

```bash
curl "http://localhost:8003/ask" -H "Content-Type: application/json" \
  -d '{"q": "what bow skill uses lightning", "limit": 8}'
```

Returns a Gemini-generated answer grounded in the retrieved gems, alongside the
sources it was given:
```json
{
  "answer": "Lightning Arrow is a good fit. It fires a charged arrow that sends chaining lightning beams to nearby enemies, which makes it strong for clearing groups.",
  "sources": [
    {
      "id": 98517804654556,
      "name": "Lightning Arrow",
      "tags": ["Attack", "AoE", "Projectile", "Lightning", "Chaining", "Repeatable"],
      "weapons": ["Bow"],
      "description": "Fire a charged arrow at the target. On hitting an enemy or wall, the arrow will fire Chaining Lightning beams at nearby enemies."
    }
  ]
}
```

## Dataset

387 skill gems scraped from poe2db.tw. The parser reads a single page and joins two
of its tabs: the summary list supplies name, tags and description, while the
gemcutting table supplies weapon restrictions (182 gems have one; the rest, such as
Archmage, genuinely aren't weapon-bound).

Excluded from the index:
- **Weapon default attacks** (`Bow Shot`, `Mace Strike`, …) — not socketable gems, and
  their generic descriptions ("Fire an arrow with your Bow.") outranked real gems.
- **Unrendered site templates** — entries whose name still contains a `{0}` placeholder.
- **Gems with no description** — 8 companion command skills whose text isn't on the
  summary page. They would embed to near-meaningless vectors.

## Testing

```bash
uv run pytest
```

Integration and API tests need a running Qdrant. Unit tests, including the parser
tests, run against committed fixtures with no network access.

## Why these choices
- Local embeddings instead of an API-based model: no API key required for retrieval,
  fully reproducible, no per-query cost — reasonable trade-off for a domain this small.
- Qdrant over a SQL-based full-text search: gem descriptions and tags benefit
  from semantic similarity matching (e.g. "chaining lightning" should surface
  gems like Lightning Arrow even without exact keyword overlap).

## Design notes

- **Stable, content-derived ids** — a gem's id is a 48-bit BLAKE2b hash of its poe2db
  slug rather than its position in the dataset. Enumeration would renumber every gem
  whenever one is added or removed, orphaning the points already stored in Qdrant.
  48 bits also keeps ids below JavaScript's safe-integer limit.
- **Name and tags are embedded, not just the description** — the text sent to the
  embedder is `name. Tags: … Weapons: … description`. Embedding the description alone
  meant a query like "lightning bow skill" ranked Lightning Arrow 7th, because the
  two words it matches on live in the gem's *name* and *tags*.
- **Async I/O, threaded CPU work** — Qdrant calls run through `AsyncQdrantClient`
  since they're I/O-bound. Embedding generation (`sentence-transformers`) is
  CPU-bound with no I/O to await, so it's explicitly offloaded to a threadpool
  instead, keeping the event loop free to serve other requests while it runs.
- **The embedding model is loaded lazily and baked into the image** — a cached
  accessor keeps imports cheap for tests and scripts, and the lifespan warms it at
  startup so the first request doesn't pay the load. The Docker build downloads the
  model and sets `HF_HUB_OFFLINE=1`, so a running container never needs the network.
- **Separate schemas for storage and API** — `GemPayload` (what's stored in
  Qdrant) and `SearchResult` (what `/search` returns) are defined separately,
  even though they're identical today. This keeps the storage layer and the
  public API contract free to diverge independently as the project grows
  (e.g. adding filter-only fields to the payload, or a relevance `score` to
  the response, without one change forcing the other).

## Roadmap
- [x] Ingest pipeline for the full gem dataset from [poe2db.tw](https://poe2db.tw/us/Skill_Gems)
- [ ] Hybrid search: combine vector similarity with tag and weapon filtering
- [ ] Basic retrieval evaluation (test queries + expected results)
- [ ] Backfill the 8 missing descriptions from individual gem pages
