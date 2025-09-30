# NGO Intelligence Platform

Multi-source data collection and analysis platform for NGO intelligence gathering on homelessness and social justice issues.

**Current Focus**: Bluesky social media monitoring for homelessness discussions (156K+ posts collected)

**Supported Data Sources**: Bluesky (active), Google Trends, News API, Reddit (ready for implementation)

## 📊 Data Sources

### [Bluesky](scripts/bluesky/) - Active ✅
Real-time monitoring and analysis of homelessness discussions on Bluesky social network.
- **Status**: Fully implemented with 156,184 posts collected
- **Scripts**: [scripts/bluesky/](scripts/bluesky/) - Collection, demo, and analysis tools
- **Data**: [data/bluesky/](data/bluesky/) - 156K+ deduplicated posts
- **Auth**: [auth/bluesky/config/](auth/bluesky/config/) - Secure credential storage
- **Visualizations**: [viz/bluesky/](viz/bluesky/) - Interactive EDA reports

### Google Trends - Coming Soon 🚧
*Awaiting implementation by team members*
- **Scripts**: [scripts/google_trends/](scripts/google_trends/)
- **Data**: [data/google_trends/](data/google_trends/)
- **Auth**: [auth/google_trends/](auth/google_trends/)
- **Visualizations**: [viz/google_trends/](viz/google_trends/)

### News API - Coming Soon 🚧
*Awaiting implementation by team members*
- **Scripts**: [scripts/news_api/](scripts/news_api/)
- **Data**: [data/news_api/](data/news_api/)
- **Auth**: [auth/news_api/](auth/news_api/)
- **Visualizations**: [viz/news_api/](viz/news_api/)

### Reddit - Coming Soon 🚧
*Awaiting implementation by team members*
- **Scripts**: [scripts/reddit/](scripts/reddit/)
- **Data**: [data/reddit/](data/reddit/)
- **Auth**: [auth/reddit/](auth/reddit/)
- **Visualizations**: [viz/reddit/](viz/reddit/)

---

## 🚀 Quick Start: Bluesky Intelligence Module

**Current Status**: Operational with 156K+ posts analyzing homelessness discourse on Bluesky

Comprehensive Python toolkit for real-time social media intelligence gathering focused on homelessness and housing crisis discussions.

### Intelligence Capabilities

- 🎯 **Targeted Intelligence Collection**: 155+ keywords tracking homelessness, housing crisis, and social justice
- 📡 **Real-time Monitoring**: Firehose and search-based collection methods
- 📊 **Advanced Analytics**: Interactive EDA with geographic distribution, sentiment analysis, and engagement metrics
- 🗺️ **Geographic Intelligence**: Location-based analysis with word clouds and world maps
- 💾 **Flexible Outputs**: JSONL, CSV, JSON formats for downstream analysis
- 🔄 **Session Management**: Automated deduplication and data merging
- ⚡ **Production-Ready**: Sleep prevention, error handling, comprehensive logging

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Authentication

Create `auth/bluesky/config/auth.json` with your Bluesky credentials:

```json
{
  "bluesky": {
    "username": "your_username.bsky.social",
    "password": "your_app_password"
  }
}
```

### 3. Run Demo Collection

**🎯 EASIEST WAY - Interactive Demo**
```bash
cd scripts/bluesky
python demo.py
```
*This will show you a menu with options like:*
- Quick Test (1 minute)
- Standard Demo (5 minutes)
- Extended Demo (15 minutes)
- Custom Demo (your choice)

**⚡ Direct Commands**
```bash
cd scripts/bluesky

# 🚀 Quick Test - 60 seconds with homelessness keywords
python main.py --duration 60 --keywords homelessness

# 📊 Standard Demo - 300 seconds with all keywords
python main.py --duration 300 --keywords all

# 🎯 Custom - Use your own keywords from keywords.txt
python main.py --duration 600 --keywords custom

# 🔄 Merge all session data into alltime_socmed
python main.py --merge-data
```

### 4. Generate EDA Analysis

```bash
# Navigate to Bluesky visualizations
cd viz/bluesky

# Generate comprehensive EDA report
python improved_eda.py

# Or generate interactive report
python interactive_eda.py
```

This creates reports with:
- 📊 Key metrics and statistics
- 🌍 Geographic distribution (word clouds + world map)
- 📈 Content analysis and engagement metrics
- 👥 Author analysis and top posts feeds
- 🔗 Clickable links to original posts

### 5. View Results

```bash
# Open Jupyter notebook for analysis
cd scripts/bluesky
jupyter notebook analysis_demo.ipynb

# Or check the generated report
ls ../../data/bluesky/alltime_socmed/COLLECTION_REPORT_*.md
```

## Usage

### Command Line Options

```bash
cd scripts/bluesky
python main.py [OPTIONS]

Options:
  --method {search,firehose,both}  Collection method (default: search)
  --duration INTEGER              Duration in minutes (default: 15)
  --keywords TEXT                 Keywords: "all", "homelessness", "custom", or specific keyword
  --no-sleep                      Prevent system sleep during collection
  --help                          Show help message
```

### Keyword Options

- `homelessness` - Default homelessness keywords (20 terms)
- `all` - All available keywords (200+ terms)
- `custom` - Load from `keywords.txt` file
- `specific_keyword` - Use a single keyword

### Examples

```bash
cd scripts/bluesky

# 15-minute homelessness collection
python main.py

# 30-minute collection with all keywords
python main.py --duration 30 --keywords all

# Custom keywords from file
python main.py --keywords custom --duration 45

# Single keyword search
python main.py --keywords "housing crisis" --duration 10

# Long collection with sleep prevention
python main.py --duration 120 --keywords all --no-sleep
```

## Project Structure

```
dfp_f25_ngo_intelligence_blueteam/
├── README.md                     # Main project README
├── requirements.txt              # Python dependencies
├── scripts/
│   ├── bluesky/                  # Bluesky intelligence module ✅
│   │   ├── main.py               # Main data collector
│   │   ├── demo.py               # Interactive demo
│   │   ├── bluesky_social_justice_collector.py  # Core collector
│   │   ├── homelessness_keywords.py  # Keyword module (155+ terms)
│   │   ├── keywords.txt          # Customizable keyword list
│   │   ├── analysis_demo.ipynb   # Analysis notebook
│   │   ├── PRD.md                # Product requirements
│   │   └── PROJECT_SUMMARY.md    # Project summary
│   ├── google_trends/            # Google Trends module 🚧
│   │   └── README.md             # Setup instructions
│   ├── news_api/                 # News API module 🚧
│   │   └── README.md             # Setup instructions
│   └── reddit/                   # Reddit module 🚧
│       └── README.md             # Setup instructions
├── data/
│   ├── bluesky/                  # Bluesky data (156K posts) ✅
│   │   ├── alltime_socmed/       # Merged data repository
│   │   ├── sessions/             # Individual collection sessions (9 sessions)
│   │   └── alltime/              # Deduplicated master dataset
│   │       ├── alltime_socmed.csv      # 156,184 posts
│   │       └── alltime_socmed.jsonl    # Raw JSON format
│   ├── google_trends/            # Google Trends data 🚧
│   ├── news_api/                 # News API data 🚧
│   └── reddit/                   # Reddit data 🚧
├── auth/
│   ├── bluesky/
│   │   └── config/
│   │       └── auth.json         # Bluesky credentials (gitignored)
│   ├── google_trends/            # Google Trends auth (placeholder)
│   ├── news_api/                 # News API auth (placeholder)
│   └── reddit/                   # Reddit auth (placeholder)
└── viz/
    ├── bluesky/                  # Bluesky visualizations ✅
    │   ├── improved_eda.py       # Comprehensive EDA generator
    │   ├── interactive_eda.py    # Interactive EDA with extras
    │   ├── improved_eda_report.html     # Latest comprehensive report
    │   ├── interactive_eda_report.html  # Latest interactive report
    │   └── README.md             # Usage instructions
    ├── google_trends/            # Google Trends viz 🚧
    │   └── README.md
    ├── news_api/                 # News API viz 🚧
    │   └── README.md
    └── reddit/                   # Reddit viz 🚧
        └── README.md
```

## Output

Data is saved to `data/bluesky/alltime_socmed/` with timestamps:

- `socmed_search_YYYYMMDD_HHMMSS.jsonl` - Raw data
- `socmed_search_YYYYMMDD_HHMMSS.csv` - Spreadsheet format
- `socmed_search_YYYYMMDD_HHMMSS_summary.json` - Collection summary
- Visualizations in `viz/bluesky/*.html`

## Configuration

### Keywords

Edit `scripts/bluesky/keywords.txt` to customize search terms:

```
homeless
homelessness
housing crisis
affordable housing
# Add your keywords here
```

### Authentication

Place your Bluesky credentials in `auth/bluesky/config/auth.json`:

```json
{
  "bluesky": {
    "username": "your_username.bsky.social",
    "password": "your_app_password"
  }
}
```

## Requirements

- Python 3.8+
- Bluesky account with app password
- Required packages in `requirements.txt`

## Contributing

**Team Project**: DFP F25 NGO Intelligence Blue Team

Each team member can contribute their own intelligence source module:

1. **Choose your source**: Google Trends, News API, or Reddit
2. **Set up structure**: Use existing directory pattern (`scripts/{source}/`, `data/{source}/`, `auth/{source}/`, `viz/{source}/`)
3. **Follow READMEs**: Each placeholder directory includes setup instructions
4. **Develop independently**: Modular structure prevents merge conflicts
5. **Submit PR**: Update main README with your module status
6. **Document**: Add your findings to module-specific documentation

### Current Team Assignments
- ✅ **Bluesky**: Implemented (156K posts)
- 🚧 **Google Trends**: Available for assignment
- 🚧 **News API**: Available for assignment
- 🚧 **Reddit**: Available for assignment

## Project Information

- **Course**: DFP F25 (Digital Forensics & Privacy)
- **Team**: NGO Intelligence Blue Team
- **Focus**: Homelessness & Social Justice Intelligence
- **Academic Year**: Fall 2025
- **Institution**: Graduate Student Team Project

---

**Last Updated**: September 2025
**Data Collection Period**: September 2024 - Present
**Total Posts Analyzed**: 156,184 (Bluesky)