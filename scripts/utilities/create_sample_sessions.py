#!/usr/bin/env python3
"""Create 3 sample sessions demonstrating full master scraper integration"""
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "scripts" / "news_api"))

# Create 3 demo sessions (different timestamps)
base_time = datetime.now()
session_times = [
    base_time - timedelta(hours=2),  # 2 hours ago
    base_time - timedelta(hours=1),  # 1 hour ago
    base_time                          # Now
]

master_output = project_root / "data" / "master_output"
master_output.mkdir(exist_ok=True)

for idx, session_time in enumerate(session_times, 1):
    timestamp = session_time.strftime('%Y%m%d_%H%M%S')
    session_dir = master_output / f"session_{timestamp}"
    session_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"Creating Sample Session {idx}/3: {session_dir.name}")
    print(f"{'='*70}")

    file_count = 0

    # 1. NEWS API: Generate visualizations from sample data
    print("➜ News API: Generating visualizations...")
    try:
        from news_viz import Visualizations, PoliticalAnalysisVisualizer
        import pandas as pd
        import json
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        # Load sample data
        sample_dir = project_root / "data" / "news" / "sample"
        with open(sample_dir / "combined_articles.json") as f:
            data = json.load(f)
            combined_articles = data['articles']
        df = pd.read_csv(sample_dir / "classified.csv")

        # Copy data files
        shutil.copy(sample_dir / "combined_articles.json", session_dir / "combined_articles.json")
        shutil.copy(sample_dir / "classified.csv", session_dir / "classified.csv")
        file_count += 2

        # Generate visualizations
        viz = Visualizations(df, 'homelessness')
        summary_df = viz.analyze_sources(combined_articles)
        all_text = ' '.join([article.get('text', '') for article in combined_articles])

        # Word Cloud
        plt.figure(figsize=(12, 6))
        viz.generate_wordcloud(all_text)
        plt.savefig(session_dir / f"news_wordcloud_{timestamp}.png", dpi=100, bbox_inches='tight')
        plt.close()
        file_count += 1

        # Outlet Counts
        plt.figure(figsize=(10, 8))
        viz.plot_comparison_horizontal(summary_df, top_n=25)
        plt.savefig(session_dir / f"news_outlet_counts_{timestamp}.png", dpi=100, bbox_inches='tight')
        plt.close()
        file_count += 1

        # Political Pie
        plt.figure(figsize=(8, 8))
        viz.pie_chart(df)
        plt.savefig(session_dir / f"news_political_pie_{timestamp}.png", dpi=100, bbox_inches='tight')
        plt.close()
        file_count += 1

        # Political Timeline
        poli_viz = PoliticalAnalysisVisualizer()
        plt.figure(figsize=(14, 7))
        poli_viz.political_timeline(df)
        plt.savefig(session_dir / f"news_political_timeline_{timestamp}.png", dpi=100, bbox_inches='tight')
        plt.close()
        file_count += 1

        # Sankey Diagram
        poli_viz.create_interactive_visualizations(df)
        sankey_src = project_root / "scripts" / "news_api" / "sankey_diagram.html"
        if sankey_src.exists():
            shutil.move(str(sankey_src), str(session_dir / f"news_sankey_{timestamp}.html"))
            file_count += 1

        print(f"  ✓ News API: 6 visualizations + 2 data files")
    except Exception as e:
        print(f"  ⚠ News API error: {e}")

    # 2. GOOGLE TRENDS: Copy sample data
    print("➜ Google Trends: Copying data files...")
    gt_data = project_root / "scripts" / "google_trends" / "data python files"
    if gt_data.exists():
        for f in gt_data.glob("*.xlsx"):
            shutil.copy2(f, session_dir / f"gt_{f.name}")
            file_count += 1
        for f in gt_data.glob("googletrends_normalised.csv"):
            shutil.copy2(f, session_dir / f"gt_{f.name}")
            file_count += 1
        print(f"  ✓ Google Trends: {len(list(gt_data.glob('*.xlsx')))} + 1 files")

    # 3. BLUESKY: Copy sample data
    print("➜ Bluesky: Copying sample data...")
    bluesky_sample = project_root / "data" / "bluesky" / "sample"
    if bluesky_sample.exists():
        csv_file = bluesky_sample / "bluesky_sample.csv"
        if csv_file.exists():
            shutil.copy2(csv_file, session_dir / "bluesky_posts.csv")
            file_count += 1
        json_file = bluesky_sample / "bluesky_sample_1000.json"
        if json_file.exists():
            shutil.copy2(json_file, session_dir / "bluesky_posts.json")
            file_count += 1
        print(f"  ✓ Bluesky: 2 data files")

    # 4. REDDIT: Create placeholder (optional)
    print("➜ Reddit: Creating placeholder...")
    reddit_placeholder = session_dir / "reddit_posts.csv"
    reddit_placeholder.write_text("# Reddit data collection placeholder\n# Run master_scraper.py with duration >= 180s for full collection\n")
    file_count += 1
    print(f"  ✓ Reddit: 1 placeholder file")

    print(f"\n✅ Session {idx} complete: {file_count} files")
    print(f"📁 Location: {session_dir}")

print(f"\n{'='*70}")
print(f"✅ ALL DONE: Created 3 sample sessions")
print(f"📂 Location: data/master_output/")
print(f"{'='*70}")
