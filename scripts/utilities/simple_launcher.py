#!/usr/bin/env python3
"""
NGO Intelligence Platform - Simple Launcher
==========================================

A lightweight launcher that provides essential functionality without
complex dependencies. This version focuses on the core features that
work reliably.

Usage:
    python simple_launcher.py [mode]
    
Modes:
    - dashboard: Launch Streamlit dashboard
    - data: Run data collection
    - viz: Run visualization
    - help: Show help
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

class SimpleLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        
    def print_banner(self):
        """Print simple banner"""
        print("NGO Intelligence Platform - Simple Launcher")
        print("=" * 50)
    
    def check_basic_deps(self):
        """Check basic dependencies"""
        try:
            import streamlit
            import pandas
            import matplotlib
            print("Core dependencies available")
            return True
        except ImportError as e:
            print(f"Missing dependency: {e}")
            return False
    
    def run_dashboard(self):
        """Launch Streamlit dashboard"""
        print("Launching Streamlit dashboard...")
        try:
            dashboard_path = self.project_root / "ngo_dashboard.py"
            if not dashboard_path.exists():
                print(f"Dashboard not found: {dashboard_path}")
                return False
            
            # Launch Streamlit
            subprocess.run([
                sys.executable, '-m', 'streamlit', 'run', str(dashboard_path),
                '--server.port', '8501',
                '--server.headless', 'false'
            ])
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def run_data_collection(self):
        """Run data collection"""
        print("Running data collection...")
        try:
            data_script = self.project_root / "master_scraper_data.py"
            if not data_script.exists():
                print(f"Data script not found: {data_script}")
                return False
            
            subprocess.run([sys.executable, str(data_script), "--duration", "300"])
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def run_visualization(self):
        """Run visualization"""
        print("Running visualization...")
        try:
            viz_script = self.project_root / "master_scraper_viz.py"
            if not viz_script.exists():
                print(f"Viz script not found: {viz_script}")
                return False
            
            subprocess.run([sys.executable, str(viz_script)])
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def show_help(self):
        """Show help"""
        help_text = """
NGO Intelligence Platform - Simple Launcher

This launcher provides essential functionality for the NGO Intelligence Platform.

AVAILABLE COMMANDS:
  python simple_launcher.py dashboard    - Launch web dashboard
  python simple_launcher.py data        - Run data collection
  python simple_launcher.py viz         - Generate visualizations
  python simple_launcher.py help        - Show this help

FEATURES:
  Interactive Dashboard - Web-based interface
  Data Collection - Google Trends, News, Reddit, Bluesky
  Visualizations - Charts, maps, word clouds
  Easy to Use - Simple command-line interface

DASHBOARD:
  - Launch: python simple_launcher.py dashboard
  - Access: http://localhost:8501
  - Features: Interactive charts, data exploration, session management

DATA COLLECTION:
  - Sources: Google Trends, News API, Reddit, Bluesky
  - Output: Raw data in session directories
  - Duration: Configurable (default 5 minutes)

VISUALIZATION:
  - Input: Raw data from sessions
  - Output: Charts, maps, word clouds
  - Formats: PNG, HTML, interactive plots

REQUIREMENTS:
  - Python 3.8+
  - Streamlit, Pandas, Matplotlib
  - Internet connection for data collection

TROUBLESHOOTING:
  - If dashboard fails: Check if port 8501 is available
  - If data collection fails: Check API credentials
  - If visualization fails: Ensure data exists in sessions

For full functionality, use the complete launcher.py
        """
        print(help_text)
    
    def run(self, mode="help"):
        """Main run method"""
        self.print_banner()
        
        if not self.check_basic_deps():
            print("Please install required dependencies first")
            return False
        
        if mode == "dashboard":
            return self.run_dashboard()
        elif mode == "data":
            return self.run_data_collection()
        elif mode == "viz":
            return self.run_visualization()
        elif mode == "help":
            self.show_help()
            return True
        else:
            print(f"Unknown mode: {mode}")
            self.show_help()
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="NGO Intelligence Platform - Simple Launcher")
    parser.add_argument('mode', nargs='?', default='help', 
                       choices=['dashboard', 'data', 'viz', 'help'],
                       help='Mode to run (default: help)')
    
    args = parser.parse_args()
    
    launcher = SimpleLauncher()
    success = launcher.run(args.mode)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()