#!/usr/bin/env python3
"""
Flask API server for interactive scraper control
Uses port 3000 to avoid AirPlay conflicts
"""

import os
import sys
import json
import subprocess
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global variables for scraper status
scraper_status = {
    'running': False,
    'start_time': None,
    'posts_collected': 0,
    'new_posts': 0,
    'error': None
}

# Global variables for refresh status
refresh_status = {
    'running': False,
    'start_time': None,
    'progress': 0,
    'current_step': '',
    'error': None
}

def run_scraper(duration, keywords='homelessness'):
    """Run the scraper in a separate thread"""
    global scraper_status
    
    try:
        scraper_status['running'] = True
        scraper_status['start_time'] = datetime.now()
        scraper_status['posts_collected'] = 0
        scraper_status['new_posts'] = 0
        scraper_status['error'] = None
        
        # Build command
        cmd = ['python', 'main.py', '--duration', str(duration), '--keywords', keywords]
        
        print(f"Running command: {' '.join(cmd)}")
        
        # Use Popen for real-time output processing
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                 text=True, cwd=os.getcwd(), bufsize=1, universal_newlines=True)
        
        # Process output in real-time
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"Scraper output: {line.strip()}")
                
                # Parse real-time statistics
                if 'Total posts collected:' in line:
                    try:
                        scraper_status['posts_collected'] = int(line.split(':')[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif 'New unique posts:' in line:
                    try:
                        scraper_status['new_posts'] = int(line.split(':')[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif 'Found' in line and 'posts for' in line:
                    try:
                        # Extract number from "Found X posts for 'keyword'"
                        parts = line.split('Found')[1].split('posts')[0].strip()
                        scraper_status['posts_collected'] = int(parts)
                    except (ValueError, IndexError):
                        pass
        
        # Wait for process to complete
        process.wait()
        
        if process.returncode == 0:
            scraper_status['running'] = False
        else:
            scraper_status['error'] = f"Scraper process failed with return code {process.returncode}"
            scraper_status['running'] = False
            
    except Exception as e:
        scraper_status['error'] = str(e)
        scraper_status['running'] = False

@app.route('/')
def serve_html():
    """Serve the interactive HTML report"""
    return send_from_directory('.', 'interactive_eda_report.html')

@app.route('/api/run-scraper', methods=['POST'])
def api_run_scraper():
    """API endpoint to run the scraper"""
    global scraper_status
    
    if scraper_status['running']:
        return jsonify({'error': 'Scraper is already running'}), 400
    
    data = request.get_json()
    duration = data.get('duration', 300)
    keywords = data.get('keywords', 'homelessness')
    
    # Start scraper in background thread
    thread = threading.Thread(
        target=run_scraper,
        args=(duration, keywords)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Scraper started', 'duration': duration})

@app.route('/api/scraper-status', methods=['GET'])
def api_scraper_status():
    """API endpoint to get scraper status"""
    global scraper_status
    
    status = {
        'running': scraper_status['running'],
        'posts_collected': scraper_status['posts_collected'],
        'new_posts': scraper_status['new_posts'],
        'error': scraper_status['error']
    }
    
    if scraper_status['start_time']:
        elapsed = (datetime.now() - scraper_status['start_time']).total_seconds()
        status['elapsed_seconds'] = int(elapsed)
    
    return jsonify(status)

@app.route('/api/refresh-status', methods=['GET'])
def api_refresh_status():
    """API endpoint to get refresh status"""
    global refresh_status
    
    status = {
        'running': refresh_status['running'],
        'progress': refresh_status['progress'],
        'current_step': refresh_status['current_step'],
        'error': refresh_status['error']
    }
    
    if refresh_status['start_time']:
        elapsed = (datetime.now() - refresh_status['start_time']).total_seconds()
        status['elapsed_seconds'] = int(elapsed)
    
    return jsonify(status)

def run_refresh():
    """Run the refresh process in a separate thread with progress tracking"""
    global refresh_status
    
    try:
        refresh_status['running'] = True
        refresh_status['start_time'] = datetime.now()
        refresh_status['progress'] = 0
        refresh_status['current_step'] = 'Starting refresh...'
        refresh_status['error'] = None
        
        # Step 1: Run deduplication script to merge new data into alltime
        refresh_status['current_step'] = 'Deduplicating data...'
        refresh_status['progress'] = 10
        print("🔄 Running deduplication to merge new data...")
        dedup_result = subprocess.run(['python', '-c', '''
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Define paths
alltime_socmed_dir = Path("../../data/bluesky/alltime_socmed")
alltime_dir = Path("../../data/bluesky/alltime")

# Collect all CSV files from alltime_socmed
csv_files = list(alltime_socmed_dir.glob("*.csv"))
print(f"Found {len(csv_files)} CSV files to merge")

if not csv_files:
    print("No CSV files found")
    exit(1)

# Load and merge all CSV files
all_posts = []
for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file)
        df['source_file'] = csv_file.name
        all_posts.append(df)
        print(f"Loaded {len(df)} posts from {csv_file.name}")
    except Exception as e:
        print(f"Error reading {csv_file.name}: {e}")

if not all_posts:
    print("No valid CSV files could be read")
    exit(1)

# Combine all dataframes
combined_df = pd.concat(all_posts, ignore_index=True)
print(f"Total posts before deduplication: {len(combined_df)}")

# Deduplicate based on URI
deduplicated_df = combined_df.drop_duplicates(subset=['uri'], keep='first')
duplicates_removed = len(combined_df) - len(deduplicated_df)
print(f"Duplicates removed: {duplicates_removed}")
print(f"Final unique posts: {len(deduplicated_df)}")

# Sort by created_at (most recent first)
deduplicated_df = deduplicated_df.sort_values('created_at', ascending=False)

# Create clean alltime directory
alltime_dir.mkdir(exist_ok=True)

# Use static filenames and backup old ones
csv_output = alltime_dir / "alltime_socmed.csv"
jsonl_output = alltime_dir / "alltime_socmed.jsonl"
backup_dir = alltime_dir / "backup"

# Create backup directory
backup_dir.mkdir(exist_ok=True)

# Backup existing files if they exist
if csv_output.exists():
    backup_csv = backup_dir / f"alltime_socmed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_output.rename(backup_csv)
    print(f"Backed up old CSV to: {backup_csv}")

if jsonl_output.exists():
    backup_jsonl = backup_dir / f"alltime_socmed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    jsonl_output.rename(backup_jsonl)
    print(f"Backed up old JSONL to: {backup_jsonl}")

# Save the final deduplicated data with static names
deduplicated_df.to_csv(csv_output, index=False)
print(f"Saved deduplicated CSV: {csv_output}")

# Save as JSONL
with open(jsonl_output, 'w', encoding='utf-8') as f:
    for _, row in deduplicated_df.iterrows():
        json.dump(row.to_dict(), f, ensure_ascii=False, default=str)
        f.write('\\n')
print(f"Saved deduplicated JSONL: {jsonl_output}")

# Update the EDA scripts to use the static filename
print("Updating EDA scripts to use static filename...")

# Update improved_eda.py
with open('../../viz/bluesky/improved_eda.py', 'r') as f:
    content = f.read()
# Replace any existing alltime file path with the static one
import re
content = re.sub(r'data_path="../../data/bluesky/alltime_socmed/alltime_socmed(?:_\d{8}_\d{6})?\.csv"',
                'data_path="../../data/bluesky/alltime_socmed/alltime_socmed.csv"', content)
with open('../../viz/bluesky/improved_eda.py', 'w') as f:
    f.write(content)

# Update interactive_eda.py
with open('../../viz/bluesky/interactive_eda.py', 'r') as f:
    content = f.read()
# Replace any existing alltime file path with the static one
content = re.sub(r'data_path="../../data/bluesky/alltime_socmed/alltime_socmed(?:_\d{8}_\d{6})?\.csv"',
                'data_path="../../data/bluesky/alltime_socmed/alltime_socmed.csv"', content)
with open('../../viz/bluesky/interactive_eda.py', 'w') as f:
    f.write(content)

print("✅ Deduplication and file updates completed")
'''], capture_output=True, text=True, cwd=os.getcwd())
        
        if dedup_result.returncode != 0:
            print(f"Deduplication error: {dedup_result.stderr}")
            refresh_status['error'] = f'Deduplication failed: {dedup_result.stderr}'
            refresh_status['running'] = False
            return
        
        print("✅ Deduplication completed successfully")
        refresh_status['progress'] = 50
        refresh_status['current_step'] = 'Regenerating EDA report...'
        
        # Step 2: Regenerate the interactive EDA report
        print("🔄 Regenerating interactive EDA report...")
        eda_result = subprocess.run(['python', 'interactive_eda.py'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
        
        if eda_result.returncode == 0:
            print("✅ Interactive EDA report regenerated successfully")
            refresh_status['progress'] = 100
            refresh_status['current_step'] = 'Refresh completed successfully!'
            refresh_status['running'] = False
        else:
            print(f"EDA regeneration error: {eda_result.stderr}")
            refresh_status['error'] = f'Failed to regenerate EDA: {eda_result.stderr}'
            refresh_status['running'] = False
            
    except Exception as e:
        print(f"Refresh error: {e}")
        refresh_status['error'] = str(e)
        refresh_status['running'] = False

@app.route('/api/refresh-data', methods=['POST'])
def api_refresh_data():
    """API endpoint to refresh data (deduplicate and regenerate EDA report)"""
    global refresh_status
    
    if refresh_status['running']:
        return jsonify({'error': 'Refresh is already running'}), 400
    
    # Start refresh in background thread
    thread = threading.Thread(target=run_refresh)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Refresh started'})

if __name__ == '__main__':
    print("🚀 Starting Interactive Scraper API Server...")
    print("📊 Interactive EDA Report will be available at: http://localhost:3000")
    print("📊 Static EDA Report available at: improved_eda_report.html")
    print("🔧 API endpoints:")
    print("   POST /api/run-scraper - Start scraper")
    print("   GET  /api/scraper-status - Get scraper status")
    print("   POST /api/refresh-data - Refresh data")
    print()
    
    app.run(host='0.0.0.0', port=3000, debug=True)
