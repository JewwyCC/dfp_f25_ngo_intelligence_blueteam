#!/usr/bin/env python3
"""
Clean up sessions directory - keep only recent and meaningful sessions
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_sessions():
    """Clean up sessions directory"""
    
    sessions_dir = Path("data/sessions")
    
    logger.info("🧹 Starting sessions directory cleanup...")
    
    # Sessions to keep (most recent and meaningful)
    sessions_to_keep = [
        "search_45days_20250921_103555",  # Most comprehensive recent session
        "notebook_collection",            # Good collection
        "comprehensive_30min",            # Good test session
        "demo_search_test",               # Demo session
    ]
    
    # Get all session directories
    all_sessions = [d for d in sessions_dir.iterdir() if d.is_dir()]
    logger.info(f"📁 Found {len(all_sessions)} session directories")
    
    # Remove old sessions
    removed_count = 0
    for session_dir in all_sessions:
        if session_dir.name not in sessions_to_keep:
            try:
                # Check if directory has meaningful data
                jsonl_files = list(session_dir.glob("*.jsonl"))
                total_posts = 0
                
                for jsonl_file in jsonl_files:
                    try:
                        with open(jsonl_file, 'r', encoding='utf-8') as f:
                            total_posts += sum(1 for line in f if line.strip())
                    except:
                        pass
                
                # Only remove if it has very few posts or is clearly old
                if total_posts < 50 or session_dir.name.startswith("session_20250918"):
                    logger.info(f"🗑️ Removing {session_dir.name} ({total_posts} posts)")
                    shutil.rmtree(session_dir)
                    removed_count += 1
                else:
                    logger.info(f"📁 Keeping {session_dir.name} ({total_posts} posts)")
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not remove {session_dir.name}: {e}")
    
    logger.info(f"✅ Sessions cleanup completed: {removed_count} directories removed")
    
    # List remaining sessions
    remaining_sessions = [d for d in sessions_dir.iterdir() if d.is_dir()]
    logger.info(f"📁 Remaining sessions: {len(remaining_sessions)}")
    for session in remaining_sessions:
        jsonl_files = list(session.glob("*.jsonl"))
        total_posts = 0
        for jsonl_file in jsonl_files:
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    total_posts += sum(1 for line in f if line.strip())
            except:
                pass
        logger.info(f"   - {session.name}: {total_posts} posts")

if __name__ == "__main__":
    cleanup_sessions()
