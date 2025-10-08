#!/usr/bin/env python3
"""
Enrich and deduplicate Bluesky demo data
"""
import pandas as pd
from pathlib import Path

def main():
    print("=" * 60)
    print("🦋 BLUESKY DATA ENRICHMENT & DEDUPLICATION")
    print("=" * 60)

    # Collect all Bluesky CSV files
    bluesky_files = []

    # Check alltime_socmed (largest dataset)
    socmed_dir = Path("data/bluesky/alltime_socmed")
    if socmed_dir.exists():
        socmed_files = list(socmed_dir.glob("socmed_*.csv"))
        bluesky_files.extend(socmed_files)
        print(f"\n📁 Found {len(socmed_files)} files in alltime_socmed/")

    # Check alltime
    alltime_dir = Path("data/bluesky/alltime")
    if alltime_dir.exists():
        alltime_files = list(alltime_dir.glob("*.csv"))
        bluesky_files.extend(alltime_files)
        print(f"📁 Found {len(alltime_files)} files in alltime/")

    # Check sample
    sample_dir = Path("data/bluesky/sample")
    if sample_dir.exists():
        sample_files = list(sample_dir.glob("*.csv"))
        bluesky_files.extend(sample_files)
        print(f"📁 Found {len(sample_files)} files in sample/")

    print(f"\n📊 Total CSV files found: {len(bluesky_files)}")

    # Load and combine all data
    all_posts = []
    total_raw = 0

    for file in bluesky_files:
        try:
            df = pd.read_csv(file)
            total_raw += len(df)
            all_posts.append(df)
            print(f"   ✓ Loaded {len(df):,} posts from {file.name}")
        except Exception as e:
            print(f"   ✗ Error loading {file.name}: {e}")

    if not all_posts:
        print("\n❌ No data loaded")
        return

    print(f"\n📊 Total posts before deduplication: {total_raw:,}")

    # Combine all DataFrames
    combined_df = pd.concat(all_posts, ignore_index=True)

    # Deduplicate by URI (unique post identifier)
    if 'uri' in combined_df.columns:
        before_dedup = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['uri'], keep='first')
        after_dedup = len(combined_df)
        removed = before_dedup - after_dedup
        print(f"🔄 Removed {removed:,} duplicates based on URI")
    elif 'text' in combined_df.columns:
        # Fallback: deduplicate by text content
        before_dedup = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['text'], keep='first')
        after_dedup = len(combined_df)
        removed = before_dedup - after_dedup
        print(f"🔄 Removed {removed:,} duplicates based on text content")

    print(f"✅ Final dataset: {len(combined_df):,} unique posts")

    # Sort by engagement if possible
    engagement_cols = []
    for col in ['like_count', 'repost_count', 'reply_count']:
        if col in combined_df.columns:
            engagement_cols.append(col)

    if engagement_cols:
        combined_df['total_engagement'] = combined_df[engagement_cols].sum(axis=1)
        combined_df = combined_df.sort_values('total_engagement', ascending=False)
        print(f"📈 Sorted by engagement ({', '.join(engagement_cols)})")

    # Save to demo directory
    output_dir = Path("data/demo_data/demo_session/raw_data")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_file = output_dir / "bluesky_homelessness_posts.csv"
    jsonl_file = output_dir / "bluesky_homelessness_posts.jsonl"

    # Remove total_engagement column before saving
    if 'total_engagement' in combined_df.columns:
        combined_df = combined_df.drop(columns=['total_engagement'])

    combined_df.to_csv(csv_file, index=False)
    combined_df.to_json(jsonl_file, orient='records', lines=True)

    print("\n" + "=" * 60)
    print("✅ ENRICHMENT COMPLETE!")
    print("=" * 60)
    print(f"📁 Saved to:")
    print(f"   CSV: {csv_file}")
    print(f"   JSONL: {jsonl_file}")
    print(f"📊 Final count: {len(combined_df):,} unique posts")

    # Show summary stats
    if 'author_handle' in combined_df.columns:
        print(f"\n👤 Top 5 authors:")
        author_counts = combined_df['author_handle'].value_counts().head(5)
        for author, count in author_counts.items():
            print(f"   @{author}: {count} posts")

    if 'created_at' in combined_df.columns:
        combined_df['created_at'] = pd.to_datetime(combined_df['created_at'], errors='coerce')
        print(f"\n📅 Date range:")
        print(f"   Earliest: {combined_df['created_at'].min()}")
        print(f"   Latest: {combined_df['created_at'].max()}")

    # Show engagement stats
    if 'like_count' in combined_df.columns:
        total_likes = combined_df['like_count'].sum()
        avg_likes = combined_df['like_count'].mean()
        max_likes = combined_df['like_count'].max()
        print(f"\n❤️ Engagement stats:")
        print(f"   Total likes: {total_likes:,}")
        print(f"   Avg likes: {avg_likes:.1f}")
        print(f"   Max likes: {max_likes:,}")

if __name__ == "__main__":
    main()
