
# News Ingestion Scaffold

A production-ready scaffold for scraping Nepali news portals, deduplicating and scoring reliability, and serving articles via a FastAPI API.

## Quickstart
```bash
cp .env.sample .env
docker compose up --build
docker compose exec api alembic upgrade head
```
Open API docs at: http://localhost:8000/docs

See `TREE.txt` for structure and notes in comments across the codebase.

## Git Branch Naming

Use consistent, kebab-cased prefixes to communicate intent:

- feature/<short-description>    e.g., feature/add-article-endpoints
- fix/<short-description>        e.g., fix/ranking-score-bug
- hotfix/<short-description>     e.g., hotfix/production-startup-failure
- chore/<short-description>      e.g., chore/bump-dependencies
- docs/<short-description>       e.g., docs/update-readme-tree
- refactor/<short-description>   e.g., refactor/split-router-controller

## Useful commands

- alembic revision --autogenerate -m "your table name"



## Scaling hints

- Storing article

Currently you re-fetch all of today’s articles’ embeddings every time.
That’s okay for hundreds, but if you start handling thousands per day, consider:

Adding an IVFFlat index:
```bash
CREATE INDEX idx_articles_embedding ON articles USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

Restrict candidate set further (e.g., same source_id or similar category).
Move deduplication logic into a stored procedure or API endpoint when scaling up.

## Embeddings

- Provider: Google Gemini embeddings via `text-embedding-004` (768-dim)
- Env: set `GEMINI_API_KEY` and optionally `GEMINI_EMBEDDING_MODEL` (defaults to `text-embedding-004`).
- DB: embedding column resized to `vector(768)`; run `alembic upgrade head` after pulling changes.
