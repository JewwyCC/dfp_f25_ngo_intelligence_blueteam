# Social Media NGO Research Project

A multi-source data collection and analysis platform for NGO research, supporting Bluesky, Google Trends, News API, and Reddit.

## 📊 Data Sources

### [Bluesky](scripts/bluesky/) - Active ✅
Collecting and analyzing homelessness discussions from Bluesky social media platform.
- **Status**: Fully implemented
- **Scripts**: [scripts/bluesky/](scripts/bluesky/)
- **Data**: [data/bluesky/](data/bluesky/)
- **Auth**: [auth/bluesky/](auth/bluesky/)
- **Visualizations**: [viz/bluesky/](viz/bluesky/)

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

## 🚀 Bluesky Module - Quick Start

A comprehensive Python tool for collecting and analyzing homelessness discussions from Bluesky social media platform.

### Features

- **Keyword-based search** with customizable keyword lists focused on homelessness
- **Real-time data collection** with firehose and search methods
- **Comprehensive EDA analysis** with interactive visualizations
- **Geographic distribution** analysis with word clouds and world maps
- **Multiple output formats** (JSONL, CSV, JSON)
- **System sleep prevention** during long collections
- **Interactive web dashboard** for data exploration

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
cd viz/bluesky
python improved_eda.py
```

This creates `improved_eda_report.html` with:
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
dfp_f25_socmed_blueteam/
├── README.md                     # Main project README
├── requirements.txt              # Python dependencies
├── PRD.md                        # Product Requirements Document
├── scripts/
│   ├── bluesky/                  # Bluesky scripts
│   │   ├── main.py               # Main data collector
│   │   ├── demo.py               # Interactive demo script
│   │   ├── keywords.txt          # Customizable keyword list
│   │   ├── homelessness_keywords.py  # Keyword module
│   │   └── *.ipynb               # Analysis notebooks
│   ├── google_trends/            # Google Trends scripts (placeholder)
│   ├── news_api/                 # News API scripts (placeholder)
│   └── reddit/                   # Reddit scripts (placeholder)
├── data/
│   ├── bluesky/
│   │   ├── alltime_socmed/       # Merged data (CSV, JSONL)
│   │   ├── sessions/             # Individual collection sessions
│   │   └── alltime/              # Historical data
│   ├── google_trends/            # Google Trends data (placeholder)
│   ├── news_api/                 # News API data (placeholder)
│   └── reddit/                   # Reddit data (placeholder)
├── auth/
│   ├── bluesky/
│   │   └── config/
│   │       └── auth.json         # Bluesky credentials (gitignored)
│   ├── google_trends/            # Google Trends auth (placeholder)
│   ├── news_api/                 # News API auth (placeholder)
│   └── reddit/                   # Reddit auth (placeholder)
└── viz/
    ├── bluesky/
    │   ├── improved_eda.py       # EDA analysis generator
    │   ├── interactive_eda.py    # Interactive EDA
    │   └── *.html                # Generated reports
    ├── google_trends/            # Google Trends viz (placeholder)
    ├── news_api/                 # News API viz (placeholder)
    └── reddit/                   # Reddit viz (placeholder)
```

## Output

Data is saved to `data/bluesky/alltime_socmed/` with timestamps:

- `socmed_search_YYYYMMDD_HHMMSS.jsonl` - Raw data
- `socmed_search_YYYYMMDD_HHMMSS.csv` - Spreadsheet format
- `socmed_search_YYYYMMDD_HHMMSS_summary.json` - Collection summary
- Visualizations in `viz/bluesky/improved_eda_report.html`

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

This is a grad student team project. Each team member can contribute their own data source module:

1. Create your module directories: `scripts/{source}/`, `data/{source}/`, `auth/{source}/`, `viz/{source}/`
2. Implement your data collection and analysis scripts
3. Update this README with your module information
4. Submit a pull request

## License

DFP F25 Social Media Blue Team Project