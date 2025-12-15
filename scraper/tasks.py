#!/usr/bin/env python3
# scraper/tasks.py
from scraper.celery_app import celery as celery_app  # shared Celery instance


@celery_app.task(name="scraper.tasks.run_generic_spider")
def run_generic_spider():
    """
    Invoke scraping via the service layer (no subprocess), so we run Scrapy
    programmatically and reuse our pipelines and settings.
    """
    try:
        print("Starting news_spider crawl via service...")
        # Import here to avoid Celery eager import issues
        from app.services.scraper.scraping_service import run_trending_scrape

        result = run_trending_scrape()
        print("Scrapy service finished.")
        return {"status": "success", "result": result}
    except Exception as e:
        print("Scrapy service failed:", e)
        return {"status": "error", "error": str(e)}


@celery_app.task(name="scraper.tasks.update_trending_scores")
def run_update_trending_scores():
    """
    Periodic task to recompute trending scores for recent news.
    """
    try:
        from app.database.db import SessionLocal
        from app.services.trending import update_trending_scores

        db = SessionLocal()
        try:
            result = update_trending_scores(db)
        finally:
            db.close()

        return {"status": "success", **result}
    except Exception as e:
        print("Trending score update failed:", e)
        return {"status": "error", "error": str(e)}

