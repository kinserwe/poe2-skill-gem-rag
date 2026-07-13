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
- API: http://localhost:8003/health
- Qdrant dashboard: http://localhost:6333/dashboard

## Why these choices
- Local embeddings instead of an API-based model: no API key required, fully
  reproducible, no per-query cost — reasonable trade-off for a domain this small.
- Qdrant over a SQL-based full-text search: gem descriptions and tags benefit
  from semantic similarity matching (e.g. "stuns and explodes" should surface
  gems like Boneshatter even without exact keyword overlap).
