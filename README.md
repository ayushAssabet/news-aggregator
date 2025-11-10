
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
