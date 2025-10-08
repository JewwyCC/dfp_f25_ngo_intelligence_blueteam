#!/usr/bin/env python3
"""
Scrape Reddit data for 1 year range for demo data
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts/reddit to path
sys.path.append('scripts/reddit')

from data_collection import collect_by_search
from reddit_client import create_reddit_client

def main():
    print("=" * 60)
    print("📊 REDDIT 1-YEAR DEMO DATA COLLECTION")
    print("=" * 60)

    # Set output directory
    output_dir = Path("data/demo_data/demo_session/raw_data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Calculate date range: last 1 year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    print(f"\n📅 Date Range:")
    print(f"   Start: {start_date.strftime('%Y-%m-%d')}")
    print(f"   End: {end_date.strftime('%Y-%m-%d')}")
    print(f"   Duration: 365 days (1 year)\n")

    # Keywords for homelessness
    keywords = [
        "homelessness",
        "homeless crisis",
        "housing crisis",
        "affordable housing",
        "eviction",
        "unhoused"
    ]

    print(f"🔍 Keywords: {', '.join(keywords)}\n")

    # Subreddits to search
    subreddits = [
        "homeless",
        "Homelessness",
        "housingcrisis",
        "LateStageCapitalism",
        "povertyfinance",
        "almosthomeless",
        "vagabond"
    ]

    print(f"📱 Subreddits: {', '.join(subreddits)}\n")
    print("🚀 Starting collection...\n")

    # Create Reddit client
    print("📡 Connecting to Reddit API...")
    reddit = create_reddit_client()

    # Collect data
    result_df = collect_by_search(
        reddit=reddit,
        subreddits=subreddits,
        keywords=keywords,
        posts_per_sub=1000,  # Aim for large dataset
        time_filter="year",
        strategy="relevance"
    )

    if result_df is not None and not result_df.empty:
        # Save to demo directory
        output_file = output_dir / "reddit_posts.csv"
        result_df.to_csv(output_file, index=False)

        # Also save as JSON
        json_file = output_dir / "reddit_posts.json"
        result_df.to_json(json_file, orient='records', indent=2)

        print("\n" + "=" * 60)
        print("✅ COLLECTION COMPLETE!")
        print("=" * 60)
        print(f"📊 Total posts collected: {len(result_df)}")
        print(f"📁 Saved to:")
        print(f"   CSV: {output_file}")
        print(f"   JSON: {json_file}")

        # Show summary stats
        if 'subreddit' in result_df.columns:
            print(f"\n📱 Subreddit breakdown:")
            sub_counts = result_df['subreddit'].value_counts().head(10)
            for sub, count in sub_counts.items():
                print(f"   r/{sub}: {count} posts")

        if 'created_utc' in result_df.columns:
            result_df['created_utc'] = pd.to_datetime(result_df['created_utc'])
            print(f"\n📅 Date range in data:")
            print(f"   Earliest: {result_df['created_utc'].min()}")
            print(f"   Latest: {result_df['created_utc'].max()}")

    else:
        print("\n❌ No data collected")

if __name__ == "__main__":
    import pandas as pd
    main()
