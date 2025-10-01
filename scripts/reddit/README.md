# Reddit Module

## Status: Coming Soon 🚧

This directory is reserved for Reddit data collection scripts.

## Setup Instructions

1. Create a Reddit application at https://www.reddit.com/prefs/apps

2. Install required dependencies:
```bash
pip install praw
```

3. Create authentication config in [auth/reddit/](../../auth/reddit/)
```json
{
  "reddit": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "user_agent": "your_user_agent"
  }
}
```

4. Add your scripts here:
   - Data collection scripts
   - Analysis notebooks
   - Utility functions

## Expected Structure

```
scripts/reddit/
├── main.py              # Main data collector
├── keywords.py          # Keyword management
├── subreddits.txt       # List of subreddits to monitor
├── analysis.ipynb       # Analysis notebook
└── utils.py            # Helper functions
```

## Data Output

Data should be saved to [data/reddit/](../../data/reddit/)

## Visualizations

Visualizations should be saved to [viz/reddit/](../../viz/reddit/)

## Contributing

Team members working on Reddit:
- [ ] Add your name here
- [ ] Update this README with implementation details
- [ ] Add requirements to root requirements.txt
