#!/usr/bin/env python3
"""
Regenerate News visualizations with updated styling
"""
import pandas as pd
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.append('scripts/news_api')

from news_viz import Visualizations, PoliticalAnalysisVisualizer

def main():
    # Load demo news data
    demo_dir = Path("data/demo_data/demo_session")
    news_csv = demo_dir / "raw_data" / "news_classified.csv"

    if not news_csv.exists():
        print(f"❌ News data not found at {news_csv}")
        return

    print(f"📰 Loading news data from {news_csv}")
    df = pd.read_csv(news_csv)
    print(f"✓ Loaded {len(df)} news articles")

    # Set output directory to demo artifacts
    output_dir = demo_dir / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Update output directory in viz classes
    import scripts.news_api.news_configs as config
    config.OUTPUT_DIRECTORY = str(output_dir)

    # Create visualizations
    print("\n🎨 Generating visualizations...")

    # 1. Political Analysis Timeline
    print("  - Political timeline...")
    pol_viz = PoliticalAnalysisVisualizer()
    pol_viz.output_directory = str(output_dir)
    pol_viz.political_timeline(df)

    # 2. Source comparison bar chart
    print("  - News outlet comparison...")
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

    # 3. Pie chart
    print("  - Political pie chart...")
    viz.pie_chart(df)

    # 4. Word cloud
    print("  - Word cloud...")
    all_text = ' '.join(df['title'].fillna('').astype(str))
    viz.generate_wordcloud(all_text)

    print("\n✅ News visualizations regenerated successfully!")
    print(f"📁 Saved to: {output_dir}")

    # List generated files
    viz_files = list(output_dir.glob("news_*.png")) + list(output_dir.glob("news_*.html"))
    print(f"\n📊 Generated {len(viz_files)} visualizations:")
    for f in sorted(viz_files):
        print(f"  - {f.name}")

if __name__ == "__main__":
    main()
