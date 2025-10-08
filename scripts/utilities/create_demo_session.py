#!/usr/bin/env python3
"""Create a comprehensive demo session with all module outputs"""
import shutil
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Create demo session
demo_session = project_root / "data" / "master_output" / f"session_{timestamp}_demo"
demo_session.mkdir(parents=True, exist_ok=True)

print(f"Creating comprehensive demo session: {demo_session.name}")

# 1. Copy News API outputs (already working)
news_session = project_root / "data" / "master_output" / "session_20251006_111322"
if news_session.exists():
    for f in news_session.glob("*"):
        if f.is_file():
            shutil.copy2(f, demo_session / f.name)
    print(f"✓ Copied {len(list(news_session.glob('*')))} News API files")

# 2. Copy Google Trends sample data
gt_data = project_root / "scripts" / "google_trends" / "data python files"
if gt_data.exists():
    for f in gt_data.glob("*.xlsx"):
        shutil.copy2(f, demo_session / f"gt_{f.name}")
    for f in gt_data.glob("*.csv"):
        shutil.copy2(f, demo_session / f"gt_{f.name}")
    print(f"✓ Copied Google Trends data files")

# 3. Copy Google Trends visualizations (if available)
gt_viz = project_root / "viz" / "google_trends"
if gt_viz.exists():
    viz_count = 0
    for f in gt_viz.glob("*.png"):
        shutil.copy2(f, demo_session / f"gt_viz_{f.name}")
        viz_count += 1
    for f in gt_viz.glob("*.html"):
        shutil.copy2(f, demo_session / f"gt_viz_{f.name}")
        viz_count += 1
    if viz_count > 0:
        print(f"✓ Copied {viz_count} Google Trends visualizations")

# 4. Copy Bluesky sample data
bluesky_sample = project_root / "data" / "bluesky" / "sample"
if bluesky_sample.exists():
    for f in bluesky_sample.glob("bluesky_sample*.csv"):
        shutil.copy2(f, demo_session / "bluesky_posts.csv")
        print(f"✓ Copied Bluesky sample CSV")
        break
    for f in bluesky_sample.glob("bluesky_sample*.json"):
        shutil.copy2(f, demo_session / "bluesky_posts.json")
        print(f"✓ Copied Bluesky sample JSON")
        break

print(f"\n✅ Demo session created!")
print(f"📁 Location: {demo_session}")
print(f"📊 Files: {len(list(demo_session.glob('*')))}")
