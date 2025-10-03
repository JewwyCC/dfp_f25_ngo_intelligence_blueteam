# NGO Intelligence Platform

Multi-source data collection and analysis platform for NGO intelligence gathering on homelessness and social justice issues.

**Project**: Data Focused Python (DFP) Fall 2025 - Carnegie Mellon University Heinz College
**Focus**: Homelessness & Housing Crisis Intelligence

---

## 🎯 Master Scraper - Sequential Data Collection

**NEW**: Automated sequential data collection from all sources with keyword propagation and political bias classification.

### Quick Start

```bash
# Install all dependencies
pip install -r requirements.txt

# Configure credentials (see Authentication section below)

# Run fast test (completes in ~25 seconds)
python3 master_scraper_fast.py

# Run full collection (can take 30-60 minutes)
python3 master_scraper.py
```

### How It Works

The master scraper executes modules **sequentially** in this order:

1. **Google Trends** → Extracts keywords and zipcodes from trend data
2. **News API** → Searches news articles using Google Trends keywords + Political bias classification
3. **Reddit** → Collects posts from subreddits using keywords
4. **Bluesky** → Searches social media posts using keywords

**Features:**
- ✅ Sequential execution with real-time progress output
- ✅ Keyword propagation from Google Trends to all modules
- ✅ Political bias classification (HuggingFace) with 10-second timeout
- ✅ Completion signals for each module
- ✅ Summary report generation (JSON)
- ✅ Colored terminal output
- ✅ Error handling and graceful failure recovery

**Output:**
```
data/
├── google_trends/        # Trend analysis data
├── news_api/
│   ├── news_articles_fast.json      # Collected articles
│   └── classified_fast.json         # Political bias classification
├── reddit/               # Reddit posts (CSV)
└── bluesky/              # Bluesky posts (JSONL/CSV)
```

---

## 📊 Data Sources

### 1. Google Trends ✅
Keyword extraction and trend analysis
- **Status**: Operational
- **Function**: Provides keywords for downstream modules
- **Output**: Keywords, zipcodes, trend data

### 2. News API ✅
News article collection with political bias classification
- **Status**: Operational with HuggingFace classifier
- **Features**:
  - Collects articles from 40+ US news sources
  - Political bias classification (Left/Center/Right)
  - 10-second timeout for classification
- **Scripts**: [scripts/news_api/](scripts/news_api/)
  - `NewsAPI_Scrape.py` - Article collection
  - `HF_Classifier.py` - Political bias classifier
  - `Viz.py` - Visualization tools

### 3. Reddit ✅
Subreddit monitoring for homelessness discussions
- **Status**: Operational
- **Subreddits**: r/homeless, r/housing, r/eviction, r/affordablehousing, r/rent, r/shelter, r/housingcrisis, r/povertyfinance, r/urbancarliving
- **Keywords**: 31 homelessness-related terms
- **Scripts**: [scripts/reddit/](scripts/reddit/)
  - `data_collection.py` - Post collection
  - `analysis.py` - Data analysis
  - `visualization.py` - Charts and graphs
  - `gui.py` - Interactive interface

### 4. Bluesky ✅
Real-time social media monitoring
- **Status**: Operational with 156K+ posts collected
- **Features**:
  - Dual collection: Firehose (real-time) + Search API (historical)
  - 155+ homelessness keywords
  - Geographic analysis and sentiment tracking
- **Scripts**: [scripts/bluesky/](scripts/bluesky/)
  - `bluesky_social_justice_collector.py` - Main collector
  - `demo.py` - Interactive demo
  - `main.py` - Quick collection script
- **Data**: [data/bluesky/](data/bluesky/) - 156K+ posts

---

## 🚀 Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd dfp_ngo_module
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `atproto` - Bluesky API client
- `praw` - Reddit API wrapper
- `newsapi-python` - News API client
- `pytrends` - Google Trends API
- `pandas` - Data manipulation
- `transformers` - HuggingFace (optional for local classification)

### 3. Authentication Setup

#### Bluesky
```bash
# Create auth file
cat > auth/bluesky/config/auth.json << EOF
{
  "bluesky": {
    "username": "your_email@example.com",
    "password": "your_app_password"
  }
}
EOF
```

#### News API
```bash
# Edit credentials file (NEVER COMMIT THIS)
# File is gitignored
cat > scripts/news_api/credentials.py << EOF
NEWSAPI_KEY = 'your_newsapi_key'
HUGGINGFACE_TOKEN = 'your_huggingface_token'
EOF
```

#### Reddit
Already configured in `scripts/reddit/config.py`

#### Google Trends
No authentication required

---

## 📖 Usage

### Master Scraper (Recommended)

**Fast Test Mode** (~25 seconds):
```bash
python3 master_scraper_fast.py
```
- Extracts 15 keywords from Google Trends
- Collects 10 news articles with political classification
- Searches 2 subreddits
- Collects 50 Bluesky posts (1 day history)

**Full Collection Mode** (30-60 minutes):
```bash
python3 master_scraper.py
```
- Full Google Trends analysis
- 100+ news articles with classification
- 1000+ Reddit posts
- 1000+ Bluesky posts (30 days history)

### Individual Modules

#### Google Trends
```bash
cd scripts/google_trends
python3 googletrends.py
```

#### News API
```bash
cd scripts/news_api
python3 NewsAPI_Scrape.py
```

#### Reddit
```bash
cd scripts/reddit
python3 gui.py  # Interactive GUI
# OR
python3 data_collection.py  # Command line
```

#### Bluesky
```bash
cd scripts/bluesky
python3 demo.py  # Interactive demo
# OR
python3 bluesky_social_justice_collector.py --method search --days-back 7 --max-posts 500
```

---

## 📁 Project Structure

```
dfp_ngo_module/
├── master_scraper.py              # Full production scraper
├── master_scraper_fast.py         # Fast test scraper (~25s)
├── requirements.txt               # All dependencies
├── README.md                      # This file
│
├── scripts/                       # Data collection scripts
│   ├── bluesky/                   # Bluesky module
│   ├── news_api/                  # News API + Classifier
│   ├── reddit/                    # Reddit module
│   └── google_trends/             # Google Trends module
│
├── data/                          # Collected data
│   ├── bluesky/                   # 156K+ posts
│   ├── news_api/                  # News articles + classifications
│   ├── reddit/                    # Reddit posts
│   └── google_trends/             # Trend data
│
├── auth/                          # Authentication (gitignored)
│   ├── bluesky/config/auth.json
│   └── news_api/credentials.py
│
└── viz/                           # Visualizations
    ├── bluesky/                   # EDA reports
    ├── news_api/                  # News visualizations
    └── reddit/                    # Reddit charts
```

---

## 🔒 Security

**Important**: Never commit credentials to git!

Files automatically gitignored:
- `auth/*/config/auth.json`
- `scripts/news_api/credentials.py`
- `**/credentials.py`
- `*.json` (except requirements.json)

---

## 📊 Data Collection Capabilities

### Master Scraper Fast Mode (~25 seconds)
- Google Trends: 15 keywords extracted
- News API: 10 articles + 1 classified
- Reddit: 20 posts from 2 subreddits
- Bluesky: 50 posts (1 day)

### Master Scraper Full Mode (~30-60 minutes)
- Google Trends: Full analysis (national + state-level)
- News API: 100 articles + batch classification
- Reddit: 1000 posts from 9 subreddits
- Bluesky: 1000 posts (30 days)

---

## 🧪 Testing

Run component test:
```bash
python3 master_scraper_test.py
```

This verifies:
- ✅ All scripts exist
- ✅ Data directories created
- ✅ Credentials configured
- ✅ Authentication working

---

## 📈 Political Bias Classification

The News API module includes political bias classification using HuggingFace's `politicalBiasBERT` model.

**Features:**
- Classifies articles as: LEFT, CENTER-LEFT, CENTER, CENTER-RIGHT, RIGHT
- 10-second timeout to prevent blocking
- Confidence scores for each classification
- Automatic fallback on timeout/error

**Output Example:**
```json
[
  {
    "title": "Article Title Here",
    "label": "LEFT",
    "confidence": 0.74
  }
]
```

---

## 🤝 Contributing

**Team Project**: DFP F25 NGO Intelligence Blue Team

Each team member maintains their own module:
- Module directories: `scripts/{source}/`
- Data directories: `data/{source}/`
- Visualizations: `viz/{source}/`

**Development Workflow:**
1. Work in your module directory
2. Test independently
3. Ensure compatibility with master scraper
4. Update README with your changes
5. Submit PR

---

## 📝 Output Files

### Master Scraper Report
```json
{
  "start_time": "2025-10-03T10:00:00",
  "end_time": "2025-10-03T10:25:00",
  "duration_seconds": 1500,
  "keywords_used": ["homelessness", "housing crisis", ...],
  "results": {
    "google_trends": {"status": "success", "duration": 5.0},
    "news_api": {"status": "success", "duration": 15.0},
    "reddit": {"status": "success", "duration": 10.0},
    "bluesky": {"status": "success", "duration": 8.0}
  }
}
```

Saved as: `collection_report_YYYYMMDD_HHMMSS.json`

---

## 🎓 Academic Information

- **Course**: Data Focused Python (Fall 2025)
- **Institution**: Carnegie Mellon University - Heinz College
- **Team**: NGO Intelligence Blue Team
- **Focus**: Homelessness & Social Justice Intelligence
- **Project Type**: Graduate Student Team Project

---

## 📄 License

Carnegie Mellon University - Data Focused Python Course Project

---

## 📧 Support

For issues or questions:
- Create an issue in the repository
- Contact team members
- Refer to individual module READMEs in `scripts/{module}/`

---

**Last Updated**: October 3, 2025
**Total Data Collected**: 156K+ posts (Bluesky) + News articles + Reddit posts
**Master Scraper Status**: ✅ Operational
