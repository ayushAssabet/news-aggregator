from datetime import datetime, timezone
import math
from typing import List

from .trending_config import (
    SOURCE_WEIGHTS,
    CATEGORY_WEIGHTS,
    MIN_RECENCY_SCORE,
    DEFAULT_CATEGORY_WEIGHT,
    DEFAULT_SOURCE_WEIGHT,
)


def calculate_recency_score(published_at: datetime, decay_hours: float = 12.0) -> float:
    """Exponential decay based on time."""
    now = datetime.now(timezone.utc)
    hours_old = (now - published_at).total_seconds() / 3600

    decay_rate = math.log(2) / decay_hours
    score = math.exp(-decay_rate * hours_old)

    return max(score, MIN_RECENCY_SCORE)


def calculate_coverage_score(similar_news: List[dict]) -> tuple[float, int]:
    """
    Coverage score based on how many portals covered similar story.
    Returns (score, count).
    """
    if not similar_news:
        return 1.0, 1

    coverage_count = len(similar_news) + 1  
    coverage_score = 1 + math.log(coverage_count, 2) * 0.5

    return coverage_score, coverage_count


def get_source_weight(source: str) -> float:
    """Get credibility weight for news source."""
    if not source:
        return DEFAULT_SOURCE_WEIGHT

    key = source.lower().strip()
    return SOURCE_WEIGHTS.get(key, DEFAULT_SOURCE_WEIGHT)


def get_category_weight(category: str) -> float:
    """Get importance weight for category."""
    if not category:
        return DEFAULT_CATEGORY_WEIGHT

    key = category.lower().strip()
    return CATEGORY_WEIGHTS.get(key, DEFAULT_CATEGORY_WEIGHT)
