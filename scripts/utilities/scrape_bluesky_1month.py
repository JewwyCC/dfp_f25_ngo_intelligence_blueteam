#!/usr/bin/env python3
"""
Scrape Bluesky data for 1 month range (thousands of posts) for demo data
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts to path
sys.path.append('scripts/bluesky')

from bluesky_social_justice_collector import BlueskyCollector

def main():
    print("=" * 60)
    print("🦋 BLUESKY 1-MONTH DEMO DATA COLLECTION")
    print("=" * 60)

    # Set output directory
    output_dir = Path("data/demo_data/demo_session/raw_data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Calculate date range: last 1 month
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    print(f"\n📅 Date Range:")
    print(f"   Start: {start_date.strftime('%Y-%m-%d')}")
    print(f"   End: {end_date.strftime('%Y-%m-%d')}")
    print(f"   Duration: 30 days (1 month)\n")

    # Keywords for homelessness
    keywords = [
        "homelessness",
        "homeless",
        "housing crisis",
        "affordable housing",
        "unhoused",
        "eviction",
        "shelter",
        "houseless"
    ]

    print(f"🔍 Keywords: {', '.join(keywords)}\n")
    print(f"🎯 Target: 1000+ posts\n")
    print("🚀 Starting collection...\n")

    # Initialize collector
    collector = BlueskyCollector()

    # Collect data for each keyword
    all_posts = []
    for keyword in keywords:
        print(f"   Searching: '{keyword}'...")
        try:
            posts = collector.search_posts(
                query=keyword,
                limit=200,  # 200 per keyword = ~1600 total
                since_date=start_date.strftime('%Y-%m-%d'),
                until_date=end_date.strftime('%Y-%m-%d')
            )
            all_posts.extend(posts)
            print(f"      ✓ Found {len(posts)} posts")
        except Exception as e:
            print(f"      ✗ Error: {e}")

    if all_posts:
        # Remove duplicates based on post URI
        seen_uris = set()
        unique_posts = []
        for post in all_posts:
            uri = post.get('uri', '')
            if uri and uri not in seen_uris:
                seen_uris.add(uri)
                unique_posts.append(post)

        print(f"\n📊 Total unique posts: {len(unique_posts)}")

        # Convert to DataFrame
        import pandas as pd
        df = pd.DataFrame(unique_posts)

        # Save to demo directory
        csv_file = output_dir / "bluesky_homelessness_posts.csv"
        jsonl_file = output_dir / "bluesky_homelessness_posts.jsonl"

        df.to_csv(csv_file, index=False)
        df.to_json(jsonl_file, orient='records', lines=True)

        print("\n" + "=" * 60)
        print("✅ COLLECTION COMPLETE!")
        print("=" * 60)
        print(f"📊 Total posts collected: {len(df)}")
        print(f"📁 Saved to:")
        print(f"   CSV: {csv_file}")
        print(f"   JSONL: {jsonl_file}")

        # Show summary stats
        if 'author_handle' in df.columns:
            print(f"\n👤 Top authors:")
            author_counts = df['author_handle'].value_counts().head(5)
            for author, count in author_counts.items():
                print(f"   @{author}: {count} posts")

        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
            print(f"\n📅 Date range in data:")
            print(f"   Earliest: {df['created_at'].min()}")
            print(f"   Latest: {df['created_at'].max()}")

        # Show engagement stats
        if 'like_count' in df.columns:
            total_likes = df['like_count'].sum()
            avg_likes = df['like_count'].mean()
            print(f"\n❤️ Engagement:")
            print(f"   Total likes: {total_likes}")
            print(f"   Avg likes: {avg_likes:.1f}")

    else:
        print("\n❌ No data collected")

if __name__ == "__main__":
    main()
