#!/usr/bin/env python3
"""Generate news visualizations from Kaitlin's sample data"""
import sys
import json
from pathlib import Path
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "scripts" / "news_api"))

# Use sample data
sample_dir = project_root / "data" / "news" / "sample"
combined_json = sample_dir / "combined_articles.json"
classified_csv = sample_dir / "classified.csv"

# Create output directory
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_dir = project_root / "data" / "master_output" / f"session_{timestamp}"
output_dir.mkdir(parents=True, exist_ok=True)

print(f"Generating News API visualizations...")
print(f"Output: {output_dir}")

try:
    from news_viz import Visualizations, PoliticalAnalysisVisualizer
    import shutil

    # Load sample data
    print(f"➜ Loading sample data...")
    with open(combined_json) as f:
        data = json.load(f)
        combined_articles = data['articles']

    df = pd.read_csv(classified_csv)
    print(f"✓ Loaded {len(combined_articles)} articles, {len(df)} classified")

    # Copy data files to output
    shutil.copy(combined_json, output_dir / 'combined_articles.json')
    shutil.copy(classified_csv, output_dir / 'classified.csv')
    print(f"✓ Copied data files")

    left_count = len(df[df['leaning'] == 'LEFT'])
    right_count = len(df[df['leaning'] == 'RIGHT'])
    center_count = len(df[df['leaning'] == 'CENTER'])
    print(f"✓ Classification: LEFT={left_count}, CENTER={center_count}, RIGHT={right_count}")

    # Generate visualizations
    print(f"➜ Generating 5 visualizations...")
    viz = Visualizations(df, 'homelessness')
    summary_df = viz.analyze_sources(combined_articles)

    # Get all text for word cloud
    all_text = ' '.join([article.get('text', '') for article in combined_articles])

    viz_files = []

    # 1. Word Cloud
    plt.figure(figsize=(12, 6))
    wordcloud = viz.generate_wordcloud(all_text)
    viz_path = output_dir / f"news_wordcloud_{timestamp}.png"
    plt.savefig(viz_path, dpi=100, bbox_inches='tight')
    plt.close()
    viz_files.append(viz_path.name)
    print(f"  ✓ 1/5: Word cloud")

    # 2. Outlet Article Count
    plt.figure(figsize=(10, 8))
    viz.plot_comparison_horizontal(summary_df, top_n=25)
    viz_path = output_dir / f"news_outlet_counts_{timestamp}.png"
    plt.savefig(viz_path, dpi=100, bbox_inches='tight')
    plt.close()
    viz_files.append(viz_path.name)
    print(f"  ✓ 2/5: Outlet counts")

    # 3. Political Pie Chart
    plt.figure(figsize=(8, 8))
    viz.pie_chart(df)
    viz_path = output_dir / f"news_political_pie_{timestamp}.png"
    plt.savefig(viz_path, dpi=100, bbox_inches='tight')
    plt.close()
    viz_files.append(viz_path.name)
    print(f"  ✓ 3/5: Political pie chart")

    # 4. Political Timeline
    poli_viz = PoliticalAnalysisVisualizer()
    plt.figure(figsize=(14, 7))
    poli_viz.political_timeline(df)
    viz_path = output_dir / f"news_political_timeline_{timestamp}.png"
    plt.savefig(viz_path, dpi=100, bbox_inches='tight')
    plt.close()
    viz_files.append(viz_path.name)
    print(f"  ✓ 4/5: Political timeline")

    # 5. Sankey Diagram
    poli_viz.create_interactive_visualizations(df)
    sankey_src = project_root / "scripts" / "news_api" / "sankey_diagram.html"
    if sankey_src.exists():
        sankey_dst = output_dir / f"news_sankey_{timestamp}.html"
        shutil.move(str(sankey_src), str(sankey_dst))
        viz_files.append(sankey_dst.name)
        print(f"  ✓ 5/5: Sankey diagram (HTML)")

    print(f"\n✅ SUCCESS: Generated {len(viz_files)} visualizations")
    print(f"📁 Session: {output_dir.name}")
    print(f"\nFiles created:")
    for f in viz_files:
        print(f"  - {f}")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
