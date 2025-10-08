#!/usr/bin/env python3
"""
Regenerate News visualizations with proper matplotlib backend
"""
import sys
import os

# Set matplotlib backend BEFORE any other imports
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pandas as pd
from pathlib import Path

# Add scripts directory to path
sys.path.append('scripts/news_api')

def main():
    print("=" * 60)
    print("📰 NEWS VISUALIZATION REGENERATION")
    print("=" * 60)

    # Import after backend is set
    from news_viz import Visualizations, PoliticalAnalysisVisualizer

    # Load demo news data
    demo_dir = Path("data/demo_data/demo_session")
    news_csv = demo_dir / "raw_data" / "news_classified.csv"

    if not news_csv.exists():
        print(f"❌ News data not found at {news_csv}")
        return

    print(f"\n📰 Loading news data from {news_csv}")
    df = pd.read_csv(news_csv)
    print(f"✅ Loaded {len(df)} news articles")

    # Set output directory to demo artifacts
    output_dir = demo_dir / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Remove old demo_session news files first
    print(f"\n🗑️  Removing old news visualizations...")
    old_files = list(output_dir.glob("news_*demo_session*"))
    for f in old_files:
        f.unlink()
        print(f"   Removed: {f.name}")

    print("\n🎨 Generating NEW visualizations with updated styles...\n")

    # 1. Political Analysis Timeline (LEFT/RIGHT emphasis)
    print("  1️⃣  Political timeline (LEFT/RIGHT emphasized)...")
    try:
        pol_viz = PoliticalAnalysisVisualizer()
        pol_viz.output_directory = str(output_dir)
        pol_viz.political_timeline(df)

        # Rename to demo_session format for consistency
        latest_timeline = sorted(output_dir.glob("news_political_timeline_*.png"))
        if latest_timeline:
            new_name = output_dir / "news_political_timeline_demo_session.png"
            latest_timeline[-1].rename(new_name)
            print(f"      ✅ Saved: {new_name.name}")
    except Exception as e:
        print(f"      ❌ Error: {e}")

    # 2. Source comparison bar chart (with gradient)
    print("\n  2️⃣  News outlet comparison (gradient bars)...")
    try:
        viz = Visualizations(df, keyword="homelessness")
        viz.output_directory = str(output_dir)

        # Prepare articles for analysis
        articles = []
        for _, row in df.iterrows():
            articles.append({
                'source': row.get('source', 'Unknown'),
                'date': row.get('date', ''),
                'title': row.get('title', ''),
                'url': row.get('url', '')
            })

        summary_df = viz.analyze_sources(articles)
        viz.plot_comparison_horizontal(summary_df, top_n=20)

        # Rename to demo_session format
        latest_outlet = sorted(output_dir.glob("news_outlet_comparison_*.png"))
        if latest_outlet:
            new_name = output_dir / "news_outlet_comparison_demo_session.png"
            latest_outlet[-1].rename(new_name)
            print(f"      ✅ Saved: {new_name.name}")
    except Exception as e:
        print(f"      ❌ Error: {e}")

    # 3. Pie chart
    print("\n  3️⃣  Political pie chart...")
    try:
        viz.pie_chart(df)

        # Rename to demo_session format
        latest_pie = sorted(output_dir.glob("news_Proportion*.png"))
        if latest_pie:
            new_name = output_dir / "news_political_pie_demo_session.png"
            latest_pie[-1].rename(new_name)
            print(f"      ✅ Saved: {new_name.name}")
    except Exception as e:
        print(f"      ❌ Error: {e}")

    # 4. Word cloud
    print("\n  4️⃣  Word cloud...")
    try:
        all_text = ' '.join(df['title'].fillna('').astype(str))
        viz.generate_wordcloud(all_text)

        # Rename to demo_session format
        latest_wc = sorted(output_dir.glob("news_Word-Cloud*.png"))
        if latest_wc:
            new_name = output_dir / "news_wordcloud_demo_session.png"
            latest_wc[-1].rename(new_name)
            print(f"      ✅ Saved: {new_name.name}")
    except Exception as e:
        print(f"      ❌ Error: {e}")

    # Clean up any leftover timestamp files
    print("\n🧹 Cleaning up timestamp files...")
    timestamp_files = [f for f in output_dir.glob("news_*.png")
                      if "demo_session" not in f.name]
    for f in timestamp_files:
        f.unlink()
        print(f"   Removed: {f.name}")

    print("\n" + "=" * 60)
    print("✅ NEWS VISUALIZATION REGENERATION COMPLETE!")
    print("=" * 60)

    # List final files
    news_files = sorted(output_dir.glob("news_*demo_session*.png"))
    print(f"\n📊 Generated {len(news_files)} visualizations:")
    for f in news_files:
        size_kb = f.stat().st_size / 1024
        print(f"   ✓ {f.name} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main()
