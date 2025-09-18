# 🦋 DFP F25 Social Media Blue Team
## Bluesky Social Justice Data Collector - Hybrid System

**Comprehensive data collection with dual methods: real-time firehose + historical search API with deep pagination.**

## ⚡ Quick Start

### 🔧 Installation
```bash
pip install -r requirements.txt
```

### 🔐 Setup Credentials
Create `data/config/auth.json`:
```json
{
  "bluesky": {
    "username": "your.email@example.com", 
    "password": "your_password"
  }
}
```

### 🚀 Collection Methods

**Three collection approaches:**
- `firehose` - Real-time stream collection
- `search` - Historical data with pagination
- `both` - Historical first, then real-time (recommended)

**Parameters:**
- `--method {firehose,search,both}` - Collection method
- `--duration SECONDS` - Firehose duration in seconds
- `--days-back DAYS` - Historical search days back
- `--max-posts NUM` - Max posts per keyword for search
- `--session_name NAME` - Custom session name

```bash
# Real-time collection (firehose)
python bluesky_social_justice_collector.py --method firehose --duration 1800

# Historical collection (search API with pagination)
python bluesky_social_justice_collector.py --method search --days-back 30 --max-posts 1000

# Hybrid collection (recommended - historical + real-time)
python bluesky_social_justice_collector.py --method both --duration 600 --days-back 7

# Quick test
python bluesky_social_justice_collector.py --method search --days-back 1 --max-posts 10
```

### 🔍 Search API Features
- **Deep pagination** with cursor navigation
- **Date range filtering** by post creation time
- **Enhanced queries** (exact phrases, hashtags)
- **Rate limiting** and error handling
- **Resumable collection** with cursor persistence

## 🎯 What It Collects

**Social Justice Topics:**
- Food insecurity
- Housing crisis  
- Homelessness
- Unemployment
- Gender inequality

**Rich Author Data:**
- Real follower counts 👥
- Verification status ✅
- Account age and activity
- Influence scores
- Profile descriptions

**Content Analysis:**
- Word/character counts
- Hashtags and mentions
- Media detection
- Emotion scoring
- URL extraction

## 📁 Data Organization

```
data/
├── sessions/
│   ├── session_20250918_065442/    # Per-session data
│   │   ├── housing_posts.jsonl
│   │   ├── homeless_posts.jsonl
│   │   ├── unemployment_posts.jsonl
│   │   └── session_summary.json
│   └── session_20250918_120000/    # Next session
│
└── alltime/                        # Cumulative datasets  
    ├── housing_alltime.jsonl       # All housing posts ever
    ├── housing_alltime.csv
    ├── homeless_alltime.jsonl      # All homeless posts ever  
    ├── homeless_alltime.csv
    └── ...
```

## 🔧 Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create credentials file:**
   ```json
   // data/config/auth.json
   {
     "bluesky": {
       "username": "your.email@example.com",
       "password": "your_password"
     }
   }
   ```

3. **Run collection:**
   ```bash
   # Hybrid collection (recommended)
   python bluesky_social_justice_collector.py --method both --duration 1800 --days-back 7
   ```

## 📊 Performance

**Firehose Collection:**
- Processing rate: ~20-25 posts/second
- Relevance rate: ~0.1-1% (high-quality filtering)
- Real-time monitoring of current conversations

**Search API Collection:**
- Collection rate: ~50-100 posts/minute
- Historical data with systematic coverage
- Enhanced query precision reduces noise

**Author Profiles:**
- Real follower counts with authentication
- Influence scoring and verification status
- Profile caching for efficiency

## 🎯 Perfect For

- **Academic research** on social movements
- **Real-time monitoring** of social issues
- **Author influence analysis** using follower metrics
- **Trend detection** with fresh authenticated data
- **Dataset building** for ML/analysis

## 📈 Data Quality

### Session Data
- **Fresh posts** from real-time firehose
- **Author influence metrics** (follower counts, verification)
- **Content analysis** (hashtags, media, emotions)
- **Session organization** for temporal analysis

### Alltime Data  
- **Cumulative datasets** across all sessions
- **Automatic deduplication** (never collect same post twice)
- **Historical growth** tracking
- **Ready for analysis** in CSV and JSONL formats

## 🔍 Example Data

```json
{
  "text": "Housing crisis getting worse, can't afford rent",
  "author_handle": "activist.bsky.social",
  "author_followers_count": 2408,
  "author_influence_score": 34.2,
  "keyword": "housing",
  "session_name": "session_20250918_065442",
  "emotion_score": 2,
  "has_media": true
}
```

---

**Hybrid system for comprehensive social justice data collection with full author influence metrics.**