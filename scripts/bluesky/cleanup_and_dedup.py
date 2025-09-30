#!/usr/bin/env python3
"""
Comprehensive Data Cleanup and Deduplication Script
- Merges all CSV files from alltime_socmed into one deduplicated file
- Cleans up redundant files
- Ensures data integrity
"""

import os
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_and_dedup():
    """Main cleanup and deduplication function"""
    
    # Define paths
    alltime_socmed_dir = Path("../../data/bluesky/alltime_socmed")
    alltime_dir = Path("../../data/bluesky/alltime")
    
    logger.info("🧹 Starting comprehensive data cleanup and deduplication...")
    
    # 1. Collect all CSV files from alltime_socmed
    csv_files = list(alltime_socmed_dir.glob("*.csv"))
    logger.info(f"📊 Found {len(csv_files)} CSV files in alltime_socmed")
    
    if not csv_files:
        logger.warning("❌ No CSV files found in alltime_socmed")
        return
    
    # 2. Load and merge all CSV files
    all_posts = []
    file_stats = {}
    
    for csv_file in csv_files:
        try:
            logger.info(f"📖 Reading {csv_file.name}...")
            df = pd.read_csv(csv_file)
            logger.info(f"   - {len(df)} posts in {csv_file.name}")
            
            # Add source file info
            df['source_file'] = csv_file.name
            all_posts.append(df)
            file_stats[csv_file.name] = len(df)
            
        except Exception as e:
            logger.error(f"❌ Error reading {csv_file.name}: {e}")
            continue
    
    if not all_posts:
        logger.error("❌ No valid CSV files could be read")
        return
    
    # 3. Combine all dataframes
    logger.info("🔗 Combining all data...")
    combined_df = pd.concat(all_posts, ignore_index=True)
    logger.info(f"📊 Total posts before deduplication: {len(combined_df)}")
    
    # 4. Deduplicate based on URI (unique identifier)
    logger.info("🔄 Deduplicating based on URI...")
    original_count = len(combined_df)
    
    # Remove duplicates based on URI, keeping the first occurrence
    deduplicated_df = combined_df.drop_duplicates(subset=['uri'], keep='first')
    final_count = len(deduplicated_df)
    duplicates_removed = original_count - final_count
    
    logger.info(f"✅ Deduplication complete:")
    logger.info(f"   - Original posts: {original_count}")
    logger.info(f"   - Duplicates removed: {duplicates_removed}")
    logger.info(f"   - Final unique posts: {final_count}")
    
    # 5. Sort by created_at (most recent first)
    logger.info("📅 Sorting by creation date...")
    deduplicated_df = deduplicated_df.sort_values('created_at', ascending=False)
    
    # 6. Create clean alltime directory structure
    logger.info("📁 Creating clean alltime directory...")
    alltime_dir.mkdir(exist_ok=True)
    
    # 7. Save the final deduplicated data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save as CSV
    csv_output = alltime_dir / f"alltime_socmed_{timestamp}.csv"
    deduplicated_df.to_csv(csv_output, index=False)
    logger.info(f"💾 Saved deduplicated CSV: {csv_output}")
    
    # Save as JSONL
    jsonl_output = alltime_dir / f"alltime_socmed_{timestamp}.jsonl"
    with open(jsonl_output, 'w', encoding='utf-8') as f:
        for _, row in deduplicated_df.iterrows():
            json.dump(row.to_dict(), f, ensure_ascii=False, default=str)
            f.write('\n')
    logger.info(f"💾 Saved deduplicated JSONL: {jsonl_output}")
    
    # 8. Create summary report
    summary = {
        "cleanup_timestamp": timestamp,
        "original_files": len(csv_files),
        "original_posts": original_count,
        "duplicates_removed": duplicates_removed,
        "final_unique_posts": final_count,
        "deduplication_rate": f"{(duplicates_removed/original_count)*100:.1f}%" if original_count > 0 else "0%",
        "file_stats": file_stats,
        "output_files": {
            "csv": str(csv_output),
            "jsonl": str(jsonl_output)
        }
    }
    
    summary_file = alltime_dir / f"cleanup_summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    logger.info(f"📋 Saved cleanup summary: {summary_file}")
    
    # 9. Clean up old files (keep only the latest deduplicated files)
    logger.info("🗑️ Cleaning up old files...")
    
    # Keep only the latest files
    old_csv_files = [f for f in csv_files if f.name != csv_output.name]
    old_jsonl_files = list(alltime_socmed_dir.glob("*.jsonl"))
    old_md_files = list(alltime_socmed_dir.glob("*.md"))
    old_summary_files = list(alltime_socmed_dir.glob("*_summary.json"))
    
    files_to_remove = old_csv_files + old_jsonl_files + old_md_files + old_summary_files
    
    removed_count = 0
    for file_path in files_to_remove:
        try:
            file_path.unlink()
            removed_count += 1
        except Exception as e:
            logger.warning(f"⚠️ Could not remove {file_path.name}: {e}")
    
    logger.info(f"🗑️ Removed {removed_count} old files")
    
    # 10. Create a symlink to the latest file for easy access
    latest_csv = alltime_socmed_dir / "latest_alltime_socmed.csv"
    latest_jsonl = alltime_socmed_dir / "latest_alltime_socmed.jsonl"
    
    try:
        if latest_csv.exists():
            latest_csv.unlink()
        if latest_jsonl.exists():
            latest_jsonl.unlink()
            
        latest_csv.symlink_to(f"../alltime/{csv_output.name}")
        latest_jsonl.symlink_to(f"../alltime/{jsonl_output.name}")
        logger.info("🔗 Created symlinks to latest files")
    except Exception as e:
        logger.warning(f"⚠️ Could not create symlinks: {e}")
    
    # 11. Final statistics
    logger.info("🎉 Cleanup and deduplication completed!")
    logger.info(f"📊 Final statistics:")
    logger.info(f"   - Unique posts: {final_count:,}")
    logger.info(f"   - Duplicates removed: {duplicates_removed:,}")
    logger.info(f"   - Deduplication rate: {(duplicates_removed/original_count)*100:.1f}%")
    logger.info(f"   - Files cleaned: {removed_count}")
    logger.info(f"   - Latest CSV: {csv_output}")
    logger.info(f"   - Latest JSONL: {jsonl_output}")
    
    return summary

if __name__ == "__main__":
    cleanup_and_dedup()
