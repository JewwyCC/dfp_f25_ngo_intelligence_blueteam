# 🌐 Web Data Viewer

Simple HTML interface for exploring collected Bluesky social justice data.

## Features

### 📊 **Data Visualization**
- **Keyword Distribution Chart**: Bar chart showing posts per social justice theme
- **Daily Trends Chart**: Line chart showing theme activity over time
- **Real-time Data**: Loads directly from alltime JSONL files

### 🔍 **Search & Browse**
- **Wildcard Search**: Search posts by text content
- **Pagination**: 20 posts per page with navigation
- **All Themes**: Searches across all collected social justice topics

### 👥 **Author Analysis**
- **Top Authors**: Ranked by follower count
- **Author Details**: Shows themes they discuss and sample tweets
- **Pagination**: 5 authors per page with navigation

## Quick Start

### 1. Install Dependencies
```bash
pip install flask
```

### 2. Run Web Viewer
```bash
python web_viewer.py
```

### 3. Open Browser
Navigate to: `http://localhost:5000`

## Usage

### Search Posts
- Type in search bar for wildcard matching
- Press Enter or click Search
- Navigate with pagination controls

### View Charts
- Keyword chart updates automatically
- Daily trends show activity patterns
- Charts are interactive and responsive

### Browse Authors
- Top authors sorted by follower count
- See what themes each author discusses
- Navigate through author pages

## Data Source

The web viewer reads directly from:
- `data/alltime/*_alltime.jsonl` files
- No modification to collector functionality
- Real-time data loading

## Technical Details

- **Backend**: Flask with JSON API endpoints
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Charts**: Chart.js for visualizations
- **Data**: Pandas for processing
- **Port**: 5000 (configurable)

## API Endpoints

- `GET /api/search?q=query&page=1` - Search posts
- `GET /api/keyword-stats` - Keyword statistics
- `GET /api/daily-trends` - Daily trend data
- `GET /api/top-authors?page=1` - Top authors

## Requirements

- Python 3.7+
- Flask 2.3+
- Existing alltime data files
- Modern web browser
