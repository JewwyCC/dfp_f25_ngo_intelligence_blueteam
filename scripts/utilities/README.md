# Utility Scripts

This folder contains utility scripts for data collection, visualization generation, and platform setup.

## Data Collection Scripts

- `scrape_reddit_1year.py` - Collect 1 year of Reddit data
- `scrape_bluesky_1month.py` - Collect 1 month of Bluesky data (targeting 1000+ posts)
- `scrape_comprehensive_data.py` - Comprehensive data collection across all sources
- `enrich_bluesky_demo.py` - Enrich and deduplicate Bluesky demo data

## Visualization Generation Scripts

- `regen_news_viz_final.py` - Regenerate news visualizations with LEFT/RIGHT emphasis
- `regenerate_news_viz.py` - Original news visualization regeneration
- `regenerate_demo_viz.py` - Regenerate all demo visualizations
- `deduplicate_viz.py` - Remove duplicate visualization files
- `generate_news_viz.py` - Generate news visualizations
- `dashboard_visualizations.py` - Dashboard-specific visualizations

## Platform & Setup Scripts

- `setup_platform.py` - Platform setup and configuration
- `launcher.py` - Platform launcher
- `simple_launcher.py` - Simplified launcher
- `run_dashboard.py` - Run the dashboard
- `start_platform.sh` - Shell script to start platform
- `install.bat` - Windows installation script
- `ngo_dashboard_backup.py` - Backup of main dashboard

## Testing Scripts

- `test_gui.py` - GUI testing
- `test_master_news.py` - Master news scraper testing
- `test_news_viz.py` - News visualization testing
- `test_split_scrapers.sh` - Test split scrapers

## Demo & Sample Scripts

- `create_demo_session.py` - Create demo session data
- `create_sample_sessions.py` - Create sample sessions

## Usage

Most scripts can be run directly:

```bash
python3 scripts/utilities/scrape_reddit_1year.py
python3 scripts/utilities/enrich_bluesky_demo.py
```

Some scripts require API credentials to be configured in the respective module configuration files.
