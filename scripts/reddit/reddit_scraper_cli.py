#!/usr/bin/env python3
"""
Reddit CLI Scraper for Homelessness Data Collection
Outputs to: data/reddit/reddit_posts.csv and reddit_posts.json
"""

import os
import sys
import praw
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import RedditAuth, ISSUE_CONFIGS
from data_collection import collect_by_search


def main():
    """Run Reddit scraping for homelessness"""
    
    # Get configuration
    auth = RedditAuth()
    homelessness_config = ISSUE_CONFIGS["Housing/Homelessness"]
    
    subreddits = homelessness_config["subreddits"]
    keywords = homelessness_config["keywords"]
    
    print(f"🔍 Reddit Homelessness Scraper")
    print(f"   Subreddits: {len(subreddits)} ({', '.join(subreddits[:5])}...)")
    print(f"   Keywords: {len(keywords)} ({', '.join(keywords[:5])}...)")
    
    # Create Reddit client
    try:
        reddit = praw.Reddit(
            client_id=auth.client_id,
            client_secret=auth.client_secret,
            user_agent=auth.user_agent
        )
        print("✓ Connected to Reddit API")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return
    
    # Collect data using search method (best for comprehensive collection)
    print(f"\n📊 Collecting posts...")
    df = collect_by_search(
        reddit=reddit,
        subreddits=subreddits,
        keywords=keywords,
        posts_per_sub=100,  # 100 posts per subreddit
        time_filter='year',  # Last 365 days (1 year)
        strategy='comprehensive'  # Use comprehensive strategy (not fast)
    )
    
    if df.empty:
        print("⚠️  No posts found matching criteria")
        return
    
    # Prepare output directory
    output_dir = Path(__file__).parent.parent.parent / "data" / "reddit"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save outputs
    csv_file = output_dir / "reddit_posts.csv"
    json_file = output_dir / "reddit_posts.json"
    
    df.to_csv(csv_file, index=False, encoding='utf-8')
    df.to_json(json_file, orient='records', indent=2)
    
    print(f"\n✅ Collection complete!")
    print(f"   Posts collected: {len(df)}")
    print(f"   Subreddits: {df['subreddit'].nunique()}")
    print(f"   Date range: {df['created_utc'].min()} to {df['created_utc'].max()}")
    print(f"   Saved to:")
    print(f"     - {csv_file}")
    print(f"     - {json_file}")


if __name__ == "__main__":
    # Disable HuggingFace tokenizers parallelism warning
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    main()

