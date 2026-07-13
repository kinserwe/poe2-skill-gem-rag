# PoE2 Skill Gem RAG

A small Retrieval-Augmented Generation (RAG) app for searching Path of Exile 2 skill gems
using natural language, built with FastAPI + Qdrant + sentence-transformers.

## Stack
- **FastAPI** — API layer
- **Qdrant** — vector database for storing gem embeddings
- **sentence-transformers** (`all-MiniLM-L6-v2`) — local embedding model, no external API needed
- **uv** — dependency management
- **Docker Compose** — app + Qdrant, runs locally with one command

## Running locally
```bash
docker compose up --build
```
- API: http://localhost:8003/search
- Qdrant dashboard: http://localhost:6333/dashboard

## Usage

Ingest the sample dataset:
```bash
python -m scripts.ingest
```

Search:
```bash
curl "http://localhost:8003/search?q=stuns+and+explodes&limit=3"
```

Returns matching gems ranked by semantic similarity, e.g.:
```json
[{"id": 1, "name": "Boneshatter", "tags": [...], "description": "..."}]
```

## Why these choices
- Local embeddings instead of an API-based model: no API key required, fully
  reproducible, no per-query cost — reasonable trade-off for a domain this small.
- Qdrant over a SQL-based full-text search: gem descriptions and tags benefit
  from semantic similarity matching (e.g. "stuns and explodes" should surface
  gems like Boneshatter even without exact keyword overlap).

## Design notes

- **Idempotent ingestion** — points are upserted using the gem's own `id` as the
  Qdrant point ID, so re-running the ingestion script updates existing gems in
  place instead of creating duplicates.
- **Async I/O, threaded CPU work** — Qdrant calls run through `AsyncQdrantClient`
  since they're I/O-bound. Embedding generation (`sentence-transformers`) is
  CPU-bound with no I/O to await, so it's explicitly offloaded to a threadpool
  instead, keeping the event loop free to serve other requests while it runs.
- **Separate schemas for storage and API** — `GemPayload` (what's stored in
  Qdrant) and `SearchResult` (what `/search` returns) are defined separately,
  even though they're identical today. This keeps the storage layer and the
  public API contract free to diverge independently as the project grows
  (e.g. adding filter-only fields to the payload, or a relevance `score` to
  the response, without one change forcing the other).

## Dataset

Currently indexed against a small hand-written sample of gems. See Roadmap
below for scaling to the full gem list.

## Roadmap
- [ ] Ingest pipeline for the full ~400 gem dataset from [poe2db.tw](https://poe2db.tw/Skill_Gems)
- [ ] Hybrid search: combine vector similarity with tag-based filtering
- [ ] Basic retrieval evaluation (test queries + expected results)
