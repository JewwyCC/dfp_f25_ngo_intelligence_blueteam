# NGO Intelligence Platform - Homelessness Research

**Comprehensive multi-source data collection and analysis platform for homelessness research**

*Carnegie Mellon University - DFP F25 | DFP Blue Team: Jerry, Kaitlin, Mel, Rizaldy, Shriya*

---

## 🎯 Overview

The NGO Intelligence Platform is a comprehensive data collection and visualization system designed for homelessness research. It integrates data from multiple sources including Google Trends, News APIs, Reddit, and Bluesky social media, providing automated analysis and interactive visualizations.

### Key Features

- **Multi-Source Data Collection**: Google Trends, News API, Reddit, Bluesky
- **Interactive Dashboard**: Streamlit-based web interface
- **Automated Visualizations**: Charts, maps, and analysis reports
- **Political Classification**: News sentiment and political bias analysis
- **Real-Time Processing**: Live data collection and analysis
- **Demo Data Integration**: Fast loading with comprehensive sample data

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Git
- Internet connection for data collection

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dfp_ngo_module
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the platform**
   ```bash
   # Option 1: Simple launcher (recommended)
   ./start_platform.sh dashboard
   
   # Option 2: Direct Streamlit
   streamlit run ngo_dashboard.py
   ```

4. **Access the dashboard**
   - Open your browser to `http://localhost:8501`
   - Use demo data or enter a ZIP code for fresh analysis

---

## 📊 Data Sources

### 1. Google Trends
- **Purpose**: Search volume patterns and geographic interest
- **Data**: National and state-level search trends
- **Visualizations**: Time series, choropleth maps, seasonal patterns
- **Note**: Uses demo data for fast loading during analysis

### 2. News API
- **Purpose**: Media coverage analysis and political classification
- **Data**: Articles from major news sources
- **Analysis**: Sentiment analysis, political bias classification
- **Visualizations**: Word clouds, timeline analysis, source distribution

### 3. Reddit
- **Purpose**: Community discussions and lived experiences
- **Data**: Posts from homelessness-related subreddits
- **Analysis**: Engagement metrics, topic clustering
- **Visualizations**: Engagement trends, subreddit analysis, post timelines

### 4. Bluesky Social
- **Purpose**: Social media sentiment and real-time discussions
- **Data**: Posts and engagement metrics
- **Analysis**: Sentiment trends, author analysis
- **Visualizations**: Engagement patterns, top posts table, sentiment timeline

---

## 🖥️ Dashboard Features

### Home Page
- **Interactive ZIP Code Analysis**: Enter any US ZIP code for regional analysis
- **Demo Data Access**: Quick access to comprehensive sample data
- **Progress Tracking**: Real-time data collection status
- **Navigation**: Seamless flow between data collection and visualization

### Data Collection
- **Smart Scraping**: Fresh data collection for News, Reddit, and Bluesky
- **Demo Integration**: Fast Google Trends loading using demo data
- **Progress Monitoring**: Real-time status updates and completion tracking
- **Error Handling**: Robust error management and recovery

### Visualizations
- **Interactive Charts**: Plotly-based interactive visualizations
- **Geographic Maps**: Choropleth maps with real data integration
- **Data Tables**: Sortable and paginated data displays
- **Responsive Design**: Optimized for different screen sizes

### Analysis Sections
1. **Search Trends**: Google Trends analysis with geographic insights
2. **Media Coverage**: News analysis with political classification
3. **Community Discussions**: Reddit engagement and topic analysis
4. **Social Sentiment**: Bluesky sentiment and engagement patterns

---

## 🛠️ Technical Architecture

### Core Components

- **`ngo_dashboard.py`**: Main Streamlit dashboard application
- **`master_scraper_data.py`**: Data collection orchestrator
- **`master_scraper_viz.py`**: Visualization generation system
- **`start_platform.sh`**: Platform launcher script

### Data Flow

1. **Data Collection**: Multi-source scraping with session management
2. **Data Processing**: Cleaning, deduplication, and formatting
3. **Visualization Generation**: Automated chart and map creation
4. **Dashboard Integration**: Real-time display and interaction

### Session Management

- **Session Directories**: Organized by timestamp (`session_YYYYMMDD_HHMMSS`)
- **Raw Data Storage**: CSV, JSON, JSONL files in `raw_data/`
- **Visualizations**: PNG, HTML files in `artifacts/`
- **Demo Data**: Comprehensive sample data in `demo_data/`

---

## 📁 Project Structure

```
dfp_ngo_module/
├── ngo_dashboard.py              # Main dashboard application
├── master_scraper_data.py        # Data collection orchestrator
├── master_scraper_viz.py         # Visualization generator
├── start_platform.sh            # Platform launcher
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── data/
│   ├── demo_data/               # Demo/sample data
│   │   └── demo_session/
│   │       ├── raw_data/        # Sample CSV/JSON files
│   │       └── artifacts/       # Sample visualizations
│   └── master_output/           # Generated data sessions
│       └── session_*/           # Timestamped sessions
├── scripts/                     # Individual scraper modules
│   ├── google_trends/           # Google Trends scraper
│   ├── news_api/                # News API scraper
│   ├── reddit/                  # Reddit scraper
│   └── bluesky/                 # Bluesky scraper
└── auth/                        # Authentication configurations
    └── bluesky/                 # Bluesky API credentials
```

---

## 🔧 Configuration

### API Credentials

1. **News API**: Add your API key to `scripts/news_api/credentials.py`
2. **Reddit**: Configure PRAW credentials in `scripts/reddit/config.py`
3. **Bluesky**: Add authentication to `auth/bluesky/auth.json`

### Environment Variables

```bash
# Optional: Disable HuggingFace tokenizers parallelism warning
export TOKENIZERS_PARALLELISM=false
```

---

## 📈 Usage Examples

### Quick Analysis with Demo Data

1. Launch the dashboard: `./start_platform.sh dashboard`
2. Click "Go To Visualization" to load demo data
3. Explore comprehensive sample visualizations

### Fresh Data Collection

1. Enter a US ZIP code (e.g., "10001" for NYC)
2. Click "Analyze Region"
3. Monitor real-time progress
4. View generated visualizations

### Custom Analysis

1. Navigate to specific sections
2. Filter by themes or time periods
3. Export data or visualizations
4. Share insights and findings

---

## 🐛 Troubleshooting

### Common Issues

**Dashboard won't start**
```bash
# Check dependencies
pip install -r requirements.txt

# Try direct Streamlit
streamlit run ngo_dashboard.py
```

**Data collection fails**
```bash
# Check API credentials
# Verify internet connection
# Check logs in terminal output
```

**Visualizations not loading**
```bash
# Ensure demo data exists in data/demo_data/
# Check file permissions
# Verify Streamlit cache
```

### Performance Tips

- Use demo data for quick exploration
- Google Trends uses demo data for fast loading
- Fresh data collection may take 2-5 minutes
- Clear browser cache if visualizations appear outdated

---

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

### Code Style

- Follow Python PEP 8 guidelines
- Use descriptive variable names
- Add docstrings to functions
- Include error handling

---

## 📄 License

This project is developed for educational and research purposes at Carnegie Mellon University.

---

## 🙏 Acknowledgments

- **DFP Blue Team**: Jerry, Kaitlin, Mel, Rizaldy, Shriya
- **Carnegie Mellon University**: DFP F25 Program
- **Open Source Libraries**: Streamlit, Plotly, Pandas, and more

---

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the demo data and examples
3. Check terminal output for detailed error messages
4. Ensure all dependencies are properly installed

---

*Last updated: January 2025*