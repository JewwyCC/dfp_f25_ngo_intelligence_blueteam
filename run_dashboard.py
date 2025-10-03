#!/usr/bin/env python3
"""
NGO Dashboard Launcher
Simple script to launch the NGO Intelligence Dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the NGO dashboard using Streamlit"""
    dashboard_path = os.path.join(os.path.dirname(__file__), 'ngo_dashboard.py')
    
    print("🏠 Launching NGO Intelligence Dashboard...")
    print("📊 Dashboard will open in your default web browser")
    print("🔗 If it doesn't open automatically, navigate to: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print("-" * 60)
    
    try:
        # Run the dashboard
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', dashboard_path,
            '--server.port', '8501',
            '--server.headless', 'false',
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thank you for using NGO Intelligence Dashboard!")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()
