import os
import sys
from pathlib import Path
from typing import Optional, Sequence


def run_trending_scrape(sources: Optional[Sequence[str]] = None) -> dict:
    """
    Programmatically run the Scrapy spider within the project, ensuring the
    Scrapy settings and pipelines are applied. Returns a small status dict.
    """
    # Ensure the Scrapy project (news_spider) is importable
    # Adjusted for new location (one level deeper under services/scraping)
    repo_root = Path(__file__).resolve().parents[4]  # points to project root
    scrapy_project_path = repo_root / "scraper" / "news_spider"
    if str(scrapy_project_path) not in sys.path:
        sys.path.insert(0, str(scrapy_project_path))

    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "news_spider.settings")

    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from news_spider.spiders.news_spider import NewsSpider

    settings = get_project_settings()

    process = CrawlerProcess(settings=settings)
    # Optionally, could pass args to the spider here from `sources`
    process.crawl(NewsSpider)
    process.start(stop_after_crawl=True)

    return {"status": "success"}
