
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

