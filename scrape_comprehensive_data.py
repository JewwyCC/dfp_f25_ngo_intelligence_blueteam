#!/usr/bin/env python3
"""
Scrape Comprehensive Data for Demo Session
- Bluesky: 5 minutes, last 1 month, aim for thousands of posts
- Reddit: Last 1 year data
"""

import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta

def run_command(cmd, description, timeout=None):
    """Run a command and return success status"""
    print(f"\n{'='*80}")
    print(f"🚀 {description}")
    print(f"{'='*80}")
    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, timeout=timeout, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"\n✅ {description} - SUCCESS")
            return True
        else:
            print(f"\n❌ {description} - FAILED (exit code: {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print(f"\n⏱️ {description} - COMPLETED (timeout reached)")
        return True
    except Exception as e:
        print(f"\n❌ {description} - ERROR: {e}")
        return False

def main():
    print("="*80)
    print("📊 COMPREHENSIVE DATA SCRAPING FOR DEMO SESSION")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    project_root = Path(__file__).parent
    scripts_dir = project_root / "scripts"
    demo_raw_data = project_root / "data" / "demo_data" / "demo_session" / "raw_data"

    # Ensure demo raw_data directory exists
    demo_raw_data.mkdir(parents=True, exist_ok=True)

    # ==================== BLUESKY SCRAPING ====================
    print("\n" + "="*80)
    print("🦋 PHASE 1: BLUESKY COMPREHENSIVE SCRAPING")
    print("="*80)
    print("Target: 1000+ posts from last 30 days")
    print("Duration: 5 minutes")
    print()

    bluesky_script = scripts_dir / "bluesky" / "main.py"

    if bluesky_script.exists():
        # Run for 5 minutes (300 seconds) using both methods for maximum coverage
        bluesky_cmd = [
            sys.executable,
            str(bluesky_script),
            "--method", "both",  # Use both search and firehose
            "--duration", "5",  # 5 minutes
            "--keywords", "all"  # Use all homelessness keywords
        ]

        print("⚠️ Note: Bluesky data will be saved to scripts/bluesky/data/")
        print("We'll move it to demo_session after collection")
        run_command(bluesky_cmd, "Bluesky 5-minute comprehensive scrape", timeout=360)

        # Move the collected data to demo_session
        bluesky_data_dir = scripts_dir / "bluesky" / "data" / "alltime_socmed"
        if bluesky_data_dir.exists():
            import shutil
            for csv_file in bluesky_data_dir.glob("*.csv"):
                # Get the most recent file
                dest_file = demo_raw_data / "bluesky_homelessness_posts.csv"
                shutil.copy2(csv_file, dest_file)
                print(f"✓ Copied {csv_file.name} to demo_session")
                break
    else:
        print(f"⚠️ Bluesky scraper not found at {bluesky_script}")

    # ==================== REDDIT SCRAPING ====================
    print("\n" + "="*80)
    print("💬 PHASE 2: REDDIT COMPREHENSIVE SCRAPING")
    print("="*80)
    print("Target: Last 1 year of data")
    print()

    reddit_script = scripts_dir / "reddit" / "reddit_scraper_cli.py"

    if reddit_script.exists():
        reddit_cmd = [
            sys.executable,
            str(reddit_script)
        ]

        print("⚠️ Note: Reddit data will be saved to data/reddit/")
        print("We'll copy it to demo_session after collection")
        run_command(reddit_cmd, "Reddit comprehensive scrape (1 year data)", timeout=600)

        # Move the collected data to demo_session
        reddit_data_file = project_root / "data" / "reddit" / "reddit_posts.csv"
        if reddit_data_file.exists():
            import shutil
            dest_file = demo_raw_data / "reddit_posts.csv"
            shutil.copy2(reddit_data_file, dest_file)
            print(f"✓ Copied reddit_posts.csv to demo_session")

            # Also copy JSON if exists
            reddit_json_file = project_root / "data" / "reddit" / "reddit_posts.json"
            if reddit_json_file.exists():
                dest_json = demo_raw_data / "reddit_posts.json"
                shutil.copy2(reddit_json_file, dest_json)
                print(f"✓ Copied reddit_posts.json to demo_session")
    else:
        print(f"⚠️ Reddit scraper not found at {reddit_script}")

    # ==================== SUMMARY ====================
    print("\n" + "="*80)
    print("📊 DATA COLLECTION SUMMARY")
    print("="*80)

    # Check what was collected
    bluesky_files = list(demo_raw_data.glob("*bluesky*.csv")) + list(demo_raw_data.glob("*socmed*.csv"))
    reddit_files = list(demo_raw_data.glob("*reddit*.csv"))

    print(f"\n📁 Output directory: {demo_raw_data}")
    print(f"\n🦋 Bluesky files: {len(bluesky_files)}")
    for f in bluesky_files:
        line_count = sum(1 for _ in open(f)) - 1 if f.exists() else 0
        print(f"   - {f.name}: {line_count} posts")

    print(f"\n💬 Reddit files: {len(reddit_files)}")
    for f in reddit_files:
        line_count = sum(1 for _ in open(f)) - 1 if f.exists() else 0
        print(f"   - {f.name}: {line_count} posts")

    print("\n" + "="*80)
    print("✅ DATA SCRAPING COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("1. Run: python3 regenerate_demo_viz.py")
    print("2. Run: streamlit run ngo_dashboard.py")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
