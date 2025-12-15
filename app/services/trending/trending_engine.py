from __future__ import annotations

from datetime import datetime
from typing import List

from .trending_features import (
    calculate_recency_score,
    calculate_coverage_score,
    get_source_weight,
    get_category_weight,
)





class TrendingEngine:
    def calculate_trending_score(
        self,
        published_at: datetime,
        source: str,
        category: str,
        similar_news: List[dict],
        boost_factor: float = 1.0,
    ) -> dict:
        """
        Calculate final trending score and return full breakdown.
        """
        recency = calculate_recency_score(published_at)
        source_weight = get_source_weight(source)
        category_weight = get_category_weight(category)
        coverage_score, coverage_count = calculate_coverage_score(similar_news)

        final_score = (
            recency * 0.40
            + coverage_score * 0.30
            + source_weight * 0.20
            + category_weight * 0.10
        ) * boost_factor

        return {
            "trending_score": round(final_score, 6),
            "coverage_count": coverage_count,
            "breakdown": {
                "recency": round(recency, 3),
                "coverage": round(coverage_score, 3),
                "source": round(source_weight, 3),
                "category": round(category_weight, 3),
            },
        }


trending_engine = TrendingEngine()

