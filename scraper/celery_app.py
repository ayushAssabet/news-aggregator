from celery import Celery
from app.config.settings import settings

redis_url = settings.redis_url
schedule_seconds = float(settings.scrape_schedule_seconds)

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
