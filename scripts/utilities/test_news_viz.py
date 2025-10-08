#!/usr/bin/env python3
"""Quick test of Kaitlin's news API with visualizations"""
import sys
import os
from pathlib import Path
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "scripts" / "news_api"))

# Create test output directory
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_dir = project_root / "data" / "master_output" / f"session_{timestamp}"
output_dir.mkdir(parents=True, exist_ok=True)

print(f"Testing News API with visualizations...")
print(f"Output: {output_dir}")

try:
    # Import Kaitlin's modules
    from combined_news_analyzer import CombinedNewsAnalyzer
    from NewsPoliticalClassifier import PoliticalLeaningClassifier
    from news_viz import Visualizations, PoliticalAnalysisVisualizer
    from credentials import NEWSAPI_KEY
    from news_configs import KEYWORDS_DEFAULT
    import pandas as pd

    print(f"✓ Imports successful")

    # Fetch articles
    print(f"➜ Fetching articles from NewsAPI + NPR...")
    scraper = CombinedNewsAnalyzer(newsapi_key=NEWSAPI_KEY)
    combined_articles = scraper.combine_sources()
    print(f"✓ Collected {len(combined_articles)} articles")

    # Save combined articles
    output_file = output_dir / 'combined_articles.json'
    scraper.save_combined_data(str(output_file))
    print(f"✓ Saved: {output_file}")

    # Classify
    print(f"➜ Classifying political leaning...")
    classifier = PoliticalLeaningClassifier()
    classified_articles = classifier.classify_batch(combined_articles)

    df = pd.DataFrame(classified_articles)
    df.loc[df['source'] == 'section_/sections/news/', 'source'] = 'NPR'

    csv_file = output_dir / 'classified.csv'
    df.to_csv(csv_file, index=False)
    print(f"✓ Saved: {csv_file}")

    left_count = len(df[df['leaning'] == 'LEFT'])
    right_count = len(df[df['leaning'] == 'RIGHT'])
    center_count = len(df[df['leaning'] == 'CENTER'])
    print(f"✓ Classification: LEFT={left_count}, CENTER={center_count}, RIGHT={right_count}")

    # Generate visualizations
    print(f"➜ Generating visualizations...")
    viz = Visualizations(df, 'homelessness')
    summary_df = viz.analyze_sources(combined_articles)
    all_text = scraper.all_text(combined_articles)

    viz_files = []

    # 1. Word Cloud
    plt.figure(figsize=(12, 6))
    wordcloud = viz.generate_wordcloud(all_text)
    viz_path = output_dir / f"news_wordcloud_{timestamp}.png"
    plt.savefig(viz_path, dpi=100, bbox_inches='tight')
    plt.close()
    viz_files.append(viz_path)
    print(f"  ✓ Word cloud")

    # 2. Outlet Article Count
    plt.figure(figsize=(10, 8))
    viz.plot_comparison_horizontal(summary_df, top_n=25)
    viz_path = output_dir / f"news_outlet_counts_{timestamp}.png"
    plt.savefig(viz_path, dpi=100, bbox_inches='tight')
    plt.close()
    viz_files.append(viz_path)
    print(f"  ✓ Outlet counts")

    # 3. Political Pie Chart
    plt.figure(figsize=(8, 8))
    viz.pie_chart(df)
    viz_path = output_dir / f"news_political_pie_{timestamp}.png"
    plt.savefig(viz_path, dpi=100, bbox_inches='tight')
    plt.close()
    viz_files.append(viz_path)
    print(f"  ✓ Political pie")

    # 4. Political Timeline
    poli_viz = PoliticalAnalysisVisualizer()
    plt.figure(figsize=(14, 7))
    poli_viz.political_timeline(df)
    viz_path = output_dir / f"news_political_timeline_{timestamp}.png"
    plt.savefig(viz_path, dpi=100, bbox_inches='tight')
    plt.close()
    viz_files.append(viz_path)
    print(f"  ✓ Political timeline")

    # 5. Sankey Diagram
    poli_viz.create_interactive_visualizations(df)
    sankey_src = project_root / "scripts" / "news_api" / "sankey_diagram.html"
    if sankey_src.exists():
        sankey_dst = output_dir / f"news_sankey_{timestamp}.html"
        import shutil
        shutil.move(str(sankey_src), str(sankey_dst))
        viz_files.append(sankey_dst)
        print(f"  ✓ Sankey diagram")

    print(f"\n✅ SUCCESS: Generated {len(viz_files)} visualizations")
    print(f"📁 Location: {output_dir}")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
