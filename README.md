# Bluesky Homelessness Data Analysis

A comprehensive Python tool for collecting and analyzing homelessness discussions from Bluesky social media platform with advanced EDA capabilities.

## Features

- **Keyword-based search** with customizable keyword lists focused on homelessness
- **Real-time data collection** with firehose and search methods
- **Comprehensive EDA analysis** with interactive visualizations
- **Geographic distribution** analysis with word clouds and world maps
- **Multiple output formats** (JSONL, CSV, JSON)
- **System sleep prevention** during long collections
- **Interactive web dashboard** for data exploration

## 🚀 Quick Start Demo

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Authentication

Create `data/config/auth.json` with your Bluesky credentials:

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
python demo.py
```
*This will show you a menu with options like:*
- Quick Test (1 minute)
- Standard Demo (5 minutes) 
- Extended Demo (15 minutes)
- Custom Demo (your choice)

**⚡ Direct Commands**
```bash
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
# Generate comprehensive EDA report
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
jupyter notebook analysis_demo.ipynb

# Or check the generated report
ls data/alltime_socmed/COLLECTION_REPORT_*.md
```

## Usage

### Command Line Options

```bash
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

## File Structure

```
dfp_f25_socmed_blueteam/
├── main.py                    # Main data collector
├── demo.py                    # Interactive demo script
├── improved_eda.py            # EDA analysis generator
├── analysis_demo.ipynb        # Jupyter notebook for analysis
├── keywords.txt               # Customizable keyword list
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── PRD.md                     # Product Requirements Document
├── data/
│   ├── config/
│   │   └── auth.json          # Bluesky credentials
│   ├── alltime_socmed/        # Merged data (CSV, JSONL)
│   └── sessions/              # Individual collection sessions
└── templates/
    ├── index.html             # Web viewer template
    └── eda_dashboard.html     # EDA dashboard template
```

## Output

Data is saved to `data/alltime_socmed/` with timestamps:

- `socmed_search_YYYYMMDD_HHMMSS.jsonl` - Raw data
- `socmed_search_YYYYMMDD_HHMMSS.csv` - Spreadsheet format
- `socmed_search_YYYYMMDD_HHMMSS_summary.json` - Collection summary
- `improved_eda_report.html` - Comprehensive EDA analysis

## Configuration

### Keywords

Edit `keywords.txt` to customize search terms:

```
homeless
homelessness
housing crisis
affordable housing
# Add your keywords here
```

### Authentication

Place your Bluesky credentials in `data/config/auth.json`:

   ```json
   {
     "bluesky": {
    "username": "your_username.bsky.social",
    "password": "your_app_password"
     }
   }
   ```

## Data Analysis

Use the Jupyter notebook for data analysis:

   ```bash
jupyter notebook analysis_demo.ipynb
```

## Project Structure

```
├── main.py                    # Main collection script
├── keywords.txt              # Custom keywords file
├── requirements.txt          # Python dependencies
├── analysis_demo.ipynb      # Data analysis notebook
├── data/
│   ├── config/
│   │   └── auth.json        # Authentication (gitignored)
│   └── alltime_socmed/      # Collected data
├── templates/
│   └── index.html           # Web viewer template
└── web_viewer.py            # Web viewer for data visualization
```

## Requirements

- Python 3.8+
- Bluesky account with app password
- Required packages in `requirements.txt`

## License

DFP F25 Social Media Blue Team Project