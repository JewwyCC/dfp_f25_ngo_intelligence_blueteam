# Bluesky Homelessness Data Collector

A comprehensive Bluesky data collection tool **focused extensively on homelessness** and related housing insecurity issues. Tracks 12 distinct homelessness-related categories with extensive keyword variations for comprehensive data coverage.

## Features

- ✅ **Dual Collection Methods:**
  - Real-time firehose collection (live posts)
  - Historical search API with deep pagination
  - Hybrid mode (both methods combined)

- ✅ **Rich Data Collection:**
  - Author follower counts and profile metrics
  - Content analysis (hashtags, mentions, URLs)
  - Engagement metrics (likes, reposts, replies)
  - Influence scoring

- ✅ **Smart Features:**
  - Session-based organization with alltime datasets
  - Automatic deduplication
  - Resumable collection with cursor persistence
  - Rate limiting and API compliance

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up authentication:**
   - Copy template: `cp auth/bluesky/config/auth_template.json auth/bluesky/config/auth.json`
   - Get app password from: https://bsky.app/settings/app-passwords
   - Fill in your credentials in `auth.json`

## Usage

### Quick Start (15-20 seconds sample)

Collect sample data for testing:

```bash
cd scripts/bluesky
python bluesky_social_justice_collector.py --method firehose --duration 20
```

### Real-time Collection (Firehose)

Collect live posts for 30 minutes:

```bash
python bluesky_social_justice_collector.py --method firehose --duration 1800
```

### Historical Collection (Search API)

Collect posts from the past 7 days:

```bash
python bluesky_social_justice_collector.py --method search --days-back 7 --max-posts 500
```

### Hybrid Collection

Combine both methods:

```bash
# Option 1: Auto-split time (75% search, 25% firehose)
python bluesky_social_justice_collector.py --method both --total-time 600

# Option 2: Manual time allocation
python bluesky_social_justice_collector.py --method both --days-back 7 --duration 300
```

## Keywords Tracked - HOMELESSNESS FOCUS

The collector extensively monitors **12 homelessness-related categories**:

1. **Homelessness** - General homelessness discussions, crisis, epidemic
2. **Homeless Individuals** - People experiencing homelessness
3. **Unhoused** - Alternative terminology and unhoused community
4. **Street Homelessness** - Rough sleeping, living on streets
5. **Chronic Homelessness** - Long-term homelessness patterns
6. **Housing Insecurity** - At-risk populations, unstable housing
7. **Homeless Shelter** - Emergency shelters, transitional housing
8. **Homeless Encampment** - Tent cities, encampment sweeps
9. **Homeless Crisis** - Emergency situations and responses
10. **Homeless Veterans** - Veteran-specific homelessness
11. **Homeless Youth** - Youth and child homelessness
12. **Homeless Families** - Family homelessness situations

Each category includes **6-10 search query variations** and multiple regex patterns for comprehensive coverage (100+ total search queries).

## Output Structure

```
data/bluesky/
├── sessions/          # Individual collection sessions
│   └── session_YYYYMMDD_HHMMSS/
│       ├── *_posts.jsonl
│       └── session_summary.json
└── alltime/          # Cumulative deduplicated data
    ├── food_insecurity_alltime.jsonl
    ├── food_insecurity_alltime.csv
    └── ...
```

## Data Fields

Each collected post includes:

**Basic Post Data:**
- uri, cid, text, created_at, lang
- author_handle, author_did, keyword

**Author Profile:**
- followers_count, following_count, posts_count
- account_age_days, posts_per_day
- follower_following_ratio, influence_score

**Content Analysis:**
- word_count, char_count
- hashtags, mentions, urls
- has_images, has_external_link
- emotion_score, is_reply

**Engagement Metrics:**
- reply_count, repost_count, like_count

## Safety & Compliance

- ✅ Uses official Bluesky API (no scraping violations)
- ✅ Respects rate limits
- ✅ Uses app passwords (not main credentials)
- ✅ Credentials stored securely (never committed)
- ✅ Deduplication prevents data redundancy
- ✅ Session-based collection for organization

## Sample Data

Sample data with ~1000 posts is provided in `data/bluesky/sample/`:
- `bluesky_sample_1000.json` - Full JSON dataset
- `bluesky_sample.csv` - CSV format for analysis
- `README.md` - Sample data documentation

## Troubleshooting

**Authentication Error:**
- Verify credentials in `auth/bluesky/config/auth.json`
- Ensure you're using an app password, not your main password
- Check your Bluesky account is active

**No Posts Collected:**
- Try increasing duration for firehose method
- Check keyword relevance for search method
- Verify network connectivity

**Rate Limiting:**
- The script includes automatic rate limiting
- For search API, there's a 0.5-1 second delay between requests

## Contributing

This collector is part of the DFP F25 NGO Intelligence Blue Team project. For questions or contributions, please refer to the main project README.

## License

Part of the Data Focused Python course project at Carnegie Mellon University.
