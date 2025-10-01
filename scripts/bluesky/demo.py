#!/usr/bin/env python3
"""
Easy Demo Script for Bluesky Social Justice Data Collector
DFP F25 Social Media Blue Team

This script provides easy demo options for testing the collector.
"""

import subprocess
import sys
import time
from pathlib import Path

def run_demo():
    """Run interactive demo"""
    print("🎯 Bluesky Social Justice Data Collector - Easy Demo")
    print("=" * 60)
    
    # Check if auth file exists
    auth_file = Path("../../auth/bluesky/config/auth.json")
    if not auth_file.exists():
        print("❌ Authentication file not found!")
        print("Please create auth/bluesky/config/auth.json with your Bluesky credentials:")
        print("""
{
  "bluesky": {
    "username": "your_username.bsky.social",
    "password": "your_app_password"
  }
}
        """)
        return
    
    print("✅ Authentication file found")
    print("\nChoose a demo option:")
    print("1. 🚀 Quick Test (60 seconds, homelessness keywords)")
    print("2. 📊 Standard Demo (300 seconds, all keywords)")
    print("3. 🔬 Extended Demo (900 seconds, all keywords)")
    print("4. 🎯 Custom Demo (you choose duration and keywords)")
    print("5. ❌ Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                print("\n🚀 Running Quick Test (60 seconds)...")
                subprocess.run([sys.executable, "main.py", "--duration", "60", "--keywords", "homelessness"])
                break
                
            elif choice == "2":
                print("\n📊 Running Standard Demo (300 seconds)...")
                subprocess.run([sys.executable, "main.py", "--duration", "300", "--keywords", "all"])
                break
                
            elif choice == "3":
                print("\n🔬 Running Extended Demo (900 seconds)...")
                subprocess.run([sys.executable, "main.py", "--duration", "900", "--keywords", "all", "--no-sleep"])
                break
                
            elif choice == "4":
                duration = input("Enter duration in seconds (60-3600): ").strip()
                print("\nKeyword options:")
                print("  - 'homelessness' - Default homelessness keywords")
                print("  - 'all' - All available keywords")
                print("  - 'custom' - Use keywords.txt file")
                keywords = input("Enter keyword option: ").strip()
                
                cmd = [sys.executable, "main.py", "--duration", duration, "--keywords", keywords]
                if int(duration) > 600:  # 10 minutes
                    cmd.append("--no-sleep")
                
                print(f"\n🎯 Running Custom Demo ({duration} seconds, {keywords} keywords)...")
                subprocess.run(cmd)
                break
                
            elif choice == "5":
                print("👋 Goodbye!")
                return
                
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Demo cancelled by user")
            return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
    
    print("\n✅ Demo completed!")
    print("\n📁 Check your results:")
    print("  - Data files: ../../data/bluesky/alltime_socmed/")
    print("  - Collection reports: ../../data/bluesky/alltime_socmed/COLLECTION_REPORT_*.md")
    print("  - Analysis: jupyter notebook analysis_demo.ipynb")

if __name__ == "__main__":
    run_demo()
