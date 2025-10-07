# NGO Intelligence Platform - Homelessness Research

Comprehensive multi-source data collection and analysis platform for homelessness research. Collects data from Google Trends, News APIs, Reddit, and Bluesky with automated visualizations and political analysis.

**Carnegie Mellon University - DFP F25**

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 2. Run Master Scraper

```bash
# Run comprehensive scraper (15 minutes for full analysis)
python3 master_scraper.py --duration 900

# Quick test run (5 minutes - uses cached Google Trends if available)
python3 master_scraper.py --duration 300
```

### 3. View Results

All data saved to: `data/master_output/session_YYYYMMDD_HHMMSS/`

---

## 📊 What It Collects

The master scraper runs **4 modules sequentially**:

| Module | Duration | What It Collects | Visualizations |
|--------|----------|------------------|----------------|
| **Google Trends** | ~13 min (fresh) <br> <1 sec (cached) | Search trends, keywords, geographic data | 20+ charts & maps |
| **News API** | ~30 sec | 75+ articles from NewsAPI + NPR | 4 visualizations |
| **Reddit** | ~30 sec | 150+ posts from 9 subreddits | Raw data (CSV/JSON) |
| **Bluesky** | ~1 sec | Social media posts | Script integration |

**Total Output:** ~36 files per run including data, visualizations, and logs

---

## 📁 Output Structure

```
data/master_output/session_20251006_123042/
├── Google Trends (28 files)
│   ├── googletrends_national_*.xlsx       # National trends data
│   ├── googletrends_state_*.xlsx          # State-level trends
│   ├── googletrends_help_*.csv            # Help-seeking queries
│   ├── googletrends_mapdata_*.pkl         # Geographic data
│   └── viz_*.png/html (20 visualizations)
│       ├── national_timeseries            # National trends over time
│       ├── CA_timeseries                  # California state trends
│       ├── theme_comp                     # Theme comparison chart
│       ├── national_seasonal_* (4)        # National seasonal patterns
│       ├── state_seasonal_* (4)           # State seasonal patterns
│       └── choropleth_*.html (2)          # Interactive maps
│
├── News API (6 files)
│   ├── combined_articles.json             # 75 articles (NewsAPI + NPR)
│   ├── classified.csv                     # Political classification
│   └── news_*.png (4 visualizations)
│       ├── wordcloud                      # Most common words
│       ├── outlet_counts                  # Articles by outlet
│       ├── political_pie                  # LEFT/CENTER/RIGHT split
│       └── political_timeline             # Coverage over time
│
├── Reddit (2 files)
│   ├── reddit_posts.csv                   # 150+ posts with metadata
│   └── reddit_posts.json                  # Same data in JSON format
│
└── Master Log
    └── master_log_*.json                  # Complete execution log
```

---

## 🔧 Installation Guide

### Prerequisites

- **Python 3.8+** (tested on 3.13)
- **pip** package manager
- Internet connection for API calls

### Step-by-Step Setup

1. **Clone/Download the Repository**
```bash
cd /path/to/dfp_ngo_module
```

2. **Install All Dependencies**
```bash
pip install -r requirements.txt
```

This installs:
- Core: `pandas`, `numpy`, `requests`
- Google Trends: `pytrends`, `geopandas`, `folium`, `statsmodels`
- News API: `newsapi-python`, `beautifulsoup4`, `wordcloud`, `transformers`, `torch`
- Reddit: `praw`, `textblob`
- Bluesky: `atproto`
- Visualization: `matplotlib`, `seaborn`, `plotly`

3. **Configure API Keys (Optional)**

For News API:
```bash
# Edit scripts/news_api/credentials.py
NEWS_API_KEY = "your_api_key_here"  # Get from https://newsapi.org
```

For Reddit (optional - works without):
```bash
# Edit scripts/reddit/config.py if you have Reddit API credentials
```

For Bluesky (optional):
```bash
# Edit auth/bluesky/config/auth.json if you have Bluesky account
```

---

## 🎯 Usage

### Master Scraper (Recommended)

Runs all 4 modules sequentially:

```bash
# Comprehensive run (15-20 minutes)
python3 master_scraper.py --duration 900

# Quick run (5 minutes) - uses cached Google Trends if <7 days old
python3 master_scraper.py --duration 300

# Custom duration (30 seconds to 60 minutes)
python3 master_scraper.py --duration <seconds>
```

**Output:** `data/master_output/session_YYYYMMDD_HHMMSS/`

### Individual Modules

Run modules independently:

```bash
# Google Trends (creates 20+ visualizations)
cd scripts/google_trends
python3 googletrends.py

# News API
cd scripts/news_api
python3 news_main.py

# Reddit
cd scripts/reddit
python3 reddit_scraper_app.py

# Bluesky
cd scripts/bluesky
python3 main.py
```

---

## 📖 Module Details

### 1. Google Trends

**What it does:**
- Analyzes search trends for homelessness-related keywords
- Generates national and state-level time series
- Creates seasonal decomposition plots for 4 themes:
  - General Information and Definitions
  - Location-specific search
  - Policy, Organisations and Solutions
  - Statistics, Data, and Scope
- Produces interactive choropleth maps

**Output:**
- 8 data files (XLSX, CSV, PKL)
- 20 visualizations (PNG, HTML)
- Keywords extracted for use by other modules

**Caching:** Results cached for 7 days to avoid API rate limits

### 2. News API

**What it does:**
- Fetches articles from NewsAPI and NPR
- Classifies political leaning (LEFT/CENTER/RIGHT) using HuggingFace transformers
- Generates word clouds and timeline charts

**Output:**
- 2 data files (75+ articles)
- 4 visualizations
- Political classification: typically 50-70% LEFT, 20-40% RIGHT, <5% CENTER

### 3. Reddit

**What it does:**
- Scrapes 9 homelessness-related subreddits:
  - r/homeless, r/housing, r/eviction, r/affordablehousing
  - r/rent, r/shelter, r/housingcrisis, r/povertyfinance, r/urbancarliving
- Uses keywords from Google Trends for filtering
- Collects 150-200 posts with metadata

**Output:**
- CSV and JSON formats
- Title, selftext, author, score, num_comments, created_utc

### 4. Bluesky

**What it does:**
- Integrates with Bluesky social media platform
- Searches for homelessness-related posts
- Can generate visualizations if run independently

**Output:**
- Post data in JSONL format
- Metadata: author, engagement, timestamps

---

## 🔍 Key Features

### Intelligent Caching
- **Google Trends:** 7-day cache to avoid API rate limits
- Automatically reuses recent data when available
- Manual cache clearing: `rm -rf viz/google_trends/* scripts/google_trends/googletrends_*`

### Centralized Output
- All modules write to single session directory
- Timestamped sessions: `session_20251006_123042`
- Easy to find and analyze complete runs

### Political Analysis
- News articles classified as LEFT/CENTER/RIGHT
- Uses `cardiffnlp/twitter-roberta-base-sentiment-latest` transformer model
- Provides insights into media coverage bias

### Keyword Propagation
- Google Trends extracts homelessness keywords
- Keywords automatically used by Reddit and News modules
- Ensures consistent search terms across platforms

---

## 📊 Sample Statistics

From a typical comprehensive run:

| Metric | Value |
|--------|-------|
| Total Duration | ~15 minutes (fresh) / ~1 minute (cached) |
| Success Rate | 4/4 modules (100%) |
| Total Files | 36 files (3-4 MB) |
| Google Trends Visualizations | 20 charts & maps |
| News Articles | 75 articles |
| Reddit Posts | 150-200 posts |
| Keywords Extracted | 10-15 terms |

---

## 🛠️ Troubleshooting

### Issue: Missing Dependencies

```bash
# Error: No module named 'newsapi'
pip install newsapi-python

# Error: No module named 'praw'
pip install praw prawcore

# Error: No module named 'wordcloud'
pip install wordcloud

# Install all at once:
pip install -r requirements.txt
```

### Issue: Google Trends Timeout

**Symptom:** Google Trends running for 20+ minutes

**Solution:** This is normal for first run! Google Trends makes many API calls. Subsequent runs will use cached data (<1 second).

To force fresh data:
```bash
rm -rf viz/google_trends/* scripts/google_trends/googletrends_*
```

### Issue: News API Failing

**Symptom:** "No articles found" or API errors

**Solution:**
1. Check internet connection
2. Verify NEWS_API_KEY in `scripts/news_api/credentials.py`
3. NPR scraping works without API key

### Issue: Reddit Rate Limiting

**Symptom:** "Too many requests"

**Solution:**
- Reduce posts_per_subreddit in master_scraper.py
- Wait 5-10 minutes before retrying
- Add Reddit API credentials for higher limits

---

## 📝 Configuration

### Master Scraper Time Budget

Edit `master_scraper.py` line 47-52:

```python
self.time_budget = {
    'google_trends': int(self.total_duration * 0.15),  # 15%
    'news_api': int(self.total_duration * 0.30),       # 30%
    'reddit': int(self.total_duration * 0.25),         # 25%
    'bluesky': int(self.total_duration * 0.30)         # 30%
}
```

### Keywords & Subreddits

Customize in each module's script or use GUI interfaces:
- Google Trends: `scripts/google_trends/data python files/keyword_theme.xlsx`
- Reddit: `scripts/reddit/config.py`
- News API: `scripts/news_api/news_configs.py`

---

## 📚 Documentation

- **Master Scraper Results:** `MASTER_SCRAPER_RESULTS.md` - Detailed output breakdown
- **Lessons Learned:** `LESSONS_LEARNED.md` - Problems & solutions
- **Individual Modules:**
  - Google Trends: `scripts/google_trends/README-googletrends.md`
  - News API: `scripts/news_api/README.md`
  - Reddit: `scripts/reddit/README.md`
  - Bluesky: `scripts/bluesky/README.md`

---

## 🤝 Contributing

This is a research project for CMU DFP F25. For questions or issues:

1. Check documentation in each module's folder
2. Review `LESSONS_LEARNED.md` for common issues
3. Check master_log_*.json for detailed execution logs

---

## 📄 License

Carnegie Mellon University - DFP F25 Project

---

## 🎓 Project Structure

```
dfp_ngo_module/
├── master_scraper.py              # Main orchestrator (use this!)
├── requirements.txt               # All dependencies
├── README.md                      # This file
│
├── data/
│   └── master_output/            # All output goes here
│       └── session_*/            # Timestamped sessions
│
├── scripts/
│   ├── google_trends/            # Google Trends module
│   ├── news_api/                 # News API module
│   ├── reddit/                   # Reddit scraper
│   └── bluesky/                  # Bluesky integration
│
├── viz/
│   ├── google_trends/            # Google Trends visualizations (cached)
│   ├── news_api/                 # News visualizations
│   └── reddit/                   # Reddit visualizations
│
└── auth/                         # API credentials (gitignored)
```

---

## ⚡ Quick Reference

```bash
# Full comprehensive run
python3 master_scraper.py --duration 900

# Quick test (uses cache)
python3 master_scraper.py --duration 300

# Clear cache for fresh data
rm -rf viz/google_trends/* scripts/google_trends/googletrends_*

# Install dependencies
pip install -r requirements.txt

# View results
ls -lh data/master_output/session_*/

# Check logs
cat data/master_output/master_log_*.json
```

---

**Status:** ✅ All 4 modules working comprehensively as of October 6, 2025

**Last Updated:** October 6, 2025
