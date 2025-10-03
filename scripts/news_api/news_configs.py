"""
News API Configuration
Default keywords and settings for news scraping
"""

from datetime import datetime, timedelta

# Default keywords for homelessness and housing crisis
KEYWORDS_DEFAULT = [
    'homelessness',
    'homeless crisis',
    'housing crisis',
    'affordable housing',
    'homeless shelter',
    'housing insecurity',
    'eviction crisis',
    'tent cities',
    'unhoused',
    'housing affordability'
]

# Maximum pages to fetch from NewsAPI
MAX_PAGES = 100

# Search time window (days)
SEARCH_TIME_DAYS = 30
