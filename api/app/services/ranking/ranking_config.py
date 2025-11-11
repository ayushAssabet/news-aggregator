from __future__ import annotations


from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RankingConfig:
    # Weighting for score components
    w_recency: float = 0.5
    w_reliability: float = 0.3
    w_length: float = 0.15
    w_category: float = 0.05

    # Recency decay: half life in hours (newer articles get higher score)
    recency_half_life_hours: float = 6.0

    # Length heuristic
    min_content_chars: int = 300
    target_content_chars: int = 1500

    # Candidate selection
    max_age_hours: int = 72
    max_candidates: int = 1000

    # Category boosts
    category_boosts: Dict[str, float] = field(
        default_factory=lambda: {
            "MUKHYA_SAMACHAR": 0.10,
            "RAJNITI": 0.06,
            "PRAVIDHI": 0.04,
            "JALAVAYU": 0.04,
            "ANTARRASHTRIYA": 0.03,
        }
    )
