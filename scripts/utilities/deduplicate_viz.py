#!/usr/bin/env python3
"""
Deduplicate Visualizations
Keep only unique visualizations (remove timestamp-based duplicates)
"""

from pathlib import Path
import re

def deduplicate_visualizations():
    artifacts_dir = Path("data/demo_data/demo_session/artifacts")

    if not artifacts_dir.exists():
        print(f"❌ Artifacts directory not found: {artifacts_dir}")
        return

    # Get all visualization files
    viz_files = list(artifacts_dir.glob("*.png")) + list(artifacts_dir.glob("*.html"))

    print(f"📊 Total files: {len(viz_files)}")

    # Group by base name (without timestamp)
    groups = {}

    for viz_file in viz_files:
        # Extract base name (remove timestamp patterns like _20251007_104657 and _demo_session)
        base_name = re.sub(r'_\d{8}_\d{6}', '', viz_file.name)
        base_name = re.sub(r'_demo_session', '', base_name)

        if base_name not in groups:
            groups[base_name] = []
        groups[base_name].append(viz_file)

    # Keep only the newest file from each group
    kept = []
    removed = []

    for base_name, files in groups.items():
        if len(files) > 1:
            # Sort by modification time, keep the newest
            files_sorted = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
            keep_file = files_sorted[0]
            remove_files = files_sorted[1:]

            kept.append(keep_file)
            for f in remove_files:
                f.unlink()
                removed.append(f.name)
        else:
            kept.append(files[0])

    print(f"\n✅ Deduplication complete:")
    print(f"   Kept: {len(kept)} unique visualizations")
    print(f"   Removed: {len(removed)} duplicates")

    if removed:
        print(f"\n🗑️  Removed files:")
        for name in sorted(removed)[:10]:  # Show first 10
            print(f"   - {name}")
        if len(removed) > 10:
            print(f"   ... and {len(removed) - 10} more")

    # Show final counts by type
    final_files = list(artifacts_dir.glob("*.png")) + list(artifacts_dir.glob("*.html"))
    bluesky = [f for f in final_files if 'bluesky' in f.name.lower()]
    reddit = [f for f in final_files if 'reddit' in f.name.lower()]
    news = [f for f in final_files if 'news' in f.name.lower()]
    trends = [f for f in final_files if 'google_trends' in f.name.lower()]

    print(f"\n📁 Final counts:")
    print(f"   🦋 Bluesky: {len(bluesky)} files")
    print(f"   💬 Reddit: {len(reddit)} files")
    print(f"   📰 News: {len(news)} files")
    print(f"   🔍 Google Trends: {len(trends)} files")
    print(f"   Total: {len(final_files)} files")

if __name__ == "__main__":
    deduplicate_visualizations()
