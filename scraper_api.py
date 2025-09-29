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

def run_scraper(duration, date_from=None, date_to=None, keywords='homelessness'):
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
        
        if date_from:
            cmd.extend(['--date-from', date_from])
        if date_to:
            cmd.extend(['--date-to', date_to])
        
        print(f"Running command: {' '.join(cmd)}")
        
        # Run the scraper
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            # Parse output for statistics
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'Total posts collected:' in line:
                    try:
                        scraper_status['posts_collected'] = int(line.split(':')[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif 'New posts added:' in line:
                    try:
                        scraper_status['new_posts'] = int(line.split(':')[1].strip())
                    except (ValueError, IndexError):
                        pass
            
            scraper_status['running'] = False
        else:
            # Show only last few lines of error
            error_lines = result.stderr.strip().split('\n')
            if len(error_lines) > 5:
                scraper_status['error'] = '\n'.join(error_lines[-5:])
            else:
                scraper_status['error'] = result.stderr
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
    date_from = data.get('dateFrom')
    date_to = data.get('dateTo')
    keywords = data.get('keywords', 'homelessness')
    
    # Start scraper in background thread
    thread = threading.Thread(
        target=run_scraper,
        args=(duration, date_from, date_to, keywords)
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

@app.route('/api/refresh-data', methods=['POST'])
def api_refresh_data():
    """API endpoint to refresh data (regenerate EDA report)"""
    try:
        # Run the interactive EDA script to regenerate the report
        result = subprocess.run(['python', 'interactive_eda.py'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return jsonify({'message': 'Data refreshed successfully'})
        else:
            return jsonify({'error': f'Failed to refresh data: {result.stderr}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
