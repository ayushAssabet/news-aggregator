from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from .trending_engine import trending_engine


def update_trending_scores(db: Session) -> dict[str, int]:
    """
    Background job to update trending scores.

    Run every 15–30 minutes by Celery/APScheduler,
    or call manually through FastAPI.
    """
    # Efficient selection from last 48 hours
    query = text(
        """
        SELECT 
            id, 
            published_at, 
            source, 
            category, 
            COALESCE(similar_news, '[]') AS similar_news
        FROM news
        WHERE published_at > NOW() - INTERVAL '48 hours'
        """
    )

    result = db.execute(query)
    news_items = result.fetchall()

    updates: list[dict[str, Any]] = []

    for item in news_items:
        score_data = trending_engine.calculate_trending_score(
            published_at=item.published_at,
            source=item.source,
            category=item.category,
            similar_news=item.similar_news,
        )

        updates.append(
            {
                "id": item.id,
                "score": score_data["trending_score"],
                "count": score_data["coverage_count"],
            }
        )

    # Nothing to update; exit early
    if not updates:
        return {"updated": 0}

    # Batch updates (safe + fast)
    BATCH_SIZE = 500
    total_updated = 0

    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i : i + BATCH_SIZE]

        # Build VALUES placeholders
        values_sql = ",".join(
            f"(:id_{i+n}, :score_{i+n}, :count_{i+n})"
            for n in range(len(batch))
        )

        # Bind parameters safely
        params = {
            f"id_{i+n}": row["id"]
            for n, row in enumerate(batch)
        }
        params.update(
            {
                f"score_{i+n}": row["score"]
                for n, row in enumerate(batch)
            }
        )
        params.update(
            {
                f"count_{i+n}": row["count"]
                for n, row in enumerate(batch)
            }
        )

        update_query = text(
            f"""
            UPDATE news
            SET 
                trending_score = data.score,
                coverage_count = data.count,
                last_score_update = NOW()
            FROM (VALUES {values_sql}) AS data(id, score, count)
            WHERE news.id = data.id
            """
        )

        db.execute(update_query, params)
        total_updated += len(batch)

    db.commit()

    return {"updated": total_updated}
