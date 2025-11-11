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
        from api.app.services.scraping.scraping_service import run_trending_scrape

        result = run_trending_scrape()
        print("Scrapy service finished.")
        return {"status": "success", "result": result}
    except Exception as e:
        print("Scrapy service failed:", e)
        return {"status": "error", "error": str(e)}
