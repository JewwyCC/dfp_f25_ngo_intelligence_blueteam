# NGO Intelligence Platform - Homelessness Research

Multi-source data collection and analysis platform focused on **homelessness research** and housing crisis intelligence gathering.

**Project Focus**: Comprehensive homelessness data collection from social media, trends, and community discussions.

---

## 📊 Available Data Sources

### 1. [Bluesky](scripts/bluesky/) - ✅ OPERATIONAL

**Status:** Production-ready homelessness data collector

**Features:**
- **12 homelessness categories** with 100+ search query variations
- Dual collection: Real-time firehose + Historical search API
- Interactive GUI with visualization dashboard
- Sample dataset included (~1000 posts)
- Political polarization analysis

**Categories Tracked:**
- General Homelessness, Homeless Individuals, Unhoused Populations
- Street & Chronic Homelessness, Housing Insecurity
- Homeless Shelters, Encampments, Crisis Situations
- Homeless Veterans, Youth, and Families

**Quick Start:**
```bash
# Add your Bluesky credentials
cp auth/bluesky/config/auth_template.json auth/bluesky/config/auth.json

# Collect data
cd scripts/bluesky
python bluesky_social_justice_collector.py --method search --days-back 7 --max-posts 500

# Or use GUI
python gui.py
```

**Documentation:** [scripts/bluesky/README.md](scripts/bluesky/README.md)

---

### 2. [Reddit](RedditScraper/) - ✅ OPERATIONAL

**Status:** Fully working with homelessness configuration

**Features:**
- 9 homelessness-focused subreddits monitored
- 31 homelessness keywords tracked
- Interactive GUI interface
- Data collection, analysis, and visualization modules
- **Authentication already configured**

**Subreddits Monitored:**
- r/homeless, r/housing, r/eviction
- r/affordablehousing, r/rent, r/shelter
- r/housingcrisis, r/povertyfinance, r/urbancarliving

**Quick Start:**
```bash
cd RedditScraper
python gui.py
```

**Note:** Credentials are configured in `config.py`

---

### 3. [Google Trends](scripts/google_trends/) - ✅ READY

**Status:** Dependencies installed, needs keyword configuration

**Features:**
- Geographic visualization (national & state-level)
- Time series analysis
- Trend decomposition
- Comprehensive keyword tracking

**Quick Start:**
```bash
cd scripts/google_trends
# Configure homelessness keywords in googletrends.py
python googletrends.py
```

**Dependencies:** All installed via requirements.txt

---

## 🚀 Quick Start Guide

### Installation

1. **Clone and navigate:**
```bash
cd dfp_ngo_module
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up authentication:**
```bash
# Bluesky (required)
cp auth/bluesky/config/auth_template.json auth/bluesky/config/auth.json
# Edit auth.json with your Bluesky credentials

# Reddit (already configured in RedditScraper/config.py)
# Google Trends (no auth needed)
```

### Start Collecting Data

**Option 1: Use Reddit (Ready Now)**
```bash
cd RedditScraper
python gui.py
```

**Option 2: Use Bluesky (After auth setup)**
```bash
cd scripts/bluesky
python gui.py
```

**Option 3: Use Google Trends**
```bash
cd scripts/google_trends
python googletrends.py
```

---

## 📁 Project Structure

```
dfp_ngo_module/
├── scripts/
│   ├── bluesky/              ✅ Homelessness collector (12 categories)
│   │   ├── bluesky_social_justice_collector.py
│   │   ├── gui.py            # Interactive GUI
│   │   ├── gui_viz.py        # Visualization module
│   │   └── README.md         # Detailed documentation
│   │
│   ├── google_trends/        ✅ Trends analysis (needs config)
│   │   ├── googletrends.py
│   │   └── requirements-googletrends.txt
│   │
│   ├── reddit/               📝 Placeholder
│   └── news_api/             📝 Placeholder
│
├── RedditScraper/            ✅ Reddit collector (9 subreddits)
│   ├── config.py             # Has auth credentials
│   ├── data_collection.py
│   ├── analysis.py
│   ├── visualization.py
│   └── gui.py
│
├── auth/
│   └── bluesky/              # Bluesky authentication
│       ├── README.md
│       └── config/
│           └── auth_template.json
│
├── data/
│   └── bluesky/
│       └── sample/           # Sample dataset (~1000 posts)
│
├── viz/
│   └── bluesky/              # Visualization examples
│
├── requirements.txt          # All dependencies
├── FINAL_SCRAPER_STATUS.md   # Complete test report
└── README.md                 # This file
```

---

## 🎯 Homelessness Research Focus

All data sources are configured to collect comprehensive homelessness data:

### Bluesky Coverage
- 12 distinct categories
- 100+ search query variations
- Multiple perspectives (homeless, unhoused, housing insecure)
- All demographics (veterans, youth, families)

### Reddit Coverage
- 9 specialized subreddits
- 31 targeted keywords
- Community discussions and personal experiences
- Real-time monitoring

### Google Trends Coverage
- Geographic distribution analysis
- Temporal trend patterns
- Public interest metrics
- State-level comparisons

---

## 📊 Data Collection Capabilities

### Expected Output (24 hours)

| Source | Posts/Data | Coverage |
|--------|-----------|----------|
| **Bluesky** | 2,400-12,000 posts | 12 categories, real-time + historical |
| **Reddit** | 1,200-4,800 posts | 9 subreddits, community discussions |
| **Google Trends** | State-level trends | 50 states, temporal patterns |

**Total:** ~3,600-16,800 posts + trend data
**Storage:** ~50-100MB per day

---

## 🛠️ Available Tools

### Bluesky Tools
- `bluesky_social_justice_collector.py` - Main collector
- `gui.py` - Interactive GUI
- `gui_viz.py` - Visualization generator
- Sample data for testing

### Reddit Tools
- `data_collection.py` - Subreddit scraper
- `analysis.py` - Data analysis
- `visualization.py` - Chart generation
- `gui.py` - Interactive interface
- `cleaning.py` - Data cleaning
- `curation.py` - Data curation

### Google Trends Tools
- `googletrends.py` - Trend collector
- Geographic visualization
- Time series analysis
- Trend decomposition

---

## 📝 Documentation

- **[FINAL_SCRAPER_STATUS.md](FINAL_SCRAPER_STATUS.md)** - Complete scraper test report
- **[scripts/bluesky/README.md](scripts/bluesky/README.md)** - Bluesky detailed guide
- **[scripts/bluesky/GUI_README.md](scripts/bluesky/GUI_README.md)** - GUI documentation
- **[auth/bluesky/README.md](auth/bluesky/README.md)** - Authentication setup

---

## 🔒 Security Notes

### Bluesky
- ✅ Template-based authentication
- ✅ Credentials stored in gitignored auth.json
- ✅ Uses app passwords (not main credentials)

### Reddit
- ⚠️ Credentials currently in `RedditScraper/config.py`
- ⚠️ Working but not following best practices
- 📝 Recommendation: Move to environment variables

### Google Trends
- ✅ No authentication required
- ✅ Public API access

---

## 🚧 Development Status

| Component | Status | Ready |
|-----------|--------|-------|
| **Bluesky Collector** | ✅ Production | YES |
| **Reddit Collector** | ✅ Working | YES |
| **Google Trends** | ✅ Installed | YES* |
| **News API** | 📝 Placeholder | NO |

*Needs keyword configuration

---

## 🤝 Contributing

This project focuses on comprehensive homelessness research through multi-source data collection.

**Key Focus Areas:**
1. Homelessness and housing crisis
2. Social media discourse analysis
3. Geographic distribution patterns
4. Temporal trend analysis
5. Community discussions and experiences

---

## 📄 License

Part of the Data Focused Python course project at Carnegie Mellon University.

---

## 👥 Contact

For questions or contributions:
- Email: rutomo@andrew.cmu.edu
- GitHub: https://github.com/ecoflowtsel/dfp_f25_ngo_intelligence_blueteam

---

## 🎯 Quick Commands Reference

```bash
# Bluesky - Collect last 7 days
cd scripts/bluesky
python bluesky_social_justice_collector.py --method search --days-back 7 --max-posts 500

# Bluesky - Real-time collection (30 min)
python bluesky_social_justice_collector.py --method firehose --duration 1800

# Bluesky - GUI
python gui.py

# Reddit - GUI
cd RedditScraper
python gui.py

# Reddit - Quick test
python -c "from config import RedditAuth; import praw; r = praw.Reddit(client_id=RedditAuth.client_id, client_secret=RedditAuth.client_secret, user_agent=RedditAuth.user_agent); print([p.title for p in r.subreddit('homeless').hot(limit=5)])"

# Google Trends - Test
cd scripts/google_trends
python3 -c "from pytrends.request import TrendReq; pt = TrendReq(); pt.build_payload(['homelessness'], timeframe='today 1-m'); print(pt.interest_over_time())"
```

---

**Status:** All three scrapers operational and ready for homelessness research! 🏠
