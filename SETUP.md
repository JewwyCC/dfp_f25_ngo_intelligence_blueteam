# 🔧 Setup Instructions
## DFP F25 Social Media Blue Team - Bluesky Hybrid Collector

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/dfp_f25_socmed_blueteam.git
   cd dfp_f25_socmed_blueteam
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create credentials file:**
   ```bash
   # Create data/config/auth.json with your Bluesky credentials
   {
     "bluesky": {
       "username": "your.email@example.com",
       "password": "your_bluesky_password"
     }
   }
   ```

## 🚀 Quick Start

```bash
# Test search collection
python bluesky_social_justice_collector.py --method search --days-back 1 --max-posts 10

# Real-time firehose collection
python bluesky_social_justice_collector.py --method firehose --duration 600

# Hybrid collection with total time parameter (recommended)
python bluesky_social_justice_collector.py --method both --total-time 1200 --days-back 7

# Hybrid collection with separate time controls
python bluesky_social_justice_collector.py --method both --duration 300 --search-timeout 900 --days-back 7
```

## 📋 Collection Methods

**Firehose (Real-time):**
- Connects to live Bluesky stream
- Collects posts as they happen
- Use `--duration` for collection time

**Search API (Historical):**
- Uses native search with pagination
- Systematic historical data collection
- Use `--days-back` or `--start-date`/`--end-date`

**Both (Hybrid):**
- Historical data first, then real-time
- Complete coverage approach
- Use `--total-time` for automatic 75%/25% split
- Or use separate `--duration` and `--search-timeout` for manual control

## 📊 Data Output

- **Session data**: `data/sessions/[session_name]/`
- **Alltime data**: `data/alltime/`
- **Both formats**: JSONL and CSV

## 🔐 Security

- Credentials file (`data/config/auth.json`) is in `.gitignore`
- Never commit authentication information
- Data files are also gitignored for privacy
