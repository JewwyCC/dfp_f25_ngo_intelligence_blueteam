#!/usr/bin/env python3
"""
NGO Intelligence Platform - All-in-One Launcher
===============================================

This launcher provides a unified interface for all platform functionality:
- Master Data Collection
- Visualization Generation  
- Interactive Dashboard
- Desktop GUIs
- Configuration Management

Usage:
    python launcher.py [--mode MODE] [--duration SECONDS] [--session SESSION_ID]
    
Modes:
    - data: Run data collection only
    - viz: Run visualization generation only
    - dashboard: Launch Streamlit dashboard
    - gui: Launch desktop GUIs
    - full: Run complete pipeline (data + viz)
    - help: Show this help message

Examples:
    python launcher.py --mode full --duration 600
    python launcher.py --mode dashboard
    python launcher.py --mode viz --session session_20251006_175651
"""

import os
import sys
import argparse
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class NGOPlatformLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.master_output_dir = self.data_dir / "master_output"
        
        # Ensure directories exist
        self.master_output_dir.mkdir(parents=True, exist_ok=True)
        
    def print_banner(self):
        """Print the platform banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🏛️  NGO Intelligence Platform  🏛️                      ║
║                           All-in-One Launcher                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  📊 Data Collection  |  📈 Visualizations  |  🖥️  Dashboard  |  ⚙️  Tools    ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def check_dependencies(self):
        """Check if all required modules are available"""
        try:
            import pandas
            import streamlit
            import matplotlib
            import plotly
            import torch
            import transformers
            print("✅ All core dependencies available")
            return True
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            return False
    
    def run_data_collection(self, duration=600):
        """Run master data collection"""
        print(f"\n🔍 Starting data collection (duration: {duration}s)...")
        try:
            # Import and run master scraper data
            sys.path.insert(0, str(self.project_root))
            from master_scraper_data import MasterScraperData
            
            scraper = MasterScraperData(duration=duration)
            result = scraper.run()
            
            if result:
                print("✅ Data collection completed successfully!")
                return True
            else:
                print("❌ Data collection failed!")
                return False
                
        except Exception as e:
            print(f"❌ Error during data collection: {e}")
            return False
    
    def run_visualization(self, session_id=None):
        """Run visualization generation"""
        if not session_id:
            # Find the most recent session
            sessions = list(self.master_output_dir.glob("session_*"))
            if not sessions:
                print("❌ No sessions found! Run data collection first.")
                return False
            
            # Get the most recent session
            session_id = max(sessions, key=lambda x: x.stat().st_mtime).name
            print(f"📊 Using most recent session: {session_id}")
        
        print(f"\n📊 Starting visualization generation for {session_id}...")
        try:
            # Import and run master scraper viz
            sys.path.insert(0, str(self.project_root))
            from master_scraper_viz import MasterScraperViz
            
            viz = MasterScraperViz(session_id=session_id)
            result = viz.run()
            
            if result:
                print("✅ Visualization generation completed successfully!")
                return True
            else:
                print("❌ Visualization generation failed!")
                return False
                
        except Exception as e:
            print(f"❌ Error during visualization generation: {e}")
            return False
    
    def run_dashboard(self):
        """Launch Streamlit dashboard"""
        print("\n🖥️  Launching Streamlit dashboard...")
        try:
            dashboard_path = self.project_root / "ngo_dashboard.py"
            if not dashboard_path.exists():
                print(f"❌ Dashboard file not found: {dashboard_path}")
                return False
            
            # Launch Streamlit
            subprocess.run([
                sys.executable, '-m', 'streamlit', 'run', str(dashboard_path),
                '--server.port', '8501',
                '--server.headless', 'false',
                '--browser.gatherUsageStats', 'false'
            ])
            return True
            
        except Exception as e:
            print(f"❌ Error launching dashboard: {e}")
            return False
    
    def run_desktop_gui(self):
        """Launch desktop GUIs"""
        print("\n🖥️  Launching desktop GUIs...")
        try:
            # Launch various desktop GUIs
            gui_files = [
                "scripts/bluesky/gui.py",
                "scripts/reddit/gui.py", 
                "scripts/news_api/gui.py"
            ]
            
            for gui_file in gui_files:
                gui_path = self.project_root / gui_file
                if gui_path.exists():
                    print(f"🚀 Launching {gui_file}...")
                    subprocess.Popen([sys.executable, str(gui_path)])
                    time.sleep(2)  # Give time between launches
            
            return True
            
        except Exception as e:
            print(f"❌ Error launching desktop GUIs: {e}")
            return False
    
    def run_full_pipeline(self, duration=600):
        """Run complete pipeline: data collection + visualization"""
        print(f"\n🚀 Starting full pipeline (duration: {duration}s)...")
        
        # Step 1: Data Collection
        if not self.run_data_collection(duration):
            return False
        
        # Step 2: Visualization
        if not self.run_visualization():
            return False
        
        print("🎉 Full pipeline completed successfully!")
        return True
    
    def show_help(self):
        """Show help information"""
        help_text = """
📚 NGO Intelligence Platform - Usage Guide

MODES:
  data       Run data collection from all sources (Google Trends, News, Reddit, Bluesky)
  viz        Generate visualizations from collected data
  dashboard  Launch interactive Streamlit dashboard
  gui        Launch desktop GUI applications
  full       Run complete pipeline (data collection + visualization)
  help       Show this help message

OPTIONS:
  --duration SECONDS    Duration for data collection (default: 600)
  --session SESSION_ID  Specific session ID for visualization (optional)

EXAMPLES:
  python launcher.py --mode full --duration 300
  python launcher.py --mode dashboard
  python launcher.py --mode viz --session session_20251006_175651
  python launcher.py --mode data --duration 900

DATA SOURCES:
  📊 Google Trends    - Search volume trends and geographic data
  📰 News API         - Political news articles and analysis
  🔴 Reddit          - Social media posts and sentiment analysis
  🐦 Bluesky         - Social media posts and engagement metrics

OUTPUTS:
  📁 data/master_output/session_*/raw_data/     - Raw collected data
  📁 data/master_output/session_*/artifacts/    - Generated visualizations
  🖥️  http://localhost:8501                     - Interactive dashboard

TROUBLESHOOTING:
  - If data collection fails, check API credentials in auth/ directory
  - If visualization fails, ensure raw data exists in session directory
  - If dashboard fails, check if port 8501 is available
  - For GUI issues, ensure tkinter is installed (usually built-in)

For more help, see the documentation files in the project root.
        """
        print(help_text)
    
    def list_sessions(self):
        """List available sessions"""
        sessions = list(self.master_output_dir.glob("session_*"))
        if not sessions:
            print("📂 No sessions found.")
            return []
        
        print(f"\n📂 Available sessions ({len(sessions)}):")
        for session in sorted(sessions, key=lambda x: x.stat().st_mtime, reverse=True):
            artifacts_count = len(list((session / "artifacts").glob("*")) if (session / "artifacts").exists() else [])
            raw_data_count = len(list((session / "raw_data").glob("*")) if (session / "raw_data").exists() else [])
            print(f"  📊 {session.name}")
            print(f"     Raw Data: {raw_data_count} files, Artifacts: {artifacts_count} files")
        
        return sessions
    
    def run(self, mode=None, duration=600, session_id=None):
        """Main run method"""
        self.print_banner()
        
        if not self.check_dependencies():
            print("❌ Please install missing dependencies first.")
            return False
        
        if mode == "data":
            return self.run_data_collection(duration)
        elif mode == "viz":
            return self.run_visualization(session_id)
        elif mode == "dashboard":
            return self.run_dashboard()
        elif mode == "gui":
            return self.run_desktop_gui()
        elif mode == "full":
            return self.run_full_pipeline(duration)
        elif mode == "help":
            self.show_help()
            return True
        elif mode == "sessions":
            self.list_sessions()
            return True
        else:
            print("❌ Invalid mode. Use --mode help for usage information.")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="NGO Intelligence Platform - All-in-One Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py --mode full --duration 300
  python launcher.py --mode dashboard
  python launcher.py --mode viz --session session_20251006_175651
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['data', 'viz', 'dashboard', 'gui', 'full', 'help', 'sessions'],
        default='help',
        help='Mode to run (default: help)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=600,
        help='Duration for data collection in seconds (default: 600)'
    )
    
    parser.add_argument(
        '--session',
        type=str,
        help='Session ID for visualization mode (optional)'
    )
    
    args = parser.parse_args()
    
    # Create and run launcher
    launcher = NGOPlatformLauncher()
    success = launcher.run(
        mode=args.mode,
        duration=args.duration,
        session_id=args.session
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
