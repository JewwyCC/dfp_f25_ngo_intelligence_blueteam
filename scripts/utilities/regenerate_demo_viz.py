#!/usr/bin/env python3
"""
Regenerate Demo Visualizations with Comprehensive Bluesky Data
This script regenerates all visualizations for the demo_session using the comprehensive alltime data
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

def main():
    print("=" * 80)
    print("🎨 REGENERATING DEMO VISUALIZATIONS WITH COMPREHENSIVE DATA")
    print("=" * 80)

    # Paths
    demo_session_path = Path("data/demo_data/demo_session")
    master_output_path = Path("data/master_output")
    temp_session_path = master_output_path / "demo_session"

    if not demo_session_path.exists():
        print(f"❌ Error: Demo session not found at {demo_session_path}")
        return 1

    # Check if comprehensive Bluesky data exists
    bluesky_data = demo_session_path / "raw_data" / "bluesky_homelessness_posts.csv"
    if bluesky_data.exists():
        line_count = sum(1 for _ in open(bluesky_data)) - 1  # Subtract header
        print(f"✓ Found comprehensive Bluesky data: {line_count} posts")
    else:
        print(f"⚠️  Warning: Bluesky data not found at {bluesky_data}")

    try:
        # Step 1: Create temporary symlink or copy to master_output
        print(f"\n📁 Creating temporary session in master_output...")
        master_output_path.mkdir(exist_ok=True)

        if temp_session_path.exists():
            shutil.rmtree(temp_session_path)

        # Copy demo_session to master_output temporarily
        shutil.copytree(demo_session_path, temp_session_path)
        print(f"✓ Copied demo session to {temp_session_path}")

        # Step 2: Run visualization generation
        from master_scraper_viz import VisualizationOrchestrator

        print(f"\n📊 Initializing visualization generation...")
        viz_orchestrator = VisualizationOrchestrator("demo_session")

        # Step 3: Generate visualizations
        print("\n🎨 Generating visualizations...")
        viz_orchestrator.run()

        # Step 4: Copy artifacts back to demo_session
        print(f"\n📦 Copying artifacts back to demo session...")
        temp_artifacts = temp_session_path / "artifacts"
        demo_artifacts = demo_session_path / "artifacts"

        if temp_artifacts.exists():
            # Remove old artifacts
            if demo_artifacts.exists():
                shutil.rmtree(demo_artifacts)

            # Copy new artifacts
            shutil.copytree(temp_artifacts, demo_artifacts)
            print(f"✓ Copied artifacts to {demo_artifacts}")

        # Step 5: Clean up temp session
        print(f"\n🧹 Cleaning up temporary files...")
        shutil.rmtree(temp_session_path)
        print(f"✓ Removed temporary session")

        print("\n" + "=" * 80)
        print("✅ VISUALIZATION GENERATION COMPLETE!")
        print("=" * 80)

        # Show artifacts generated
        if demo_artifacts.exists():
            viz_files = list(demo_artifacts.glob("*.png")) + list(demo_artifacts.glob("*.html"))
            print(f"\n📁 Generated {len(viz_files)} visualization files:")

            # Group by type
            bluesky_viz = [f for f in viz_files if 'bluesky' in f.name.lower()]
            reddit_viz = [f for f in viz_files if 'reddit' in f.name.lower()]
            news_viz = [f for f in viz_files if 'news' in f.name.lower()]
            trends_viz = [f for f in viz_files if 'google_trends' in f.name.lower() or 'googletrends' in f.name.lower()]

            print(f"   🦋 Bluesky: {len(bluesky_viz)} files")
            print(f"   💬 Reddit: {len(reddit_viz)} files")
            print(f"   📰 News: {len(news_viz)} files")
            print(f"   🔍 Google Trends: {len(trends_viz)} files")

            print(f"\n📂 Output directory: {demo_artifacts}")
            print("\n✨ You can now run the Streamlit dashboard to see the updated visualizations!")

        return 0

    except Exception as e:
        print(f"\n❌ Error during visualization generation: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
