# Bluesky Sample Dataset

## Overview

Representative sample of Bluesky homelessness discourse data for demos, testing, and quick analysis.

**Collection Period**: September 2024 - September 2025
**Sample Size**: 8,777 posts (22.7% of full dataset)
**File Size**: 9.92 MB (CSV) + 2.43 MB (JSON)

## Dataset Statistics

- **Total Posts**: 8,777
- **Unique Authors**: 7,157
- **Original Dataset**: 38,619 posts (full dataset on local machine)
- **Sampling Method**: Random stratified sampling (seed=42 for reproducibility)

## Files

### Main Sample
- **`bluesky_sample.csv`** (9.92 MB)
  - Complete sample with all 8,777 posts
  - All original columns preserved
  - Ready for analysis

### Quick Load Sample
- **`bluesky_sample_1000.json`** (2.43 MB)
  - First 1,000 posts in JSON format
  - Ideal for quick demos and testing
  - Easy to load in web applications

### Metadata
- **`sample_summary.json`**
  - Sample statistics
  - Dataset information

## Data Fields

Each post includes:
- **Identity**: uri, author_handle, author_did
- **Content**: text, created_at
- **Engagement**: like_count, repost_count, reply_count
- **Links**: embed_images, embed_external
- **Keywords**: matched keywords for homelessness topics
- **Additional metadata**: Various platform-specific fields

## Usage

### Python (Pandas)
```python
import pandas as pd

# Load full sample
df = pd.read_csv('bluesky_sample.csv')
print(f"Loaded {len(df):,} posts")

# Basic analysis
print(df['like_count'].describe())
print(df['author_handle'].value_counts().head(10))
```

### Python (JSON - Quick Load)
```python
import json

with open('bluesky_sample_1000.json') as f:
    posts = json.load(f)

print(f"Loaded {len(posts)} posts")
for post in posts[:5]:
    print(f"- {post['text'][:60]}...")
```

### R
```r
library(readr)
df <- read_csv("bluesky_sample.csv")
summary(df)
```

## Why Sample Data?

The full Bluesky dataset (38,619 posts, 44 MB) is kept locally for analysis, while this sample is pushed to GitHub for:

✅ **Quick Access**: Fast downloads and demos
✅ **Collaboration**: Easy for team members to test code
✅ **GitHub Friendly**: Stays under file size limits
✅ **Representative**: Random sampling preserves data characteristics

## Full Dataset

The complete dataset (156,184 total posts across all collections) is available locally:
- Location: `data/bluesky/alltime/`
- Size: 648 MB
- Format: CSV and JSONL
- Access: Team members with local clone

## Data Quality

✅ **Deduplicated**: No duplicate URIs
✅ **Validated**: All required fields present
✅ **Clean**: Removed deleted/suspended accounts
✅ **Recent**: September 2024 - September 2025
✅ **Authentic**: Direct from Bluesky AT Protocol API

## Keywords Tracked

Sample includes posts matching 155+ keywords:
- homeless, homelessness, unhoused
- housing crisis, affordable housing
- eviction, rent burden, gentrification
- shelter, transitional housing
- street homelessness, tent cities
- And 140+ more related terms

## Collection Method

- **API**: Bluesky AT Protocol (atproto)
- **Method**: Firehose + Search API
- **Keywords**: 155+ homelessness-related terms
- **Deduplication**: By URI
- **Cleaning**: Automated validation

## Citing This Data

```
Bluesky Homelessness Discourse Dataset (Sample)
Carnegie Mellon University - Heinz College
Data Focused Python (Fall 2025)
Collection Period: September 2024 - September 2025
Sample: 8,777 posts (22.7% stratified random sample)
```

---

**Generated**: October 2025
**Module**: Bluesky Data Collection
**Course**: DFP F25
**Institution**: Carnegie Mellon University - Heinz College
