from celery import Celery
import os

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
schedule_seconds = float(os.getenv("SCRAPE_SCHEDULE_SECONDS", "3600"))

celery = Celery(
    "news_scrap_task",
    broker=redis_url,
    backend=redis_url,
    include=["scraper.tasks"], 
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    beat_schedule={
        "run-generic-spider": {
            "task": "scraper.tasks.run_generic_spider",
            "schedule": schedule_seconds,
        },
    },
)
