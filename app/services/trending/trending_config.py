# Configuration file for Trending Engine

SOURCE_WEIGHTS = {
    'kantipur': 0.95,
    'ekantipur': 0.95,
    'onlinekhabar': 0.90,
    'setopati': 0.85,
    'ratopati': 0.80,
    'nepalipaisa': 0.75,
    'annapurnapost': 0.85,
}

CATEGORY_WEIGHTS = {
    'politics': 1.0,
    'breaking': 1.2,
    'national': 1.0,
    'economy': 0.9,
    'international': 0.8,
    'sports': 0.7,
    'entertainment': 0.6,
    'lifestyle': 0.5,
}

MIN_RECENCY_SCORE = 0.01
DEFAULT_CATEGORY_WEIGHT = 0.7
DEFAULT_SOURCE_WEIGHT = 0.6
