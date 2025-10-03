# Reddit Data Analyzer for Social Issues

A Python-based tool for collecting, analyzing, and visualizing Reddit data related to social issues like homelessness, housing, and poverty.

## 🚀 Quick Start

```bash
python reddit_scraper_app.py
```

## 📊 Data Collection

**Method**: PRAW-based keyword search across selected subreddits
**Location**: `RedditScraper/data_collection.py` - `collect_by_search()`

### Recommended Settings
- **Posts per subreddit**: 1000
- **Time period**: 1 year
- **Strategy**: Comprehensive (uses all search methods)

### How It Works
1. Searches across configured subreddits using specific keywords
2. Applies time-based filtering for fair temporal distribution
3. Caps posts per time bin to ensure even coverage
4. Uses weekly binning for trend analysis

## 🎯 Analysis Results

**Location**: `RedditScraper/analysis.py`

### Key Metrics
- **Post Count Density**: Number of posts per week
- **Engagement Density**: Total upvotes + comments per week
- **Sentiment Analysis**: Keyword-based sentiment scoring
- **Topic Classification**: Automatic categorization of posts

### What Results Mean
- **Green Hills**: Volume of discussion (post frequency)
- **Red Hills**: Community engagement (interaction levels)
- **Point Colors**: Engagement intensity (darker = more engagement)
- **Smooth Curves**: Natural trends over time using cubic spline interpolation

## 📈 Visualizations

**Location**: `RedditScraper/visualization.py` - `build_dashboard()`

### Components
1. **Main Analysis**: Smooth density plots with weekly binning
2. **Word Cloud**: Sentiment-based keyword visualization
3. **Featured Posts**: Top 3 highest engagement posts

### Visualization Construction
- **Smooth Curves**: Cubic spline interpolation + Gaussian smoothing
- **Weekly Binning**: `_time_bin()` function groups data by week
- **Density Plots**: `_create_smooth_density_plot()` creates hill-like structures
- **Color Coding**: Red spectrum for sentiment, green for post volume

## ⚙️ Configuration

**Location**: `RedditScraper/config.py`

### Key Settings
- **Subreddits**: Configured in `ISSUE_CONFIGS["Housing/Homelessness"]["subreddits"]`
- **Keywords**: Search terms in `ISSUE_CONFIGS["Housing/Homelessness"]["keywords"]`
- **Reddit Auth**: API credentials in `RedditAuth` class

### Current Subreddits
```
homeless, housing, eviction, affordablehousing, rent, shelter, 
housingcrisis, mildlyinfuriating, povertyfinance, news, nostupidquestions
```

## 🔧 Key Code Segments

| Component | File | Function |
|-----------|------|----------|
| Data Collection | `data_collection.py` | `collect_by_search()` |
| Time Binning | `visualization.py` | `_time_bin()` |
| Smooth Plots | `visualization.py` | `_create_smooth_density_plot()` |
| Analysis | `analysis.py` | `get_top_topic_keywords_by_frequency()` |
| GUI | `gui.py` | `_collect_data()` |

## 📋 Requirements

- Python 3.11+
- PRAW (Reddit API)
- SciPy (smooth interpolation)
- Matplotlib (visualization)
- Pandas (data processing)
- TextBlob (sentiment analysis)

## 🎯 Best Practices

1. **Use 1-year time period** for comprehensive trend analysis
2. **1000 posts per subreddit** for statistical significance
3. **Weekly binning** shows natural patterns
4. **Smooth curves** reveal underlying trends
5. **Engagement density** indicates community interest levels

## 📝 Output

The tool generates:
- Interactive GUI with data collection controls
- Smooth density visualizations
- Sentiment-based word clouds
- Featured high-engagement posts
- Comprehensive analysis reports
