# Homelessness Research Data Scraper

Comprehensive data collection tool for homelessness research from multiple sources.

## Quick Start

```bash
python master_scraper.py --duration 120
```

## What It Does

Collects data from 4 sources sequentially:

1. **Google Trends** (3-4 min) - Extracts trending homelessness keywords
2. **News API** (~5s) - Collects news articles with dual classification (keyword + AI)
3. **Reddit** (~20s) - Scrapes 9 homelessness subreddits
4. **Bluesky** (~30-60s) - Social media posts with polarization analysis

## Output

All data saved to: `data/master_output/session_YYYYMMDD_HHMMSS/`

Files created:
- `googletrends_*.xlsx` - Trend data
- `news_api_articles.csv/json` - News articles
- `news_api_classified.csv/json` - Dual classification results
- `reddit_posts.csv/json` - Reddit posts
- `homelessness_posts.csv/jsonl` - Bluesky posts with polarization
- `master_log_*.json` - Complete execution log

## Features

### News API - Dual Classification
- **Keyword-based** (fast): Uses political keyword matching
- **HuggingFace AI** (slow): Uses politicalBiasBERT model
- Compares speed and accuracy between methods

### Bluesky - Polarization Analysis
Every post includes:
- `political_leaning`: LEFT, RIGHT, or NEUTRAL
- `polarization_confidence`: Confidence score (0-1)
- `left_keywords_count`: Number of left-leaning keywords
- `right_keywords_count`: Number of right-leaning keywords

### Reddit - Comprehensive Coverage
Scrapes from 9 subreddits:
- homeless, housing, eviction, affordablehousing
- rent, shelter, housingcrisis, povertyfinance, urbancarliving

### Google Trends - Full Analysis
- National and state-level trends
- Seasonal analysis
- Interactive choropleth maps
- Time series visualizations

## Requirements

```bash
pip install -r requirements.txt
```

API Keys needed:
- News API: `scripts/news_api/credentials.py`
- Reddit: `scripts/reddit/config.py`
- Bluesky: `auth/bluesky/config/auth.json`

## Parameters

- `--duration`: Total time budget in seconds (default: 60)

Time is allocated:
- 15% to Google Trends (minimum 3 minutes)
- 30% to News API
- 25% to Reddit
- 30% to Bluesky

## Notes

- Google Trends takes 3-4 minutes regardless of time budget (comprehensive analysis)
- All modules save both JSON and CSV formats
- Only latest 3 sessions are kept to save space
- All data focuses on homelessness research

## Success Rate

Typical run: **4/4 modules succeed** (100%)
- Google Trends: Always succeeds (patient execution)
- News API: Fast, usually finds 5-20 articles
- Reddit: Reliable, collects 60+ posts
- Bluesky: Requires authentication, collects 100+ posts
