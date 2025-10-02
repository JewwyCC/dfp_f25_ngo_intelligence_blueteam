# Bluesky Data Collector - GUI Application

## Overview

The GUI application provides a user-friendly interface for collecting and visualizing Bluesky social justice data. It includes:

- **Interactive Control Panel** - Configure and run data collection
- **Real-time Progress Monitoring** - Watch collection statistics live
- **Integrated Visualizations** - Generate publication-quality charts
- **Data Export** - Export to CSV/JSON formats

## Features

### 1. Data Collection Interface
- Visual duration/date range selection
- Keyword customization
- Collection method selection (firehose/search/hybrid)
- Real-time progress tracking
- Stop/pause controls

### 2. Visualization Dashboard
Automatically generates comprehensive visualizations including:

#### Content Analysis
- **Word Clouds** - Topic and sentiment visualization
- **Geographic Distribution** - Where conversations happen
- **Post Length Distribution** - Content metrics

#### Political Analysis
- **Polarization Gauge** - Left/center/right distribution
- **Political Word Clouds** - Side-by-side comparison
- **Sentiment Analysis** - Political lean detection

#### Engagement Metrics
- **Temporal Patterns** - Hourly activity heatmaps
- **Engagement Distribution** - Likes, replies, reposts
- **Top Posts** - Most engaging content
- **Correlation Analysis** - Post length vs engagement

#### Author Insights
- **Top Contributors** - Most active authors
- **Follower Analysis** - Influence metrics
- **Author Activity Patterns**

### 3. Data Export
- CSV format for analysis
- JSON format for archival
- HTML reports with embedded visualizations

## Usage

### Prerequisites

Install additional GUI dependencies:
```bash
pip install tkinter matplotlib wordcloud
```

### Running the GUI

```bash
cd scripts/bluesky
python gui.py
```

### Basic Workflow

1. **Configure Collection**
   - Select collection method (firehose/search/hybrid)
   - Set duration or date range
   - Customize keywords if needed

2. **Start Collection**
   - Click "Start Collection"
   - Monitor real-time progress
   - Watch statistics update

3. **View Results**
   - Click "Generate Visualizations" when complete
   - Explore interactive charts
   - Export data as needed

4. **Open Visualization Reports**
   - Navigate to viz/bluesky/
   - Open HTML reports in browser for detailed analysis

## Visualization Files

The viz folder contains:

- **`gui_viz.py`** - Visualization generation module
- **`improved_eda.py`** - Enhanced exploratory data analysis
- **`interactive_eda.py`** - Interactive HTML report generator
- **`bluesky_py_export.html`** - Sample visualization report
- **`improved_eda_report.html`** - Full analysis report (3.1MB)
- **`interactive_eda_report.html`** - Interactive dashboard (3.2MB)

## Visualization Structure

The narrative follows a data journalism approach:

1. **What We're Tracking** - Keywords and topics
2. **When Data Was Collected** - Time period
3. **What People Are Saying** - Content word clouds
4. **Where Conversations Happen** - Geographic distribution
5. **Political Landscape** - Polarization analysis
6. **Content Patterns** - Length and structure
7. **Engagement Analysis** - Interaction metrics
8. **Author Insights** - Contributor analysis
9. **Top Content** - Most engaging posts
10. **Correlations** - Engagement patterns
11. **Summary Statistics** - Overall metrics

## Integration with Main Collector

The GUI uses the core collector (`bluesky_social_justice_collector.py`) and wraps it with:
- Visual progress bars
- Real-time statistics updates
- Thread-safe collection management
- Automatic visualization generation

## Example Visualizations

The included HTML reports (`viz/bluesky/*.html`) show:
- Professional publication-quality charts
- NYT-style minimal design
- Color-coded political analysis
- Interactive data exploration

## Tips

- **Long Collections**: Use the GUI to monitor progress
- **Visualizations**: Generate after collection completes
- **HTML Reports**: Open in Chrome/Firefox for best experience
- **Data Export**: Use CSV for analysis in Excel/Python/R

## Technical Notes

- Uses tkinter for cross-platform GUI
- Matplotlib for chart generation
- WordCloud for text visualization
- Threading for non-blocking collection
- Automatic session management

## Troubleshooting

**GUI doesn't open:**
```bash
# macOS
brew install python-tk

# Ubuntu/Debian
sudo apt-get install python3-tk
```

**Visualizations not generating:**
```bash
pip install --upgrade matplotlib wordcloud pandas
```

**Collection not starting:**
- Check authentication in `auth/bluesky/config/auth.json`
- Verify network connectivity
- Check console for error messages
