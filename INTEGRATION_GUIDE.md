# NGO Platform - Integration & Testing Guide

**Last Updated:** October 6, 2025  
**Status:** ✅ All 4 modules working comprehensively

---

## 🎯 Quick Integration Test

Run this single command to verify everything works:

```bash
python3 master_scraper.py --duration 300
```

**Expected:** ~1 minute runtime (uses cached Google Trends), 20+ files generated

---

## ✅ Verification Checklist

After running the master scraper, verify:

### 1. Check Session Created
```bash
ls -lh data/master_output/session_*/
```
**Expected:** 1 new directory with timestamp

### 2. Verify File Count
```bash
ls -1 data/master_output/session_LATEST/ | wc -l
```
**Expected:** 20-36 files depending on Google Trends cache

### 3. Verify Each Module

#### Google Trends (10-20 files)
```bash
ls -1 data/master_output/session_LATEST/googletrends_*.xlsx
ls -1 data/master_output/session_LATEST/viz_*.png | head -5
```
**Expected:** 
- 2 Excel files (national + state)
- 10+ visualization files

#### News API (6 files)
```bash
ls -1 data/master_output/session_LATEST/{combined_articles.json,classified.csv,news_*.png}
```
**Expected:**
- combined_articles.json (~80KB, 75 articles)
- classified.csv (political classification)
- 4 PNG visualizations

#### Reddit (2 files)
```bash
wc -l data/master_output/session_LATEST/reddit_posts.csv
```
**Expected:** 150-200 posts in CSV format

#### Bluesky (Script integration)
```bash
grep "Bluesky" data/master_output/master_log_*.json
```
**Expected:** "status": "success"

---

## 🔧 Dependency Verification

Test each module's dependencies:

```bash
# Core dependencies
python3 -c "import pandas, numpy, requests; print('✓ Core OK')"

# Google Trends
python3 -c "import pytrends, geopandas, folium; print('✓ Google Trends OK')"

# News API
python3 -c "import newsapi, bs4, wordcloud, transformers; print('✓ News API OK')"

# Reddit
python3 -c "import praw, textblob; print('✓ Reddit OK')"

# Bluesky
python3 -c "import atproto; print('✓ Bluesky OK')"
```

---

## 📊 Expected Output Structure

```
data/master_output/session_20251006_124016/
├── googletrends_national_20251006_125503.xlsx      # National trends
├── googletrends_state_20251006_125503.xlsx         # State trends
├── googletrends_help_20251006_125506.csv           # Help queries
├── googletrends_mapdata_20251006_125506.pkl        # Geographic data
│
├── viz_national_timeseries_*.png                   # Time series
├── viz_CA_timeseries_*.png                         # CA state trends
├── viz_theme_comp_*.png                            # Theme comparison
├── viz_national_seasonal_*.png (4)                 # Seasonal patterns
├── viz_state_seasonal_*.png (2+)                   # State seasonal
├── viz_choropleth_*.html                           # Interactive maps
│
├── combined_articles.json                          # 75 news articles
├── classified.csv                                  # Political labels
├── news_wordcloud_*.png                            # Word cloud
├── news_outlet_counts_*.png                        # Outlet chart
├── news_political_pie_*.png                        # Political pie
├── news_political_timeline_*.png                   # Timeline
│
├── reddit_posts.csv                                # Reddit data
└── reddit_posts.json                               # Same in JSON
```

---

## 🐛 Troubleshooting

### Issue: "No module named X"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Google Trends taking 15+ minutes

**Explanation:** This is NORMAL for first run. Subsequent runs use 7-day cache (<1 second).

To check cache status:
```bash
ls -lt viz/google_trends/
```

To force fresh data (if needed):
```bash
rm -rf viz/google_trends/* scripts/google_trends/googletrends_*
```

### Issue: News API returns few articles

**Explanation:** NewsAPI free tier has limits. The scraper also fetches from NPR to supplement.

**Typical output:** 50-75 articles total

### Issue: Reddit rate limiting

**Solution:** 
- Reduce duration (fewer API calls)
- Wait 5-10 minutes between runs
- Normal output: 150-200 posts is expected

### Issue: Bluesky authentication

**Explanation:** Bluesky module works without authentication for public data. For authenticated access, configure:
```bash
# Edit auth/bluesky/config/auth.json
{
  "username": "your.handle",
  "password": "your-app-password"
}
```

---

## ⚡ Performance Benchmarks

Based on comprehensive testing:

| Scenario | Duration | Files Generated | Notes |
|----------|----------|-----------------|-------|
| **Fresh Run** | ~15 min | 20-36 files | First run or cache expired |
| **Cached Run** | ~1 min | 20-22 files | Google Trends cached (<7 days) |
| **Quick Test** | 5 min | 20-22 files | duration=300 |

### Module Timing (Fresh)
- Google Trends: 800-900 seconds (API calls)
- News API: 20-30 seconds
- Reddit: 25-30 seconds  
- Bluesky: <1 second

### Module Timing (Cached)
- Google Trends: <1 second (reuses data)
- News API: 20-30 seconds
- Reddit: 25-30 seconds
- Bluesky: <1 second

---

## 📝 Configuration Options

### Time Budget Allocation

Edit `master_scraper.py` lines 47-52:

```python
self.time_budget = {
    'google_trends': int(self.total_duration * 0.15),  # 15%
    'news_api': int(self.total_duration * 0.30),       # 30%
    'reddit': int(self.total_duration * 0.25),         # 25%
    'bluesky': int(self.total_duration * 0.30)         # 30%
}
```

### Keyword Customization

**Google Trends:**
- Edit: `scripts/google_trends/data python files/keyword_theme.xlsx`
- Add/remove themes and keywords

**Reddit:**
- Edit: `master_scraper.py` line 570 (subreddits list)
- Edit: `master_scraper.py` line 600 (posts_per_subreddit)

**News API:**
- Edit: `scripts/news_api/news_configs.py`
- Modify search queries and sources

### Caching Behavior

**Google Trends Cache Duration:**
- Edit `master_scraper.py` line 141
- Current: 7 days
- Change: `seven_days_ago = time_module.time() - (N * 24 * 3600)` where N = days

---

## 🧪 Testing Individual Modules

Test each module independently before running master scraper:

### Test Google Trends
```bash
cd scripts/google_trends
python3 googletrends.py
# Check: viz_dir should have 10-20 PNG/HTML files
```

### Test News API
```bash
cd scripts/news_api
python3 news_main.py
# Check: Should print "Collected X articles"
```

### Test Reddit
```bash
cd scripts/reddit
python3 reddit_scraper_app.py
# Check: Should show progress bar and collect posts
```

### Test Bluesky
```bash
cd scripts/bluesky
python3 main.py
# Check: Should create session directory with posts
```

---

## 📦 Deployment Checklist

Before deploying to new environment:

- [ ] Python 3.8+ installed
- [ ] Git repository cloned
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API keys configured (optional - works without)
- [ ] Test run completed (`python3 master_scraper.py --duration 300`)
- [ ] Output verified (20+ files generated)
- [ ] Logs reviewed (`data/master_output/master_log_*.json`)

---

## 🔒 API Keys & Credentials

### Required (None!)
All modules work without API keys for public data.

### Optional (Improved Performance)

**News API:**
```bash
# File: scripts/news_api/credentials.py
NEWS_API_KEY = "your_key_here"  # Get from https://newsapi.org
```

**Reddit:**
```bash
# File: scripts/reddit/config.py
client_id = "your_client_id"
client_secret = "your_secret"
user_agent = "your_app_name"
```

**Bluesky:**
```bash
# File: auth/bluesky/config/auth.json
{
  "username": "your.handle.bsky.social",
  "password": "your-app-password"
}
```

---

## 📊 Success Metrics

A successful run should show:

```
Success Rate: 4/4 (100%)  # or 3/4 (75%) if one module has issues
Total Files: 20-36 files
Total Duration: ~1-15 minutes
```

**Module Success:**
- ✅ Google Trends: Keywords extracted, visualizations created
- ✅ News API: 50+ articles collected, 4 visualizations
- ✅ Reddit: 150+ posts from 9 subreddits
- ✅ Bluesky: Script completed successfully

---

## 🎓 Understanding Output

### Master Log Structure
```json
{
  "session_info": {
    "start_time": "2025-10-06T12:40:16",
    "duration_budget": 600,
    "timestamp": "20251006_124016"
  },
  "results": {
    "google_trends": {"status": "success", "keywords_extracted": 11},
    "news_api": {"status": "success", "articles": 75},
    "reddit": {"status": "success", "posts": 169},
    "bluesky": {"status": "success"}
  }
}
```

### File Naming Convention
- `googletrends_national_YYYYMMDD_HHMMSS.xlsx` - National trends data
- `viz_national_timeseries_YYYYMMDD_HHMMSS.png` - Visualization
- `news_wordcloud_YYYYMMDD_HHMMSS.png` - News visualization
- `reddit_posts.csv` - Reddit data (no timestamp in name)

---

## 🚀 Next Steps After Integration

1. **Run First Comprehensive Test**
   ```bash
   python3 master_scraper.py --duration 900
   ```

2. **Review Generated Files**
   ```bash
   ls -lh data/master_output/session_*/
   ```

3. **Check Visualizations**
   - Open PNG files to verify charts
   - Open HTML files in browser for interactive maps

4. **Review Master Log**
   ```bash
   cat data/master_output/master_log_*.json
   ```

5. **Set Up Regular Runs** (if needed)
   ```bash
   # Add to crontab for weekly runs
   0 2 * * 0 cd /path/to/dfp_ngo_module && python3 master_scraper.py --duration 900
   ```

---

## ✅ Final Verification

Run these commands to confirm everything is working:

```bash
# 1. Test dependencies
pip list | grep -E "pandas|numpy|pytrends|newsapi|praw|atproto"

# 2. Run quick test
python3 master_scraper.py --duration 300

# 3. Check output
ls -lh data/master_output/session_*/

# 4. Verify file counts
find data/master_output/session_* -type f | wc -l

# 5. Check master log
tail -50 data/master_output/master_log_*.json
```

**Expected Result:** All commands succeed, 20+ files generated

---

**Status:** ✅ Integration guide complete and tested  
**Last Test Run:** October 6, 2025  
**Success Rate:** 4/4 modules (100%)

For issues or questions, refer to:
- `README.md` - General usage
- `LESSONS_LEARNED.md` - Common problems and solutions
- `MASTER_SCRAPER_RESULTS.md` - Detailed output breakdown
