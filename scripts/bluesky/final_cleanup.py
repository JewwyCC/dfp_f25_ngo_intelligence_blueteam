#!/usr/bin/env python3
"""
Final cleanup script - remove redundant files and ensure clean directory structure
"""

import os
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def final_cleanup():
    """Final cleanup of the project directory"""
    
    logger.info("🧹 Starting final project cleanup...")
    
    # Files and directories to remove
    files_to_remove = [
        "cleanup_and_dedup.py",
        "cleanup_sessions.py", 
        "final_cleanup.py",
        "bluesky_social_justice_analysis.ipynb",  # Old notebook
        "polarization_analyzer.py",  # Not used
        "web_viewer.py",  # Old web viewer
        "WEB_VIEWER.md",  # Old documentation
    ]
    
    # Remove files
    removed_files = 0
    for file_path in files_to_remove:
        if Path(file_path).exists():
            try:
                Path(file_path).unlink()
                logger.info(f"🗑️ Removed {file_path}")
                removed_files += 1
            except Exception as e:
                logger.warning(f"⚠️ Could not remove {file_path}: {e}")
    
    # Clean up __pycache__ directories
    pycache_dirs = list(Path(".").rglob("__pycache__"))
    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir)
            logger.info(f"🗑️ Removed {pycache_dir}")
            removed_files += 1
        except Exception as e:
            logger.warning(f"⚠️ Could not remove {pycache_dir}: {e}")
    
    # Clean up .pyc files
    pyc_files = list(Path(".").rglob("*.pyc"))
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
            logger.info(f"🗑️ Removed {pyc_file}")
            removed_files += 1
        except Exception as e:
            logger.warning(f"⚠️ Could not remove {pyc_file}: {e}")
    
    # Ensure data directory structure is clean
    data_dir = Path("data")
    alltime_dir = data_dir / "alltime"
    alltime_socmed_dir = data_dir / "alltime_socmed"
    
    # Create .gitkeep files for empty directories
    for dir_path in [alltime_dir, alltime_socmed_dir]:
        if not any(dir_path.iterdir()):
            (dir_path / ".gitkeep").touch()
            logger.info(f"📁 Created .gitkeep in {dir_path}")
    
    # Final directory structure check
    logger.info("📁 Final directory structure:")
    for item in sorted(Path(".").iterdir()):
        if item.is_file() and not item.name.startswith('.'):
            logger.info(f"   📄 {item.name}")
        elif item.is_dir() and item.name not in ['.git', '__pycache__']:
            logger.info(f"   📁 {item.name}/")
    
    logger.info(f"✅ Final cleanup completed: {removed_files} files/directories removed")
    
    # Show final data statistics
    if alltime_dir.exists():
        csv_files = list(alltime_dir.glob("*.csv"))
        jsonl_files = list(alltime_dir.glob("*.jsonl"))
        logger.info(f"📊 Final data statistics:")
        logger.info(f"   - CSV files: {len(csv_files)}")
        logger.info(f"   - JSONL files: {len(jsonl_files)}")
        
        if csv_files:
            latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)
            logger.info(f"   - Latest CSV: {latest_csv.name}")
            
            # Count posts in latest CSV
            try:
                import pandas as pd
                df = pd.read_csv(latest_csv)
                logger.info(f"   - Total unique posts: {len(df):,}")
            except Exception as e:
                logger.warning(f"   - Could not count posts: {e}")

if __name__ == "__main__":
    final_cleanup()
