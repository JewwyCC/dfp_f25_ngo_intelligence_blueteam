#!/usr/bin/env python3
"""
Quick test version of master scraper with verbose output
"""

import os
import sys
from pathlib import Path

# Color codes
class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

project_root = Path(__file__).parent
scripts_dir = project_root / "scripts"

print(f"{Colors.BOLD}Testing Master Scraper Components{Colors.ENDC}\n")

# Test 1: Check all script files exist
print("1. Checking script files...")
scripts = {
    'Google Trends': scripts_dir / "google_trends" / "googletrends.py",
    'News API': scripts_dir / "news_api" / "NewsAPI_Scrape.py",
    'Reddit': scripts_dir / "reddit" / "data_collection.py",
    'Bluesky': scripts_dir / "bluesky" / "bluesky_social_justice_collector.py"
}

for name, path in scripts.items():
    if path.exists():
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {name}: {path}")
    else:
        print(f"  {Colors.FAIL}✗{Colors.ENDC} {name}: NOT FOUND at {path}")

# Test 2: Check data directories
print("\n2. Checking data directories...")
data_dir = project_root / "data"
for module in ['google_trends', 'news_api', 'reddit', 'bluesky']:
    module_dir = data_dir / module
    if module_dir.exists():
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {module_dir}")
    else:
        print(f"  {Colors.WARNING}!{Colors.ENDC} Creating {module_dir}")
        module_dir.mkdir(parents=True, exist_ok=True)

# Test 3: Check credentials
print("\n3. Checking credentials...")
cred_file = scripts_dir / "news_api" / "credentials.py"
if cred_file.exists():
    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} credentials.py exists")
    try:
        sys.path.insert(0, str(cred_file.parent))
        from credentials import NEWSAPI_KEY, HUGGINGFACE_TOKEN
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} NEWSAPI_KEY: {'*' * 10}{NEWSAPI_KEY[-4:]}")
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} HUGGINGFACE_TOKEN: {'*' * 10}{HUGGINGFACE_TOKEN[-4:]}")
    except Exception as e:
        print(f"  {Colors.FAIL}✗{Colors.ENDC} Error loading credentials: {e}")
else:
    print(f"  {Colors.FAIL}✗{Colors.ENDC} credentials.py not found")

# Test 4: Check Bluesky auth
print("\n4. Checking Bluesky authentication...")
bluesky_auth = project_root / "auth" / "bluesky" / "config" / "auth.json"
if bluesky_auth.exists():
    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Bluesky auth.json exists")
else:
    print(f"  {Colors.WARNING}!{Colors.ENDC} Bluesky auth.json not found at {bluesky_auth}")

# Test 5: Check Reddit config
print("\n5. Checking Reddit configuration...")
reddit_config = scripts_dir / "reddit" / "config.py"
if reddit_config.exists():
    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Reddit config.py exists")
    try:
        sys.path.insert(0, str(reddit_config.parent))
        from config import RedditAuth
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Reddit client_id configured")
    except Exception as e:
        print(f"  {Colors.FAIL}✗{Colors.ENDC} Error loading Reddit config: {e}")
else:
    print(f"  {Colors.FAIL}✗{Colors.ENDC} Reddit config.py not found")

# Test 6: Quick Google Trends keyword check
print("\n6. Checking Google Trends data files...")
trends_data = scripts_dir / "google_trends" / "data python files"
if trends_data.exists():
    keyword_file = trends_data / "keyword_theme.xlsx"
    if keyword_file.exists():
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} keyword_theme.xlsx found")
        try:
            import pandas as pd
            df = pd.read_excel(keyword_file)
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Keywords loaded: {len(df)} rows, {len(df.columns)} columns")
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Sample keywords: {df.iloc[0].tolist()[:3]}")
        except Exception as e:
            print(f"  {Colors.WARNING}!{Colors.ENDC} Could not read keywords: {e}")
    else:
        print(f"  {Colors.FAIL}✗{Colors.ENDC} keyword_theme.xlsx not found")
else:
    print(f"  {Colors.FAIL}✗{Colors.ENDC} Google Trends data directory not found")

print(f"\n{Colors.BOLD}Test complete!{Colors.ENDC}")
print("\nThe main issue is likely Google Trends taking a long time.")
print("Google Trends can take 10-30 minutes to complete due to API rate limits.\n")
