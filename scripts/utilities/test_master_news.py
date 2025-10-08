#!/usr/bin/env python3
"""Test master scraper news API integration only"""
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Setup
project_root = Path(__file__).parent
scripts_dir = project_root / "scripts"
master_output_dir = project_root / "data" / "master_output"
master_output_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
session_dir = master_output_dir / f"session_{timestamp}"
session_dir.mkdir(exist_ok=True)

print("="*80)
print("TESTING: Master Scraper News API Integration".center(80))
print("="*80)
print(f"Session: {session_dir.name}\n")

# Test News API module from master_scraper
start = time.time()
print("➜ Running News API with visualizations...")

try:
    # Add News API directory to path
    sys.path.insert(0, str(scripts_dir / "news_api"))

    # Import Kaitlin's modular components
    from combined_news_analyzer import CombinedNewsAnalyzer
    from NewsPoliticalClassifier import PoliticalLeaningClassifier
    from news_viz import Visualizations, PoliticalAnalysisVisualizer
    from credentials import NEWSAPI_KEY
    from news_configs import KEYWORDS_DEFAULT
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    print(f"  ✓ Imports successful")
    print(f"  ➜ Keywords: {', '.join(KEYWORDS_DEFAULT[:5])}...")

    # Initialize combined analyzer (NewsAPI + NPR)
    scraper = CombinedNewsAnalyzer(newsapi_key=NEWSAPI_KEY)

    # Fetch and combine articles from both sources
    print(f"  ➜ Fetching from NewsAPI + NPR...")
    combined_articles = scraper.combine_sources()
    print(f"  ✓ Collected {len(combined_articles)} articles")

    # Save combined articles JSON
    output_file = session_dir / 'combined_articles.json'
    scraper.save_combined_data(str(output_file))
    print(f"  ✓ Saved: combined_articles.json")

    # Classify articles with political leaning
    print(f"  ➜ Classifying political leaning...")
    classifier = PoliticalLeaningClassifier()
    classified_articles = classifier.classify_batch(combined_articles)

    # Convert to DataFrame
    df = pd.DataFrame(classified_articles)
    df.loc[df['source'] == 'section_/sections/news/', 'source'] = 'NPR'

    # Save classified CSV
    csv_file = session_dir / 'classified.csv'
    df.to_csv(csv_file, index=False)
    print(f"  ✓ Saved: classified.csv")

    left_count = len(df[df['leaning'] == 'LEFT'])
    right_count = len(df[df['leaning'] == 'RIGHT'])
    center_count = len(df[df['leaning'] == 'CENTER'])
    print(f"  ✓ Political: LEFT={left_count}, CENTER={center_count}, RIGHT={right_count}")

    # Generate visualizations
    print(f"  ➜ Generating 5 visualizations...")
    viz = Visualizations(df, 'homelessness')
    summary_df = viz.analyze_sources(combined_articles)
    all_text = scraper.all_text(combined_articles)

    viz_files = []

    # 1. Word Cloud
    plt.figure(figsize=(12, 6))
    wordcloud = viz.generate_wordcloud(all_text)
    viz_path = session_dir / f"news_wordcloud_{timestamp}.png"
    plt.savefig(viz_path, dpi=100, bbox_inches='tight')
    plt.close()
    viz_files.append(viz_path.name)
    print(f"    ✓ 1/5: Word cloud")

    # 2. Outlet Article Count
    plt.figure(figsize=(10, 8))
    viz.plot_comparison_horizontal(summary_df, top_n=25)
    viz_path = session_dir / f"news_outlet_counts_{timestamp}.png"
    plt.savefig(viz_path, dpi=100, bbox_inches='tight')
    plt.close()
    viz_files.append(viz_path.name)
    print(f"    ✓ 2/5: Outlet counts")

    # 3. Political Pie Chart
    plt.figure(figsize=(8, 8))
    viz.pie_chart(df)
    viz_path = session_dir / f"news_political_pie_{timestamp}.png"
    plt.savefig(viz_path, dpi=100, bbox_inches='tight')
    plt.close()
    viz_files.append(viz_path.name)
    print(f"    ✓ 3/5: Political pie")

    # 4. Political Timeline
    poli_viz = PoliticalAnalysisVisualizer()
    plt.figure(figsize=(14, 7))
    poli_viz.political_timeline(df)
    viz_path = session_dir / f"news_political_timeline_{timestamp}.png"
    plt.savefig(viz_path, dpi=100, bbox_inches='tight')
    plt.close()
    viz_files.append(viz_path.name)
    print(f"    ✓ 4/5: Political timeline")

    # 5. Sankey Diagram
    poli_viz.create_interactive_visualizations(df)
    sankey_src = scripts_dir / "news_api" / "sankey_diagram.html"
    if sankey_src.exists():
        sankey_dst = session_dir / f"news_sankey_{timestamp}.html"
        import shutil
        shutil.move(str(sankey_src), str(sankey_dst))
        viz_files.append(sankey_dst.name)
        print(f"    ✓ 5/5: Sankey diagram")

    elapsed = time.time() - start
    print(f"\n✅ NEWS API SUCCESS in {elapsed:.1f}s")
    print(f"📊 Articles: {len(combined_articles)}")
    print(f"📁 Visualizations: {len(viz_files)}")
    print(f"📂 Location: {session_dir}")

except Exception as e:
    elapsed = time.time() - start
    print(f"\n❌ FAILED after {elapsed:.1f}s")
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
