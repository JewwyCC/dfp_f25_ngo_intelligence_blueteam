# 🦋 DFP F25 Social Media Blue Team
## Bluesky Social Justice Data Collector

**Clean, minimal system for collecting social justice data from Bluesky with rich author influence metrics.**

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

### 🚀 Run Collection

**Parameters:**
- `--duration SECONDS` - Collection duration in seconds
- `--session_name NAME` - Custom session name (optional)

**Collection automatically:**
- ✅ Saves every 2 minutes (120 seconds)
- ✅ Updates alltime files with each batch
- ✅ Appends new posts (never loses data)
- ✅ Fetches real author follower counts

```bash
# Quick test (30 seconds = 0.5 minutes)
python bluesky_social_justice_collector.py --duration 30

# Short collection (600 seconds = 10 minutes) 
python bluesky_social_justice_collector.py --duration 600

# Medium collection (1200 seconds = 20 minutes)
python bluesky_social_justice_collector.py --duration 1200

# Long collection (1800 seconds = 30 minutes)
python bluesky_social_justice_collector.py --duration 1800

# Extended collection (3600 seconds = 60 minutes)
python bluesky_social_justice_collector.py --duration 3600

# Custom session name
python bluesky_social_justice_collector.py --duration 900 --session_name "evening_collection"
```

### ⏱️ Batching Behavior
- **Every 2 minutes (120 seconds)**: Saves batch + updates alltime files
- **Real-time progress**: Shows collection stats every minute
- **Automatic append**: New posts added to existing alltime datasets
- **No data loss**: All previous data preserved across sessions

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
   python bluesky_social_justice_collector.py --duration 1800
   ```

## 📊 Expected Performance

- **Processing Rate**: ~20-25 posts/second
- **Relevance Rate**: ~0.1-1% (high-quality filtering)
- **Author Profiles**: Real follower counts with authentication
- **Daily Yield**: 50-500 relevant posts (depends on activity)
- **Resource Usage**: <200MB RAM, <5% CPU

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

## 🚀 Currently Running

**30-minute collection in progress...**
- Started: 06:54 AM
- Expected completion: 07:24 AM  
- Process ID: 29203
- Status: Collecting social justice data with author metrics

---

**🎯 Building rich social justice datasets with real influence metrics!**