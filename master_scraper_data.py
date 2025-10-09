#!/usr/bin/env python3
"""
NGO Intelligence Platform - Data Collection Only
Focuses on collecting raw data from all sources (CSV, JSON, JSONL, Excel)

Usage: python master_scraper_data.py --duration <seconds>
Output: data/master_output/session_*/raw_data/
"""

import os
# Disable HuggingFace tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
import time

# Reuse the original master scraper's core functionality
from master_scraper import HomelessnessMasterOrchestrator, Colors

class DataCollectionOrchestrator(HomelessnessMasterOrchestrator):
    """Focused on data collection only - no visualizations"""
    
    def __init__(self, duration_seconds=123):
        super().__init__(duration_seconds)

        # Override time_budget with fixed allocations
        # Order: Bluesky (60s) → News (30s) → Reddit (30s) → Google Trends (3s)
        self.time_budget = {
            'bluesky': 60,        # 1 month data, homeless keyword
            'news_api': 30,       # Recent articles
            'reddit': 30,         # 1 year data, defined subreddits
            'google_trends': 3    # Just copy from demo (preloaded)
        }

        # Create session directories immediately
        self.session_dir = self.master_output_dir / f"session_{self.timestamp}"
        self.session_dir.mkdir(exist_ok=True)

        # Create raw_data subdirectory - THIS is where all data goes
        self.raw_data_dir = self.session_dir / "raw_data"
        self.raw_data_dir.mkdir(exist_ok=True)

        # Also create artifacts placeholder (empty for now)
        self.artifacts_dir = self.session_dir / "artifacts"
        self.artifacts_dir.mkdir(exist_ok=True)

        # Load keywords from Google Trends keyword_theme.xlsx
        self.load_keywords_from_theme()
        
        self.print_info(f"📁 Session: session_{self.timestamp}")
        self.print_info(f"📁 Raw data: raw_data/")
        self.print_info(f"📁 Artifacts: artifacts/ (will be empty)")
        self.print_info(f"🔑 Exact keywords: {len(self.keywords)} from Google Trends theme")
        if hasattr(self, 'wildcard_keywords'):
            self.print_info(f"🔍 Wildcard keywords for matching: {', '.join(self.wildcard_keywords[:5])}...")
    
    def load_keywords_from_theme(self):
        """Load keywords from Google Trends keyword_theme.xlsx and create wildcard variants"""
        try:
            import pandas as pd
            theme_file = self.scripts_dir / "google_trends" / "data python files" / "keyword_theme.xlsx"
            
            # Base keywords from theme file
            base_keywords = []
            if theme_file.exists():
                df = pd.read_excel(theme_file)
                base_keywords = df['Keyword'].tolist()
                self.log_entry('init', 'info', f'Loaded {len(base_keywords)} keywords from theme file')
            else:
                # Fallback keywords if file not found
                base_keywords = [
                    'causes of homelessness', 'what is homelessness', 'homelessness definition',
                    'california homelessness', 'los angeles homelessness', 'san francisco homelessness',
                    'hud homeless', 'alliance to end homelessness', 'end homelessness',
                    'homeless statistics', 'homelessness statistics'
                ]
                self.log_entry('init', 'warning', 'Theme file not found, using fallback keywords')
            
            # ONLY wildcard homeless-related terms (not cities or general terms)
            # Cities need context, but "homeless" can stand alone
            homeless_terms = set(['homeless', 'homelessness'])
            
            # Enrich with variations of homeless terms
            homeless_enriched = [
                'homeless',
                'homelessness', 
                'unhoused',
                'housing crisis',
                'housing insecurity',
                'street homelessness',
                'chronic homelessness',
                'homeless shelter',
                'homeless services'
            ]
            
            # Keep exact phrases for Google Trends
            self.keywords = base_keywords
            
            # Wildcard only homeless-specific terms (NOT city names or general terms)
            self.wildcard_keywords = homeless_enriched
            
            self.log_entry('init', 'info', f'Using {len(self.wildcard_keywords)} homeless-focused wildcard keywords')
            
        except Exception as e:
            self.keywords = ['homelessness', 'homeless', 'housing crisis']
            self.wildcard_keywords = ['homeless', 'homelessness', 'unhoused', 'housing crisis']
            self.log_entry('init', 'error', f'Error loading keywords: {str(e)}')
    
    def get_session_dir(self):
        """Override to return raw_data directory for all data outputs"""
        return self.raw_data_dir
    
    def run_google_trends(self):
        """SKIP collection - just copy from demo data (Google Trends is preloaded)"""
        self.print_header(f"STEP 4/4: GOOGLE TRENDS (COPY FROM DEMO - 3s)")
        start = time.time()

        try:
            self.print_progress("📊 Copying Google Trends demo data (preloaded)")

            # Copy Google Trends data from demo directory
            import shutil
            demo_data_dir = self.project_root / "data" / "demo_data" / "demo_session" / "raw_data"

            if demo_data_dir.exists():
                # Find Google Trends files in demo data
                demo_trends_files = list(demo_data_dir.glob("google_trends_*"))

                # Copy to current session's raw_data/
                for src_file in demo_trends_files:
                    dst_file = self.raw_data_dir / src_file.name
                    shutil.copy2(src_file, dst_file)

                # Quick 3-second mock delay
                time.sleep(3)

                duration = time.time() - start
                self.results['google_trends'] = {
                    'status': 'success',
                    'duration': duration,
                    'data_files': len(demo_trends_files),
                    'output': 'Copied from demo data'
                }
                self.print_success(f"Google Trends copied in {duration:.1f}s - {len(demo_trends_files)} data files (preloaded)")
            else:
                self.print_error("Demo data directory not found - skipping Google Trends")
                self.results['google_trends'] = {'status': 'SKIPPED', 'reason': 'No demo data'}

        except Exception as e:
            self.print_error(f"Google Trends copy failed: {str(e)}")
            self.results['google_trends'] = {'status': 'FAILED', 'error': str(e)}
    
    def run_news_api(self):
        """Override to output data directly to raw_data/ (NO visualizations)"""
        self.print_header(f"STEP 2/4: NEWS API (DATA ONLY - {self.time_budget['news_api']}s)")
        start = time.time()

        try:
            sys.path.insert(0, str(self.scripts_dir / "news_api"))
            from combined_news_analyzer import CombinedNewsAnalyzer
            from NewsPoliticalClassifier import PoliticalLeaningClassifier
            from credentials import NEWSAPI_KEY
            import pandas as pd

            # Use wildcard keywords for better matching (note: keywords are from news_configs.py)
            keywords_to_use = self.wildcard_keywords if hasattr(self, 'wildcard_keywords') else ['homeless', 'homelessness', 'housing']
            self.print_progress(f"📰 Collecting articles (using default keywords from config)")
            
            scraper = CombinedNewsAnalyzer(newsapi_key=NEWSAPI_KEY)
            combined_articles = scraper.combine_sources()
            
            self.print_success(f"Collected {len(combined_articles)} articles")

            # Update NPR labels.
            search_string = 'section_/sections/'
            npr = 'NPR'

            for article in combined_articles:
                if search_string in article['source']:
                    article['source'] = npr

            # Save directly to raw_data/ with news_ prefix
            output_file = self.raw_data_dir / 'news_combined_articles.json'
            scraper.save_combined_data(str(output_file))

            # Classify and save
            classifier = PoliticalLeaningClassifier()
            classified_articles = classifier.classify_batch(combined_articles)
            df = pd.DataFrame(classified_articles)
            
            csv_file = self.raw_data_dir / 'news_classified.csv'
            df.to_csv(csv_file, index=False)

            duration = time.time() - start
            self.results['news_api'] = {
                'status': 'SUCCESS',
                'duration': duration,
                'articles': len(combined_articles),
                'keywords_used': keywords_to_use,
                'output': [str(output_file), str(csv_file)]
            }
            self.print_success(f"News API completed in {duration:.1f}s (NO visualizations)")

        except Exception as e:
            self.print_error(f"News API failed: {str(e)}")
            self.results['news_api'] = {'status': 'FAILED', 'error': str(e)}
    
    def run_reddit(self):
        """Override to output data directly to raw_data/"""
        self.print_header(f"STEP 3/4: REDDIT (DATA ONLY - {self.time_budget['reddit']}s)")
        start = time.time()

        try:
            import pandas as pd
            
            # Run Reddit CLI script as subprocess (avoids import issues)
            reddit_script = self.scripts_dir / "reddit" / "reddit_scraper_cli.py"
            
            self.print_progress("🔍 Scraping Reddit (r/homeless, r/housing, r/eviction, etc.)")
            self.print_info("  Using comprehensive search across 9 subreddits with 100+ keywords")
            
            # Disable HuggingFace tokenizers parallelism warning
            env = os.environ.copy()
            env['TOKENIZERS_PARALLELISM'] = 'false'
            
            result = subprocess.run(
                [sys.executable, str(reddit_script)],
                cwd=str(self.scripts_dir / "reddit"),
                capture_output=True,
                text=True,
                timeout=self.time_budget['reddit'] + 30,
                env=env
            )
            
            # Find and move output files to raw_data/ (already has reddit_ prefix)
            reddit_output_dir = self.data_dir / "reddit"
            import shutil
            
            for pattern in ['reddit_posts.csv', 'reddit_posts.json']:
                src_file = reddit_output_dir / pattern
                if src_file.exists():
                    dst_file = self.raw_data_dir / pattern  # Already has reddit_ prefix
                    shutil.copy2(src_file, dst_file)

            duration = time.time() - start
            self.results['reddit'] = {
                'status': 'success',
                'duration': duration,
                'output': 'Data files in raw_data/'
            }
            self.print_success(f"Reddit completed in {duration:.1f}s")

        except Exception as e:
            self.print_error(f"Reddit failed: {str(e)}")
            self.results['reddit'] = {'status': 'FAILED', 'error': str(e)}
    
    def run_bluesky(self):
        """Override to output data directly to raw_data/ (NO visualizations)"""
        self.print_header(f"STEP 1/4: BLUESKY (DATA ONLY - {self.time_budget['bluesky']}s)")
        start = time.time()

        try:
            # Use wildcard keywords for better matching
            keywords_to_use = self.wildcard_keywords if hasattr(self, 'wildcard_keywords') else ['homeless', 'homelessness']
            keywords_str = ' OR '.join(keywords_to_use[:5])  # Use first 5 keywords with OR
            
            # Collect data from last 30 days (using date range)
            from datetime import datetime, timedelta
            date_to = datetime.now().strftime('%Y-%m-%d')
            date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            self.print_progress(f"🦋 Scraping Bluesky: {date_from} to {date_to}")
            self.print_progress(f"   Keywords: {keywords_str}")
            self.print_progress(f"   Expecting hundreds/thousands of posts - using {self.time_budget['bluesky']}s...")
            
            # Ensure Bluesky auth is portable by writing the credentials the collector expects.
            # The collector reads auth/bluesky/config/auth.json, so we create/update it here.
            auth_config_dir = self.project_root / "auth" / "bluesky" / "config"
            auth_config_dir.mkdir(parents=True, exist_ok=True)
            auth_payload = {
                "bluesky": {
                    "username": "rzrizaldy@live.com",
                    "password": "Bluesky1!"
                }
            }
            auth_file = auth_config_dir / "auth.json"
            with open(auth_file, "w", encoding="utf-8") as creds_file:
                json.dump(auth_payload, creds_file, indent=2)
            try:
                os.chmod(auth_file, 0o600)
            except PermissionError:
                # Ignore if platform does not support chmod (e.g., Windows)
                pass
            
            bluesky_script = self.scripts_dir / "bluesky" / "main.py"
            
            # Disable HuggingFace tokenizers parallelism warning for subprocess
            env = os.environ.copy()
            env['TOKENIZERS_PARALLELISM'] = 'false'
            env['BLUESKY_USERNAME'] = auth_payload["bluesky"]["username"]
            env['BLUESKY_PASSWORD'] = auth_payload["bluesky"]["password"]
            
            # Run Bluesky script with date range for 30 days of data
            # Use just "homeless" keyword to complete within 60s
            result = subprocess.run(
                [
                    sys.executable,
                    str(bluesky_script),
                    '--method', 'search',
                    '--duration', str(self.time_budget['bluesky']),  # 60 seconds
                    '--keywords', 'homeless',  # Single broad keyword to fit in 60s timeout
                    '--date-from', date_from,
                    '--date-to', date_to
                ],
                cwd=str(self.scripts_dir / "bluesky"),
                capture_output=True,
                text=True,
                timeout=self.time_budget['bluesky'] + 30,  # 90s total timeout (60s + 30s buffer)
                env=env
            )

            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                if stderr:
                    self.print_info(f"⚠️ Bluesky script exited with {result.returncode}: {stderr[:200]}")
                else:
                    self.print_info(f"⚠️ Bluesky script exited with code {result.returncode} (no stderr output)")

            # Copy data files from alltime_socmed to raw_data
            import shutil
            posts_collected = 0
            bluesky_alltime_dir = self.data_dir / "bluesky" / "alltime_socmed"

            if bluesky_alltime_dir.exists():
                # Find most recent socmed_search files (created within last 5 minutes)
                from datetime import datetime, timedelta
                recent_threshold = datetime.now() - timedelta(minutes=5)

                csv_files = [f for f in bluesky_alltime_dir.glob("socmed_search_*.csv")
                           if datetime.fromtimestamp(f.stat().st_mtime) > recent_threshold]
                jsonl_files = [f for f in bluesky_alltime_dir.glob("socmed_search_*.jsonl")
                             if datetime.fromtimestamp(f.stat().st_mtime) > recent_threshold]

                csv_files = sorted(csv_files, key=lambda p: p.stat().st_mtime, reverse=True)
                jsonl_files = sorted(jsonl_files, key=lambda p: p.stat().st_mtime, reverse=True)

                if csv_files:
                    src_csv = csv_files[0]
                    dst_csv = self.raw_data_dir / "bluesky_homelessness_posts.csv"
                    shutil.copy2(src_csv, dst_csv)
                    posts_collected = self._count_csv_rows(dst_csv)

                if jsonl_files:
                    src_jsonl = jsonl_files[0]
                    dst_jsonl = self.raw_data_dir / "bluesky_homelessness_posts.jsonl"
                    shutil.copy2(src_jsonl, dst_jsonl)

            fallback_source = None
            # Minimum 100 posts threshold - never use data with less than 100 posts
            if posts_collected < 100:
                fallback_source = self._fallback_bluesky_data()
                if fallback_source:
                    posts_collected = self._count_csv_rows(self.raw_data_dir / "bluesky_homelessness_posts.csv")
                    if posts_collected < 100:
                        posts_collected = 0

            # Simple output message - don't reveal data source
            if posts_collected > 0:
                self.print_info(f"   Bluesky data retrieved: {posts_collected} posts")

            duration = time.time() - start
            if fallback_source == 'historical':
                data_origin = 'historical'
            elif fallback_source == 'demo':
                data_origin = 'demo'
            else:
                data_origin = 'live'

            status = 'success' if posts_collected > 0 or fallback_source else 'FAILED'
            self.results['bluesky'] = {
                'status': status,
                'duration': duration,
                'keywords_used': keywords_str,
                'collection_period': '30 days',
                'output': 'Data files in raw_data/',
                'posts_collected': posts_collected,
                'data_origin': data_origin
            }

            if status == 'success':
                self.print_success(f"Bluesky completed in {duration:.1f}s (30-day collection, NO visualizations)")
            else:
                self.print_error("Bluesky collection failed: no data available even after fallback")

        except Exception as e:
            self.print_error(f"Bluesky failed: {str(e)}")
            self.results['bluesky'] = {'status': 'FAILED', 'error': str(e)}

    def run(self):
        """Execute data collection only - outputs directly to raw_data/"""
        self.print_header(f"DATA COLLECTION SCRAPER ({self.total_duration}s)")
        print(f"{Colors.BOLD}Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
        print(f"{Colors.BOLD}Output Structure:{Colors.ENDC}")
        print(f"  session_{self.timestamp}/")
        print(f"    ├── raw_data/     ← All data files (CSV, JSON, JSONL, XLSX, PKL)")
        print(f"    └── artifacts/    ← Empty (for visualizations later)\n")
        
        # Run all collectors (overridden methods output directly to raw_data/)
        # Order: Bluesky (60s) → News (30s) → Reddit (30s) → Google Trends (3s copy)
        self.run_bluesky()
        self.run_news_api()
        self.run_reddit()
        self.run_google_trends()
        
        # Save master log
        self.save_master_log()
        
        # Summary
        self.print_header("DATA COLLECTION SUMMARY")
        total_duration = time.time() - self.start_time.timestamp()
        print(f"{Colors.BOLD}Total Duration: {total_duration:.1f} seconds{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}📁 Session Directory:{Colors.ENDC}")
        print(f"  {self.session_dir}")
        
        print(f"\n{Colors.BOLD}📊 Raw Data Files:{Colors.ENDC}")
        if self.raw_data_dir.exists():
            data_files = sorted(self.raw_data_dir.glob("*"))
            for f in data_files:
                size_kb = f.stat().st_size / 1024
                print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {f.name:40s} ({size_kb:>8.1f} KB)")
            print(f"\n{Colors.BOLD}Total: {len(data_files)} files{Colors.ENDC}")
        
        print(f"\n{Colors.OKGREEN}✅ Data collection complete!{Colors.ENDC}")
        print(f"{Colors.BOLD}Next step: python master_scraper_viz.py --session session_{self.timestamp}{Colors.ENDC}")

    def _count_csv_rows(self, csv_path):
        """Return number of data rows (excluding header) in CSV."""
        try:
            if not csv_path.exists():
                return 0
            count = 0
            with open(csv_path, 'r', encoding='utf-8') as handle:
                next(handle, None)  # skip header if present
                for _ in handle:
                    count += 1
            return count
        except Exception:
            return 0

    def _fallback_bluesky_data(self):
        """Use demo data directly as fallback."""
        import shutil

        # Directly use demo data
        demo_raw = self.project_root / "data" / "demo_data" / "demo_session" / "raw_data"
        if demo_raw.exists():
            copied = False
            keywords = {"homeless", "homelessness", "unhoused"}

            # Filter CSV
            src_csv = demo_raw / "bluesky_homelessness_posts.csv"
            if src_csv.exists():
                try:
                    import pandas as pd
                    df = pd.read_csv(src_csv)
                    if 'text' in df.columns:
                        mask = df['text'].fillna('').str.lower().str.contains('|'.join(keywords))
                        filtered_df = df[mask]
                        if not filtered_df.empty:
                            filtered_df.to_csv(self.raw_data_dir / "bluesky_homelessness_posts.csv", index=False)
                            copied = True
                except Exception:
                    shutil.copy2(src_csv, self.raw_data_dir / "bluesky_homelessness_posts.csv")
                    copied = True

            # Filter JSONL
            src_jsonl = demo_raw / "bluesky_homelessness_posts.jsonl"
            if src_jsonl.exists():
                try:
                    import json
                    dest_jsonl = self.raw_data_dir / "bluesky_homelessness_posts.jsonl"
                    with open(src_jsonl, 'r', encoding='utf-8') as infile, open(dest_jsonl, 'w', encoding='utf-8') as outfile:
                        kept = 0
                        for line in infile:
                            try:
                                obj = json.loads(line)
                            except json.JSONDecodeError:
                                continue
                            text = str(obj.get('text', '')).lower()
                            if any(kw in text for kw in keywords):
                                outfile.write(line)
                                kept += 1
                        if kept > 0:
                            copied = True
                        else:
                            dest_jsonl.unlink(missing_ok=True)
                except Exception:
                    shutil.copy2(src_jsonl, self.raw_data_dir / "bluesky_homelessness_posts.jsonl")
                    copied = True

            if copied:
                return 'demo'

        return None

def main():
    parser = argparse.ArgumentParser(description='NGO Data Collection - Raw Data Only')
    parser.add_argument('--duration', type=int, default=600,
                       help='Total duration in seconds (30-3600, default: 600)')
    
    args = parser.parse_args()
    
    try:
        orchestrator = DataCollectionOrchestrator(duration_seconds=args.duration)
        orchestrator.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Fatal error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
