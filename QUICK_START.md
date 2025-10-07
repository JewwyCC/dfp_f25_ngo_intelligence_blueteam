# 🚀 Quick Start Guide - NGO Intelligence Platform

## For First-Time Setup

### Step 1: Install Everything (5-10 minutes)

**macOS/Linux:**
```bash
./install.sh
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python verify_installation.py
```

That's it! The script handles everything automatically.

---

## Verify Installation

```bash
python verify_installation.py
```

You should see:
```
✅ All dependencies installed successfully!
Total: 25/25 modules installed
```

---

## Running the Platform

### 1️⃣ Collect Data (10 minutes)

```bash
python master_scraper_data.py --duration 600
```

This collects data from:
- ✅ Google Trends (homelessness searches)
- ✅ News API (75+ articles)
- ✅ Reddit (600+ posts)
- ✅ Bluesky (social media posts)

**Output:** `data/master_output/session_YYYYMMDD_HHMMSS/raw_data/`

### 2️⃣ Generate Visualizations (30 seconds)

```bash
python master_scraper_viz.py --session session_YYYYMMDD_HHMMSS
```

Replace `session_YYYYMMDD_HHMMSS` with your actual session ID from step 1.

**Output:** `data/master_output/session_YYYYMMDD_HHMMSS/artifacts/` (112 visualizations!)

### 3️⃣ View Dashboard (Optional)

```bash
streamlit run ngo_dashboard.py
```

Opens in your browser at http://localhost:8501

---

## Common Issues & Fixes

### ❌ "No module named 'XXX'"

**Fix:**
```bash
pip install -r requirements.txt
```

### ❌ "scipy not found" or similar

**Fix:** Install the missing scipy:
```bash
pip install scipy
```

### ❌ PyTorch/Transformers installation fails

**Fix (Apple Silicon):**
```bash
pip install --upgrade torch torchvision torchaudio
```

**Fix (Slow connection):**
```bash
pip install --no-cache-dir torch transformers
```

### ❌ geopandas installation fails

**Fix (Linux):**
```bash
sudo apt-get install gdal-bin libgdal-dev
pip install geopandas --no-build-isolation
```

**Fix (macOS/Windows):**
```bash
conda install geopandas  # If you have conda
```

### ❌ Permission denied on install.sh

**Fix:**
```bash
chmod +x install.sh
./install.sh
```

---

## What You Need Before Running

### 1. API Credentials (Already configured for you!)

- ✅ **Bluesky:** `auth/bluesky/config/auth.json`
- ✅ **Reddit:** `scripts/reddit/config.py` (RedditAuth class)
- ✅ **News API:** `scripts/news_api/credentials.py` (NEWSAPI_KEY)

### 2. Python 3.8+ Installed

Check version:
```bash
python3 --version  # Should show 3.8 or higher
```

---

## File Structure After Running

```
dfp_ngo_module/
├── data/master_output/
│   └── session_20251006_232447/
│       ├── raw_data/           # 13 data files (~430 KB)
│       │   ├── google_trends_*.xlsx
│       │   ├── news_*.json, *.csv
│       │   ├── reddit_*.csv, *.json
│       │   └── bluesky_*.csv, *.jsonl
│       ├── artifacts/          # 112 visualizations (~27 MB)
│       │   ├── google_trends_*.png, *.html
│       │   ├── news_*.png
│       │   ├── reddit_*.png
│       │   └── bluesky_*.png
│       └── SESSION_REPORT.md   # Detailed analysis report
├── requirements.txt            # All dependencies
├── install.sh                  # Automated installer
├── verify_installation.py      # Check what's installed
└── INSTALLATION.md             # Detailed instructions
```

---

## One-Liner Cheat Sheet

```bash
# Full pipeline (fresh data + viz)
python master_scraper_data.py --duration 600 && \
python master_scraper_viz.py --session $(ls -t data/master_output/ | grep session | head -1)

# Verify everything works
python verify_installation.py

# Emergency reinstall
rm -rf venv && ./install.sh

# View latest session report
cat data/master_output/$(ls -t data/master_output/ | grep session | head -1)/SESSION_REPORT.md
```

---

## Time Estimates

| Task | Time | Disk Space |
|------|------|------------|
| Installation | 5-10 min | ~3 GB |
| Data collection | 6-10 min | ~500 KB |
| Visualization | 20-30 sec | ~30 MB |
| Dashboard loading | 5 sec | - |

---

## Getting Help

1. **Check installation:**
   ```bash
   python verify_installation.py
   ```

2. **Read detailed guide:**
   ```bash
   cat INSTALLATION.md
   ```

3. **Check Python version:**
   ```bash
   python3 --version  # Must be 3.8+
   ```

4. **Fresh start:**
   ```bash
   rm -rf venv
   ./install.sh
   ```

---

## What's Included

### ✅ Installed (25 packages)
- Core: pandas, numpy, scipy, requests
- Bluesky: atproto
- Reddit: praw, textblob
- News: newsapi-python, beautifulsoup4, transformers, torch
- Google Trends: pytrends, openpyxl, folium, geopandas, statsmodels
- Visualization: matplotlib, seaborn, plotly, wordcloud
- Dashboard: streamlit, flask

### ✅ Not Needed to Install (Standard Library)
- json, os, sys, subprocess, pathlib
- datetime, time, logging, re
- collections, typing, argparse

---

**That's it! You're ready to collect and analyze homelessness data! 🎉**

