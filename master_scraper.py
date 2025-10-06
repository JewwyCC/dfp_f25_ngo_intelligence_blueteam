#!/usr/bin/env python3
"""
NGO Intelligence Platform - Comprehensive Homelessness Research Master Scraper
Sequential data collection focused on homelessness crisis

Usage: python master_scraper.py --duration <seconds>
Duration: 30-3600 seconds (default: 60s)
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
import time

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class HomelessnessMasterOrchestrator:
    def __init__(self, duration_seconds=60):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.master_output_dir = self.data_dir / "master_output"
        self.scripts_dir = self.project_root / "scripts"
        self.start_time = datetime.now()
        self.timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
        self.results = {}
        self.keywords = []
        self.log_entries = []

        # Create master output directory
        self.master_output_dir.mkdir(exist_ok=True)

        # Duration and time budget allocation
        self.total_duration = max(30, min(duration_seconds, 3600))  # Clamp 30s-3600s
        self.time_budget = {
            'google_trends': int(self.total_duration * 0.15),  # 15%
            'news_api': int(self.total_duration * 0.30),       # 30%
            'reddit': int(self.total_duration * 0.25),         # 25%
            'bluesky': int(self.total_duration * 0.30)         # 30%
        }

    def print_header(self, message):
        """Print formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
        print(f"{message:^80}")
        print(f"{'='*80}{Colors.ENDC}")

    def print_success(self, message):
        print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

    def print_error(self, message):
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

    def print_info(self, message):
        print(f"{Colors.OKCYAN}➜ {message}{Colors.ENDC}")

    def print_progress(self, message):
        print(f"{Colors.BOLD}  {message}{Colors.ENDC}", flush=True)

    def log_entry(self, module, level, message, data=None):
        """Add entry to master log"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'module': module,
            'level': level,
            'message': message,
            'data': data
        }
        self.log_entries.append(entry)

    def save_master_log(self):
        """Save comprehensive master log"""
        log_file = self.master_output_dir / f"master_log_{self.timestamp}.json"
        log_data = {
            'session_info': {
                'start_time': self.start_time.isoformat(),
                'duration_budget': self.total_duration,
                'time_budget': self.time_budget,
                'timestamp': self.timestamp
            },
            'results': self.results,
            'keywords': self.keywords,
            'log_entries': self.log_entries
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        self.print_info(f"Master log saved: {log_file}")
        return log_file

    def filter_homelessness_keywords(self, keywords):
        """Filter keywords to only include homelessness-related terms"""
        homelessness_terms = [
            'homeless', 'homelessness', 'housing', 'shelter', 'unhoused',
            'affordable housing', 'housing crisis', 'rent', 'eviction',
            'affordable', 'supportive housing', 'transitional housing',
            'housing insecurity', 'houseless', 'rough sleeping'
        ]

        filtered = []
        for kw in keywords:
            kw_lower = kw.lower()
            if any(term in kw_lower for term in homelessness_terms):
                filtered.append(kw)

        # If no matches, use defaults
        if not filtered:
            filtered = ['homelessness', 'housing crisis', 'affordable housing', 'homeless shelter']

        return filtered

    def run_google_trends(self):
        """Step 1: Google Trends - Run EXACT script workflow with comprehensive logging"""
        self.print_header(f"STEP 1/4: GOOGLE TRENDS (HOMELESSNESS ANALYSIS - {self.time_budget['google_trends']}s)")
        start = time.time()

        self.log_entry('google_trends', 'info', f"Starting Google Trends analysis with {self.time_budget['google_trends']}s budget")

        try:
            self.print_progress("🕰️ PATIENT Google Trends: Running googletrends.py (NO TIMEOUT)")
            self.print_progress("This creates: Excel files, normalized CSV, visualizations, and keyword extraction")
            self.print_progress("⏳ Please wait - comprehensive analysis takes time...")
            
            self.log_entry('google_trends', 'info', 'Executing googletrends.py script with NO TIMEOUT - being patient', {
                'script_path': str(self.scripts_dir / "google_trends" / "googletrends.py"),
                'timeout': 'NONE - Patient execution'
            })

            # Run the EXACT Google Trends script as it's designed - NO TIMEOUT, BE PATIENT!
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.scripts_dir / "google_trends" / "googletrends.py")
                ],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
                # NO TIMEOUT - Let it run as long as needed for comprehensive analysis
            )

            elapsed = time.time() - start

            if result.returncode == 0:
                # Parse the script output for key information
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if any(indicator in line for indicator in ['✓', 'Analysis Complete', 'saved', 'completed', 'Google Trends']):
                        self.print_info(line.strip())
                        self.log_entry('google_trends', 'info', line.strip())

                # Extract keywords from the script's output files
                self.keywords = self.extract_keywords_from_trends()
                
                self.print_success(f"Google Trends script completed in {elapsed:.1f}s")
                self.print_info(f"Keywords extracted: {len(self.keywords)} homelessness-related terms")
                self.print_info(f"Sample: {', '.join(self.keywords[:5])}")

                self.log_entry('google_trends', 'success', f"Script completed successfully", {
                    'duration': elapsed,
                    'keywords_extracted': len(self.keywords),
                    'keywords_sample': self.keywords[:5]
                })

                # Copy output files to master output directory
                output_files = self.copy_google_trends_outputs()

                self.results['google_trends'] = {
                    'status': 'success',
                    'keywords_extracted': len(self.keywords),
                    'duration': elapsed,
                    'output_files': output_files
                }
                return True
            else:
                self.print_error(f"Google Trends script failed: {result.stderr[:200]}")
                self.log_entry('google_trends', 'error', 'Script execution failed', {
                    'returncode': result.returncode,
                    'stderr': result.stderr[:200]
                })
                
                # Fallback to default keywords
                self.keywords = ['homelessness', 'housing crisis', 'affordable housing', 'homeless shelter',
                               'unhoused', 'housing insecurity', 'supportive housing']
                self.results['google_trends'] = {
                    'status': 'partial',
                    'keywords_extracted': len(self.keywords),
                    'duration': elapsed,
                    'error': result.stderr[:200]
                }
                return True

        except KeyboardInterrupt:
            elapsed = time.time() - start
            self.print_error(f"Google Trends interrupted by user after {elapsed:.1f}s")
            self.log_entry('google_trends', 'interrupted', f"Script interrupted by user after {elapsed:.1f}s")
            
            # Still try to extract keywords from existing files
            self.keywords = self.extract_keywords_from_trends()
            self.log_entry('google_trends', 'info', 'Extracting keywords from existing files after interruption')
            
            # Copy any existing output files
            output_files = self.copy_google_trends_outputs()
            
            self.results['google_trends'] = {
                'status': 'interrupted', 
                'duration': elapsed,
                'keywords_extracted': len(self.keywords),
                'output_files': output_files
            }
            return False
        except Exception as e:
            elapsed = time.time() - start
            self.print_error(f"Error: {str(e)}")
            self.log_entry('google_trends', 'error', f'Exception occurred: {str(e)}')
            
            self.keywords = ['homelessness', 'housing crisis', 'affordable housing']
            self.results['google_trends'] = {'status': 'failed', 'error': str(e), 'duration': elapsed}
            return False

    def extract_keywords_from_trends(self):
        """Extract keywords from Google Trends keyword_theme.xlsx file"""
        try:
            trends_data_dir = self.scripts_dir / "google_trends" / "data python files"
            keyword_file = trends_data_dir / "keyword_theme.xlsx"

            if keyword_file.exists():
                import pandas as pd
                df = pd.read_excel(keyword_file)

                # Extract all keywords
                all_keywords = []
                for col in df.columns:
                    keywords = df[col].dropna().astype(str).tolist()
                    all_keywords.extend(keywords)

                # Clean and deduplicate
                all_keywords = list(set([k.strip() for k in all_keywords if k.strip() and len(k.strip()) > 2]))

                # Filter for homelessness-related only
                return self.filter_homelessness_keywords(all_keywords)
            else:
                return ['homelessness', 'housing crisis', 'affordable housing', 'homeless shelter',
                               'unhoused', 'housing insecurity', 'supportive housing']
        except Exception:
            return ['homelessness', 'housing crisis', 'affordable housing']

    def find_google_trends_outputs(self):
        """Find Google Trends output files created by the script"""
        output_files = []
        try:
            # Look for recent files in the scripts/google_trends directory
            trends_dir = self.scripts_dir / "google_trends"
            
            # Find files created by the script (with timestamp pattern)
            excel_files = list(trends_dir.glob("googletrends_*_*.xlsx"))
            csv_files = list(trends_dir.glob("googletrends_*_*.csv"))
            json_files = list(trends_dir.glob("googletrends_*_*.json"))
            pkl_files = list(trends_dir.glob("googletrends_*_*.pkl"))
            
            # Get the most recent files
            all_files = excel_files + csv_files + json_files + pkl_files
            if all_files:
                recent_files = sorted(all_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
                output_files = [str(f) for f in recent_files]
            
            # Also look for visualization files in viz directory
            viz_dir = self.project_root / "viz" / "google_trends"
            if viz_dir.exists():
                viz_files = list(viz_dir.glob("*"))
                if viz_files:
                    recent_viz = sorted(viz_files, key=lambda p: p.stat().st_mtime, reverse=True)[:3]
                    output_files.extend([str(f) for f in recent_viz])
                    
        except Exception:
            pass
            
        return output_files

    def copy_google_trends_outputs(self):
        """Copy Google Trends output files to master output directory and CLEAN source files"""
        copied_files = []
        try:
            # Create session directory for Google Trends
            session_dir = self.master_output_dir / f"session_{self.timestamp}"
            session_dir.mkdir(exist_ok=True)

            # Look for recent files in the scripts/google_trends directory
            trends_dir = self.scripts_dir / "google_trends"

            # Find files created by the script (with timestamp pattern)
            excel_files = list(trends_dir.glob("googletrends_*_*.xlsx"))
            csv_files = list(trends_dir.glob("googletrends_*_*.csv"))
            json_files = list(trends_dir.glob("googletrends_*_*.json"))
            pkl_files = list(trends_dir.glob("googletrends_*_*.pkl"))

            # Get the most recent files and copy to session directory
            all_files = excel_files + csv_files + json_files + pkl_files
            if all_files:
                recent_files = sorted(all_files, key=lambda p: p.stat().st_mtime, reverse=True)[:10]
                for src_file in recent_files:
                    dst_file = session_dir / src_file.name
                    import shutil
                    shutil.copy2(src_file, dst_file)
                    copied_files.append(str(dst_file))

            # Copy visualization files if they exist
            viz_dir = self.project_root / "viz" / "google_trends"
            if viz_dir.exists():
                viz_files = list(viz_dir.glob("*"))
                if viz_files:
                    recent_viz = sorted(viz_files, key=lambda p: p.stat().st_mtime, reverse=True)[:20]
                    for src_file in recent_viz:
                        dst_file = session_dir / f"viz_{src_file.name}"
                        import shutil
                        shutil.copy2(src_file, dst_file)
                        copied_files.append(str(dst_file))

            # CLEAN UP: Delete timestamp files from source directories (centralize in master_output)
            import shutil
            for f in all_files:
                f.unlink()  # Delete timestamp files from scripts/google_trends
            if viz_dir.exists():
                for f in viz_files:
                    f.unlink()  # Delete viz files from viz/google_trends

            self.log_entry('google_trends', 'info', f'Copied {len(copied_files)} files and cleaned source directories')

        except Exception as e:
            self.log_entry('google_trends', 'warning', f'Error copying output files: {str(e)}')

        return copied_files

    def copy_bluesky_outputs(self):
        """Copy Bluesky output files to master_output with session format and rename to homelessness"""
        copied_files = []
        try:
            # Find the most recent Bluesky session - use ANY recent homelessness session
            bluesky_sessions_dir = self.data_dir / "bluesky" / "sessions"
            if bluesky_sessions_dir.exists():
                # Look for homelessness sessions (created by our wrapper)
                session_dirs = [d for d in bluesky_sessions_dir.iterdir()
                               if d.is_dir() and ('homelessness' in d.name or 'test' in d.name or 'quicktest' in d.name)]

                if session_dirs:
                    # Get the most recent session
                    latest_session = max(session_dirs, key=lambda p: p.stat().st_mtime)

                    # Only copy if it has actual data files
                    has_data = any(f.suffix in ['.jsonl', '.csv'] for f in latest_session.glob('*'))

                    if has_data:
                        
                        # Create session directory in master_output
                        master_session_dir = self.master_output_dir / f"session_{self.timestamp}"
                        master_session_dir.mkdir(exist_ok=True)
                        
                        # Copy all files from the latest Bluesky session and rename to homelessness
                        for file_path in latest_session.glob("*"):
                            if file_path.is_file():
                                # Rename to homelessness-focused names
                                if "food_insecurity" in file_path.name:
                                    new_name = file_path.name.replace("food_insecurity", "homelessness")
                                elif file_path.name.endswith("_posts.jsonl"):
                                    new_name = "homelessness_posts.jsonl"
                                elif file_path.name.endswith("_posts.csv"):
                                    new_name = "homelessness_posts.csv"
                                else:
                                    new_name = file_path.name
                                
                                dst_file = master_session_dir / new_name
                                import shutil
                                shutil.copy2(file_path, dst_file)
                                copied_files.append(str(dst_file))
                        
                        self.log_entry('bluesky', 'info', f'Copied and renamed {len(copied_files)} files from {latest_session.name} to master_output/session_{self.timestamp}')
                    else:
                        self.log_entry('bluesky', 'warning', f'Bluesky session found but no data files - skipping copy: {latest_session.name}')
                else:
                    self.log_entry('bluesky', 'warning', 'No Bluesky homelessness sessions found - skipping copy')

        except Exception as e:
            self.log_entry('bluesky', 'warning', f'Error copying Bluesky output files: {str(e)}')
            
        return copied_files

    def run_news_api(self):
        """Step 2: News API - HUNGRY SCRAPER using DIRECT IMPORT"""
        self.print_header(f"STEP 2/4: NEWS API (HOMELESSNESS ARTICLES - {self.time_budget['news_api']}s)")
        start = time.time()

        self.log_entry('news_api', 'info', f"Starting News API scraping with {self.time_budget['news_api']}s budget")

        try:
            # Add News API directory to path
            sys.path.insert(0, str(self.scripts_dir / "news_api"))

            # Import directly like dfp_socmed_blueteam does
            from NewsAPI_Scrape import NewsAPIScraper
            from news_configs import KEYWORDS_DEFAULT, MAX_PAGES
            from credentials import NEWSAPI_KEY
            import pandas as pd

            # Use targeted homelessness keywords
            if self.keywords:
                # Filter Google Trends keywords to only include homelessness-related ones
                filtered_trends_keywords = [kw for kw in self.keywords if any(homeless_term in kw.lower() for homeless_term in ['homeless', 'housing', 'unhoused', 'eviction', 'affordable', 'shelter', 'tent', 'encampment'])]
                combined_keywords = list(set(filtered_trends_keywords + KEYWORDS_DEFAULT))
            else:
                combined_keywords = KEYWORDS_DEFAULT

            # HUNGRY SCRAPER: Use MAX_PAGES (100) for comprehensive collection
            num_articles = min(MAX_PAGES, self.time_budget['news_api'] * 3)  # Scale aggressively

            self.print_progress(f"🦁 HUNGRY NEWS SCRAPER: Fetching {num_articles} articles")
            self.print_progress(f"Keywords ({len(combined_keywords)}): {', '.join(combined_keywords[:8])}...")

            self.log_entry('news_api', 'info', 'Using exact News API configuration', {
                'keywords_count': len(combined_keywords),
                'max_pages': MAX_PAGES,
                'target_articles': num_articles,
                'keywords_sample': combined_keywords[:5]
            })

            # Initialize scraper
            scraper = NewsAPIScraper(NEWSAPI_KEY)

            print(f"{Colors.OKCYAN}➜ HUNGRY SCRAPER: Using {len(combined_keywords)} keywords, targeting {num_articles} articles{Colors.ENDC}")

            # Fetch articles - NEWS API ALREADY FILTERS BY KEYWORDS!
            # Don't double-filter or we lose all results
            articles = scraper.fetch_articles(keywords=combined_keywords, page_size=num_articles)

            print(f"{Colors.OKCYAN}➜ SUCCESS: Collected {len(articles)} homelessness articles{Colors.ENDC}")

            # POLARIZATION ANALYSIS: Keyword-based political bias classification
            if articles:
                print(f"{Colors.OKCYAN}➜ Running polarization analysis on {len(articles)} articles...{Colors.ENDC}")

                left_keywords = ['progressive', 'liberal', 'democrat', 'social justice', 'equity',
                                'climate action', 'healthcare for all', 'lgbtq', 'immigrant rights',
                                'gun control', 'abortion rights', 'blm', 'defund', 'taxing the rich']
                right_keywords = ['conservative', 'republican', 'traditional', 'freedom', 'liberty',
                                 'border security', 'pro-life', 'second amendment', 'small government',
                                 'law and order', 'patriot', 'maga', 'god', 'family values']

                for article in articles:
                    text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
                    left_matches = sum(1 for kw in left_keywords if kw in text)
                    right_matches = sum(1 for kw in right_keywords if kw in text)

                    total_matches = left_matches + right_matches
                    if total_matches > 0:
                        if left_matches > right_matches:
                            article['political_bias'] = 'LEFT'
                            article['bias_confidence'] = round(left_matches / total_matches, 2)
                        elif right_matches > left_matches:
                            article['political_bias'] = 'RIGHT'
                            article['bias_confidence'] = round(right_matches / total_matches, 2)
                        else:
                            article['political_bias'] = 'NEUTRAL'
                            article['bias_confidence'] = 0.5
                    else:
                        article['political_bias'] = 'NEUTRAL'
                        article['bias_confidence'] = 0.0

                left_count = sum(1 for a in articles if a.get('political_bias') == 'LEFT')
                right_count = sum(1 for a in articles if a.get('political_bias') == 'RIGHT')
                neutral_count = sum(1 for a in articles if a.get('political_bias') == 'NEUTRAL')
                print(f"{Colors.OKCYAN}➜ Polarization: LEFT={left_count}, RIGHT={right_count}, NEUTRAL={neutral_count}{Colors.ENDC}")

            # Save to MASTER OUTPUT directory
            session_dir = self.master_output_dir / f"session_{self.timestamp}"
            session_dir.mkdir(exist_ok=True)

            output_file = session_dir / 'news_api_articles.json'
            with open(output_file, 'w') as f:
                json.dump(articles, f, indent=2)

            # Save CSV
            csv_file = session_dir / 'news_api_articles.csv'
            if articles:
                df = pd.DataFrame(articles)
            else:
                df = pd.DataFrame(columns=['title', 'description', 'url', 'publishedAt', 'source'])
            df.to_csv(csv_file, index=False)

            print(f"{Colors.OKCYAN}➜ CSV: {csv_file}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}➜ JSON: {output_file}{Colors.ENDC}")

            elapsed = time.time() - start
            self.print_success(f"🦁 HUNGRY News API completed in {elapsed:.1f}s")

            self.log_entry('news_api', 'success', f"Collected {len(articles)} homelessness articles", {
                'articles_count': len(articles),
                'elapsed_seconds': round(elapsed, 1)
            })

            self.results['news_api'] = {'status': 'SUCCESS', 'duration': elapsed, 'articles': len(articles)}

        except Exception as e:
            elapsed = time.time() - start
            self.print_failure(f"Failed: {str(e)}")
            self.log_entry('news_api', 'error', f"News API failed: {str(e)}")
            self.results['news_api'] = {'status': 'FAILED', 'duration': elapsed, 'error': str(e)}
            import traceback
            traceback.print_exc()


    def run_reddit(self):
        """Step 3: Reddit - HUNGRY SCRAPER using EXACT script configuration"""
        self.print_header(f"STEP 3/4: REDDIT (HOMELESSNESS POSTS - {self.time_budget['reddit']}s)")
        start = time.time()

        self.log_entry('reddit', 'info', f"Starting Reddit scraping with {self.time_budget['reddit']}s budget")

        # Use EXACT configuration from config.py - BE HUNGRY!
        from scripts.reddit.config import ISSUE_CONFIGS
        
        # Get EXACT Housing/Homelessness config
        config = ISSUE_CONFIGS['Housing/Homelessness']
        all_subreddits = config['subreddits']  # ALL 9 subreddits!
        all_keywords = config['keywords']      # ALL 32 keywords!

        # HUNGRY SCRAPER: Use ALL subreddits and keywords, scale posts aggressively
        posts_per_sub = max(50, min(200, self.time_budget['reddit'] * 2))  # Much more posts
        num_subreddits = len(all_subreddits)  # Use ALL subreddits!

        self.print_progress(f"🦁 PATIENT REDDIT SCRAPER: {posts_per_sub} posts/subreddit from {num_subreddits} subreddits")
        self.print_progress(f"⏳ Please wait - scraping {num_subreddits} subreddits takes time...")
        self.print_progress(f"Subreddits: {', '.join(all_subreddits)}")
        self.print_progress(f"Keywords ({len(all_keywords)}): {', '.join(all_keywords[:8])}...")
        
        self.log_entry('reddit', 'info', 'Using exact Reddit configuration', {
            'subreddits': all_subreddits,
            'keywords_count': len(all_keywords),
            'posts_per_sub': posts_per_sub,
            'total_potential_posts': len(all_subreddits) * posts_per_sub
        })

        wrapper_code = f"""
import sys
sys.path.insert(0, r'{self.scripts_dir / "reddit"}')

try:
    from config import RedditAuth, ISSUE_CONFIGS
    import praw
    from data_collection import collect_with_even_distribution
    import pandas as pd
    import json
    import os

    # Initialize Reddit (following config.py workflow)
    reddit = praw.Reddit(
        client_id=RedditAuth.client_id,
        client_secret=RedditAuth.client_secret,
        user_agent=RedditAuth.user_agent
    )

    # Use EXACT Housing/Homelessness config - ALL subreddits and keywords
    config = ISSUE_CONFIGS['Housing/Homelessness']
    subreddits = config['subreddits']  # ALL subreddits
    keywords = config['keywords']      # ALL keywords

    print(f"HUNGRY SCRAPER: Using ALL {{len(subreddits)}} subreddits and {{len(keywords)}} keywords")
    print(f"Subreddits: {{', '.join(subreddits)}}")
    print(f"Posts per subreddit: {posts_per_sub}")

    # Use the EXACT same method as data_collection.py script
    # COMPREHENSIVE: 1 year of data for thorough analysis
    posts = collect_with_even_distribution(
        reddit=reddit,
        subreddits=subreddits,
        keywords=keywords,
        posts_per_sub={posts_per_sub},
        time_filter='year',  # 1 YEAR of data
        strategy='balanced'
    )

    print(f"SUCCESS: Collected {{len(posts)}} homelessness posts")

    # Save to MASTER OUTPUT directory with session format
    session_dir = '{self.master_output_dir}/session_{self.timestamp}'
    os.makedirs(session_dir, exist_ok=True)

    # CSV (following script's DataFrame handling)
    csv_file = f'{{session_dir}}/reddit_posts.csv'
    df = pd.DataFrame(posts)
    df.to_csv(csv_file, index=False)
    print(f"CSV: {{csv_file}}")

    # JSON (convert to dict first to handle pandas objects properly)
    json_file = f'{{session_dir}}/reddit_posts.json'
    if isinstance(posts, list):
        # Convert pandas objects to strings for JSON serialization
        json_data = []
        for post in posts:
            json_post = {{}}
            for key, value in post.items():
                if hasattr(value, 'isoformat'):  # datetime objects
                    json_post[key] = value.isoformat()
                else:
                    json_post[key] = str(value) if value is not None else None
            json_data.append(json_post)
    else:
        json_data = df.to_dict('records')
        # Convert pandas objects to strings
        for record in json_data:
            for key, value in record.items():
                if hasattr(value, 'isoformat'):  # datetime objects
                    record[key] = value.isoformat()
                else:
                    record[key] = str(value) if value is not None else None
    
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"JSON: {{json_file}}")

except Exception as e:
    print(f"ERROR: {{str(e)}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""

        try:
            # Reddit needs more time for 9 subreddits + 31 keywords - be patient!
            result = subprocess.run(
                [sys.executable, '-c', wrapper_code],
                capture_output=True,
                text=True,
                timeout=max(60, self.time_budget['reddit'] * 3)  # At least 60 seconds or 3x budget
            )

            elapsed = time.time() - start

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.print_info(line)
                        self.log_entry('reddit', 'info', line.strip())

                self.print_success(f"🦁 HUNGRY Reddit completed in {elapsed:.1f}s")
                self.log_entry('reddit', 'success', f"Reddit scraping completed", {
                    'duration': elapsed,
                    'subreddits_used': len(all_subreddits),
                    'keywords_used': len(all_keywords),
                    'posts_collected': 'see output files'
                })
                
                self.results['reddit'] = {
                    'status': 'success',
                    'subreddits_used': len(all_subreddits),
                    'keywords_used': len(all_keywords),
                    'duration': elapsed
                }
                return True
            else:
                self.print_error(f"Failed: {result.stderr}")
                self.log_entry('reddit', 'error', 'Reddit execution failed', {'stderr': result.stderr})
                self.results['reddit'] = {'status': 'failed', 'error': result.stderr, 'duration': elapsed}
                return False

        except Exception as e:
            elapsed = time.time() - start
            self.print_error(f"Error: {str(e)}")
            self.log_entry('reddit', 'error', f'Exception: {str(e)}')
            self.results['reddit'] = {'status': 'failed', 'error': str(e), 'duration': elapsed}
            return False

    def run_bluesky(self):
        """Step 4: Bluesky - WILDCARD SEARCH for homelessness (portable, no dependencies)"""
        self.print_header(f"STEP 4/4: BLUESKY (HOMELESSNESS SEARCH - {self.time_budget['bluesky']}s)")
        start = time.time()

        # WILDCARD SEARCH: Use broad single keyword that matches everything homelessness-related
        # This works on ANY computer - no external dependencies!
        homelessness_search_terms = ['homeless']  # Wildcard: matches homeless, homelessness, homeless shelter, etc.

        # COMPREHENSIVE settings for rich dataset (30s+ collection)
        max_posts = 100  # More posts for comprehensive analysis
        days_back = 7    # Last week of data

        self.print_progress(f"Running Bluesky script workflow")
        self.print_progress(f"Searching for homelessness ({max_posts} posts, {days_back} days)")
        self.print_progress(f"Search terms: {', '.join(homelessness_search_terms)}")

        # Create temporary keywords file with comprehensive homelessness terms
        temp_keywords_file = self.scripts_dir / "bluesky" / "temp_homelessness_keywords.txt"
        with open(temp_keywords_file, 'w') as f:
            f.write('\n'.join(homelessness_search_terms))

        try:
            # Bluesky writes DIRECTLY to master_output - no copying needed!
            session_dir = self.master_output_dir / f"session_{self.timestamp}"
            session_dir.mkdir(exist_ok=True)

            homelessness_wrapper_code = f'''
import sys
import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
sys.path.append('{self.scripts_dir}/bluesky')

try:
    from atproto import Client

    # Authenticate
    auth_path = Path('{self.project_root}/auth/bluesky/config/auth.json')
    if not auth_path.exists():
        print("ERROR: Bluesky auth file not found")
        sys.exit(1)

    with open(auth_path) as f:
        auth_data = json.load(f)
        auth = auth_data['bluesky']  # Get nested bluesky credentials

    client = Client()
    client.login(auth['username'], auth['password'])
    print(f"✅ Authenticated as {{auth['username']}}")

    # Search for homelessness posts with FULL metadata
    posts = []
    query = 'homeless'
    max_posts = {max_posts}

    response = client.app.bsky.feed.search_posts({{'q': query, 'limit': max_posts}})

    for post_view in response.posts[:max_posts]:
        post = post_view.record
        author = post_view.author

        # Get full author profile
        try:
            profile = client.get_profile(author.did)
            followers = profile.followers_count or 0
            following = profile.follows_count or 0
            posts_count = profile.posts_count or 0
        except:
            followers = getattr(author, 'followers_count', 0)
            following = getattr(author, 'following_count', 0)
            posts_count = 0

        # Extract content features
        text = post.text
        words = text.split()
        hashtags = [w for w in words if w.startswith('#')]
        mentions = [w for w in words if w.startswith('@')]
        urls = [w for w in words if w.startswith('http')]

        # Engagement metrics
        like_count = getattr(post_view, 'like_count', 0) or 0
        repost_count = getattr(post_view, 'repost_count', 0) or 0
        reply_count = getattr(post_view, 'reply_count', 0) or 0

        posts.append({{
            # Basic post data
            'uri': post_view.uri,
            'cid': str(post_view.cid) if hasattr(post_view, 'cid') else '',
            'text': text,
            'created_at': post.created_at,
            'keyword': query,
            'lang': post.langs[0] if hasattr(post, 'langs') and post.langs else 'en',

            # Author info
            'author_handle': author.handle,
            'author_did': author.did,
            'author_display_name': getattr(author, 'display_name', ''),
            'author_description': getattr(author, 'description', ''),
            'author_avatar': getattr(author, 'avatar', ''),

            # Author metrics
            'author_followers_count': followers,
            'author_following_count': following,
            'author_posts_count': posts_count,
            'author_verified': getattr(author, 'verified', False),

            # Engagement metrics
            'like_count': like_count,
            'repost_count': repost_count,
            'reply_count': reply_count,
            'total_engagement': like_count + repost_count + reply_count,

            # Content features
            'word_count': len(words),
            'char_count': len(text),
            'hashtag_count': len(hashtags),
            'mention_count': len(mentions),
            'url_count': len(urls),
            'hashtags': ','.join(hashtags) if hashtags else '',
            'mentions': ','.join(mentions) if mentions else '',
            'has_media': hasattr(post, 'embed') and post.embed is not None,
            'is_reply': hasattr(post, 'reply') and post.reply is not None
        }})

    print(f"✅ Collected {{len(posts)}} homeless posts")

    # Write DIRECTLY to master_output
    output_dir = Path('{session_dir}')
    output_dir.mkdir(exist_ok=True, parents=True)

    # Save JSONL
    jsonl_path = output_dir / 'homelessness_posts.jsonl'
    with open(jsonl_path, 'w') as f:
        for post in posts:
            f.write(json.dumps(post) + '\\n')
    print(f"✅ Saved: {{jsonl_path}}")

    # Save CSV
    if posts:
        df = pd.DataFrame(posts)
        csv_path = output_dir / 'homelessness_posts.csv'
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved: {{csv_path}} ({{len(posts)}} posts)")

    print("✅ Bluesky collection complete!")
    
except Exception as e:
    print(f"Error in Bluesky wrapper: {{str(e)}}")
    import traceback
    traceback.print_exc()
'''
            
            # Run the homelessness-focused Bluesky wrapper
            # Always use at least 30s timeout for Bluesky (API can be slow)
            bluesky_timeout = max(30, self.time_budget['bluesky'])
            result = subprocess.run(
                [sys.executable, '-c', homelessness_wrapper_code],
                cwd=str(self.project_root),  # Run from project root for auth path
                capture_output=True,
                text=True,
                timeout=bluesky_timeout
            )

            elapsed = time.time() - start

            if result.returncode == 0:
                # Extract key info from output (following script's output pattern)
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if any(keyword in line.lower() for keyword in ['saved', 'posts', 'collected', 'session', 'success']):
                        self.print_info(line.strip())

                self.print_success(f"Bluesky script workflow completed in {elapsed:.1f}s")

                # POLARIZATION ANALYSIS: Add political bias to Bluesky posts (already in master_output!)
                session_dir = self.master_output_dir / f"session_{self.timestamp}"
                bluesky_jsonl = session_dir / "homelessness_posts.jsonl"
                output_files = [str(bluesky_jsonl), str(session_dir / "homelessness_posts.csv")]

                if bluesky_jsonl.exists() and bluesky_jsonl.stat().st_size > 10:
                    print(f"{Colors.OKCYAN}➜ Running polarization analysis on Bluesky posts...{Colors.ENDC}")

                    left_keywords = ['progressive', 'liberal', 'democrat', 'social justice', 'equity',
                                    'climate action', 'healthcare for all', 'lgbtq', 'immigrant rights',
                                    'gun control', 'abortion rights', 'blm', 'defund', 'taxing the rich']
                    right_keywords = ['conservative', 'republican', 'traditional', 'freedom', 'liberty',
                                     'border security', 'pro-life', 'second amendment', 'small government',
                                     'law and order', 'patriot', 'maga', 'god', 'family values']

                    posts = []
                    with open(bluesky_jsonl, 'r') as f:
                        for line in f:
                            if line.strip():
                                posts.append(json.loads(line))

                    left_count = right_count = neutral_count = 0
                    for post in posts:
                        text = post.get('text', '').lower()
                        left_matches = sum(1 for kw in left_keywords if kw in text)
                        right_matches = sum(1 for kw in right_keywords if kw in text)

                        total_matches = left_matches + right_matches
                        if total_matches > 0:
                            if left_matches > right_matches:
                                post['political_bias'] = 'LEFT'
                                post['bias_confidence'] = round(left_matches / total_matches, 2)
                                left_count += 1
                            elif right_matches > left_matches:
                                post['political_bias'] = 'RIGHT'
                                post['bias_confidence'] = round(right_matches / total_matches, 2)
                                right_count += 1
                            else:
                                post['political_bias'] = 'NEUTRAL'
                                post['bias_confidence'] = 0.5
                                neutral_count += 1
                        else:
                            post['political_bias'] = 'NEUTRAL'
                            post['bias_confidence'] = 0.0
                            neutral_count += 1

                    # Save updated posts with polarization
                    with open(bluesky_jsonl, 'w') as f:
                        for post in posts:
                            f.write(json.dumps(post) + '\n')

                    print(f"{Colors.OKCYAN}➜ Polarization: LEFT={left_count}, RIGHT={right_count}, NEUTRAL={neutral_count}{Colors.ENDC}")

                    # GENERATE VISUALIZATIONS as SEPARATE PNGs (one widget = one PNG, like Google Trends)
                    print(f"{Colors.OKCYAN}➜ Generating Bluesky visualizations (individual PNGs)...{Colors.ENDC}")
                    try:
                        import pandas as pd
                        import matplotlib.pyplot as plt
                        import matplotlib
                        matplotlib.use('Agg')  # Non-interactive backend
                        from collections import Counter
                        from wordcloud import WordCloud

                        # Load data
                        df = pd.DataFrame(posts)
                        df['created_at_parsed'] = pd.to_datetime(df['created_at'], errors='coerce', utc=True)

                        # Style settings
                        text_color = '#121212'
                        bg_color = 'white'
                        accent_color = '#4a4a4a'
                        left_color = '#4a90e2'
                        right_color = '#e24a4a'

                        viz_count = 0

                        # 1. TIMELINE - Period Data Pulled
                        if 'created_at_parsed' in df.columns and df['created_at_parsed'].notna().any():
                            df['date'] = df['created_at_parsed'].dt.date
                            posts_per_day = df.groupby('date').size().sort_index()

                            fig, ax = plt.subplots(figsize=(10, 4), dpi=100, facecolor=bg_color)
                            ax.plot(posts_per_day.index, posts_per_day.values, color=accent_color, linewidth=2.5, marker='o', markersize=5)
                            ax.fill_between(posts_per_day.index, posts_per_day.values, alpha=0.1, color=accent_color)
                            ax.set_title('Bluesky: Period Data Pulled (Timeline)', fontsize=14, color=text_color, weight='bold', pad=15)
                            ax.set_xlabel('Date', fontsize=10, color='#666666')
                            ax.set_ylabel('Posts', fontsize=10, color='#666666')
                            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
                            plt.tight_layout()
                            viz_path = session_dir / f"bluesky_timeline_{self.timestamp}.png"
                            fig.savefig(viz_path, dpi=100, bbox_inches='tight', facecolor=bg_color)
                            plt.close(fig)
                            output_files.append(str(viz_path))
                            viz_count += 1

                        # 2. CONTENT WORD CLOUD
                        if 'text' in df.columns:
                            text_data = ' '.join(df['text'].dropna().astype(str).head(1000))
                            if text_data.strip():
                                fig, ax = plt.subplots(figsize=(12, 6), dpi=100, facecolor=bg_color)
                                wc = WordCloud(width=1200, height=600, background_color='white',
                                             color_func=lambda *args, **kwargs: accent_color, max_words=80).generate(text_data)
                                ax.imshow(wc, interpolation='bilinear')
                                ax.set_title('Bluesky: Content Word Cloud (All Posts)', fontsize=14, color=text_color, weight='bold', pad=15)
                                ax.axis('off')
                                plt.tight_layout()
                                viz_path = session_dir / f"bluesky_wordcloud_all_{self.timestamp}.png"
                                fig.savefig(viz_path, dpi=100, bbox_inches='tight', facecolor=bg_color)
                                plt.close(fig)
                                output_files.append(str(viz_path))
                                viz_count += 1

                        # 3. POLITICAL POLARIZATION GAUGE
                        left_keywords = ['progressive', 'liberal', 'democrat', 'social justice', 'equity',
                                        'climate action', 'healthcare for all', 'lgbtq', 'immigrant rights']
                        right_keywords = ['conservative', 'republican', 'traditional', 'freedom', 'liberty',
                                         'border security', 'pro-life', 'second amendment', 'law and order']

                        left_texts = []
                        right_texts = []
                        left_polar_count = right_polar_count = 0

                        for text in df['text'].dropna().astype(str):
                            text_lower = text.lower()
                            left_matches = sum(1 for kw in left_keywords if kw in text_lower)
                            right_matches = sum(1 for kw in right_keywords if kw in text_lower)

                            if left_matches > right_matches and left_matches > 0:
                                left_polar_count += 1
                                left_texts.append(text)
                            elif right_matches > left_matches and right_matches > 0:
                                right_polar_count += 1
                                right_texts.append(text)

                        total_polar = left_polar_count + right_polar_count
                        if total_polar > 0:
                            left_pct = (left_polar_count / total_polar) * 100
                            right_pct = (right_polar_count / total_polar) * 100

                            fig, ax = plt.subplots(figsize=(10, 5), dpi=100, facecolor=bg_color)
                            sizes = [left_pct, right_pct]
                            colors = [left_color, right_color]
                            labels = [f'Left-leaning\\n{left_polar_count} posts\\n({left_pct:.1f}%)',
                                     f'Right-leaning\\n{right_polar_count} posts\\n({right_pct:.1f}%)']
                            wedges, texts = ax.pie(sizes, labels=labels, colors=colors, startangle=180,
                                                   wedgeprops={'width': 0.4, 'linewidth': 1, 'edgecolor': 'white'})
                            ax.set_ylim(-1, 0.2)  # Gauge style (half donut)
                            ax.text(0, -0.5, f'{total_polar}\\npolarized posts', ha='center', va='center',
                                   fontsize=12, color='#666666', weight='bold')
                            ax.set_title('Bluesky: Political Polarization Analysis', fontsize=14, color=text_color, weight='bold', pad=15)
                            plt.tight_layout()
                            viz_path = session_dir / f"bluesky_polarization_gauge_{self.timestamp}.png"
                            fig.savefig(viz_path, dpi=100, bbox_inches='tight', facecolor=bg_color)
                            plt.close(fig)
                            output_files.append(str(viz_path))
                            viz_count += 1

                        # 4. LEFT-LEANING WORD CLOUD
                        if len(left_texts) > 0:
                            left_text_data = ' '.join(left_texts)
                            if left_text_data.strip():
                                fig, ax = plt.subplots(figsize=(10, 5), dpi=100, facecolor=bg_color)
                                wc_left = WordCloud(width=1000, height=500, background_color='white',
                                                   color_func=lambda *args, **kwargs: left_color, max_words=60).generate(left_text_data)
                                ax.imshow(wc_left, interpolation='bilinear')
                                ax.set_title(f'Bluesky: Left-Leaning Content ({len(left_texts)} posts)',
                                           fontsize=14, color=left_color, weight='bold', pad=15)
                                ax.axis('off')
                                plt.tight_layout()
                                viz_path = session_dir / f"bluesky_wordcloud_left_{self.timestamp}.png"
                                fig.savefig(viz_path, dpi=100, bbox_inches='tight', facecolor=bg_color)
                                plt.close(fig)
                                output_files.append(str(viz_path))
                                viz_count += 1

                        # 5. RIGHT-LEANING WORD CLOUD
                        if len(right_texts) > 0:
                            right_text_data = ' '.join(right_texts)
                            if right_text_data.strip():
                                fig, ax = plt.subplots(figsize=(10, 5), dpi=100, facecolor=bg_color)
                                wc_right = WordCloud(width=1000, height=500, background_color='white',
                                                    color_func=lambda *args, **kwargs: right_color, max_words=60).generate(right_text_data)
                                ax.imshow(wc_right, interpolation='bilinear')
                                ax.set_title(f'Bluesky: Right-Leaning Content ({len(right_texts)} posts)',
                                           fontsize=14, color=right_color, weight='bold', pad=15)
                                ax.axis('off')
                                plt.tight_layout()
                                viz_path = session_dir / f"bluesky_wordcloud_right_{self.timestamp}.png"
                                fig.savefig(viz_path, dpi=100, bbox_inches='tight', facecolor=bg_color)
                                plt.close(fig)
                                output_files.append(str(viz_path))
                                viz_count += 1

                        # 6. ENGAGEMENT METRICS (Bar chart)
                        if 'like_count' in df.columns:
                            fig, ax = plt.subplots(figsize=(8, 5), dpi=100, facecolor=bg_color)
                            engagement_data = [df['like_count'].sum(), df.get('reply_count', pd.Series([0])).sum(),
                                             df.get('repost_count', pd.Series([0])).sum()]
                            labels = ['Likes', 'Replies', 'Reposts']
                            bars = ax.bar(labels, engagement_data, color=[accent_color, '#5a9bc4', '#8bb8d6'], width=0.6)
                            ax.set_title('Bluesky: Total Engagement Counts', fontsize=14, color=text_color, weight='bold', pad=15)
                            ax.set_ylabel('Count', fontsize=10, color='#666666')
                            for i, v in enumerate(engagement_data):
                                ax.text(i, v, f'{int(v):,}', ha='center', va='bottom', fontsize=9)
                            ax.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.5)
                            plt.tight_layout()
                            viz_path = session_dir / f"bluesky_engagement_totals_{self.timestamp}.png"
                            fig.savefig(viz_path, dpi=100, bbox_inches='tight', facecolor=bg_color)
                            plt.close(fig)
                            output_files.append(str(viz_path))
                            viz_count += 1

                        # 7. HOURLY POSTING PATTERN
                        if 'created_at_parsed' in df.columns and df['created_at_parsed'].notna().any():
                            df['hour'] = df['created_at_parsed'].dt.hour
                            hourly_counts = df.groupby('hour').size()
                            fig, ax = plt.subplots(figsize=(10, 4), dpi=100, facecolor=bg_color)
                            ax.bar(hourly_counts.index, hourly_counts.values, color=accent_color, alpha=0.7, width=0.8)
                            ax.set_title('Bluesky: Hourly Posting Pattern', fontsize=14, color=text_color, weight='bold', pad=15)
                            ax.set_xlabel('Hour (UTC)', fontsize=10, color='#666666')
                            ax.set_ylabel('Posts', fontsize=10, color='#666666')
                            ax.set_xticks(range(0, 24, 3))
                            ax.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.5)
                            plt.tight_layout()
                            viz_path = session_dir / f"bluesky_hourly_pattern_{self.timestamp}.png"
                            fig.savefig(viz_path, dpi=100, bbox_inches='tight', facecolor=bg_color)
                            plt.close(fig)
                            output_files.append(str(viz_path))
                            viz_count += 1

                        # 8. TOP AUTHORS (Horizontal bar)
                        if 'author_handle' in df.columns:
                            author_counts = df['author_handle'].value_counts().head(15)
                            fig, ax = plt.subplots(figsize=(10, 6), dpi=100, facecolor=bg_color)
                            bars = ax.barh(range(len(author_counts)), author_counts.values, color=accent_color, height=0.7)
                            ax.set_yticks(range(len(author_counts)))
                            ax.set_yticklabels([f'@{h}' for h in author_counts.index], fontsize=9)
                            ax.invert_yaxis()
                            ax.set_title('Bluesky: Top 15 Contributors', fontsize=14, color=text_color, weight='bold', pad=15)
                            ax.set_xlabel('Number of Posts', fontsize=10, color='#666666')
                            ax.grid(True, alpha=0.3, axis='x', linestyle='-', linewidth=0.5)
                            plt.tight_layout()
                            viz_path = session_dir / f"bluesky_top_authors_{self.timestamp}.png"
                            fig.savefig(viz_path, dpi=100, bbox_inches='tight', facecolor=bg_color)
                            plt.close(fig)
                            output_files.append(str(viz_path))
                            viz_count += 1

                        print(f"{Colors.OKGREEN}✅ Generated {viz_count} Bluesky visualizations (individual PNGs){Colors.ENDC}")

                    except Exception as viz_error:
                        print(f"{Colors.WARNING}⚠ Visualization failed: {str(viz_error)}{Colors.ENDC}")
                        import traceback
                        traceback.print_exc()

                self.results['bluesky'] = {
                    'status': 'success',
                    'search_terms': homelessness_search_terms,
                    'duration': elapsed,
                    'output_files': output_files
                }
                return True
            else:
                self.print_error(f"Failed: {result.stderr[:200]}")
                self.results['bluesky'] = {'status': 'failed', 'error': result.stderr[:200], 'duration': elapsed}
                return False

        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            self.print_error(f"Timeout ({bluesky_timeout}s)")
            self.results['bluesky'] = {'status': 'timeout', 'duration': elapsed}
            return False
        except Exception as e:
            elapsed = time.time() - start
            self.print_error(f"Error: {str(e)}")
            self.results['bluesky'] = {'status': 'failed', 'error': str(e), 'duration': elapsed}
            return False
        finally:
            # Clean up temp file
            if temp_keywords_file.exists():
                temp_keywords_file.unlink()

    def generate_summary(self):
        """Generate final summary"""
        self.print_header("HOMELESSNESS RESEARCH SCRAPER SUMMARY")

        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        print(f"{Colors.BOLD}Total Duration: {total_duration:.1f} seconds (budget: {self.total_duration}s){Colors.ENDC}\n")
        print(f"{Colors.BOLD}Module Results:{Colors.ENDC}")

        for module, result in self.results.items():
            status = result.get('status', 'unknown')
            duration = result.get('duration', 0)
            budget = self.time_budget.get(module, 0)

            if status == 'success':
                symbol = f"{Colors.OKGREEN}✓{Colors.ENDC}"
                status_text = f"{Colors.OKGREEN}SUCCESS{Colors.ENDC}"
            elif status == 'partial':
                symbol = f"{Colors.WARNING}!{Colors.ENDC}"
                status_text = f"{Colors.WARNING}PARTIAL{Colors.ENDC}"
            else:
                symbol = f"{Colors.FAIL}✗{Colors.ENDC}"
                status_text = f"{Colors.FAIL}FAILED{Colors.ENDC}"

            print(f"  {symbol} {module.upper()}: {status_text} ({duration:.1f}s / {budget}s budget)")

        # Data output locations
        print(f"\n{Colors.BOLD}Output Files (Homelessness Focus):{Colors.ENDC}")

        # Check master output directory for all files
        output_patterns = [
            ('Google Trends Data', self.master_output_dir),
            ('News API Articles', self.master_output_dir),
            ('News API Classified', self.master_output_dir),
            ('Reddit Posts', self.master_output_dir),
            ('Bluesky Data', self.data_dir / 'bluesky' / 'sessions'),
            ('Master Log', self.master_output_dir)
        ]

        for module, path in output_patterns:
            if isinstance(path, Path):
                if path.exists():
                    if path.is_file():
                        size = path.stat().st_size
                        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {module}: {path.name} ({size:,} bytes)")
                    elif path.is_dir():
                        if 'Bluesky' in module:
                            # Look for recent session directories
                            session_dirs = list(path.glob('session_*'))
                            if session_dirs:
                                latest_session = max(session_dirs, key=lambda p: p.stat().st_mtime)
                                jsonl_files = list(latest_session.glob('*.jsonl'))
                                if jsonl_files:
                                    latest_file = max(jsonl_files, key=lambda p: p.stat().st_mtime)
                                    size = latest_file.stat().st_size
                                    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {module}: {latest_file.name} ({size:,} bytes)")
                                else:
                                    print(f"  {Colors.WARNING}!{Colors.ENDC} {module}: Session created but no data files")
                            else:
                                print(f"  {Colors.WARNING}!{Colors.ENDC} {module}: No sessions found")
                        else:
                            # Master output directory - show all files
                            files = list(path.glob('*'))
                        if files:
                                recent_file = max(files, key=lambda p: p.stat().st_mtime)
                                if recent_file.is_file():
                                    size = recent_file.stat().st_size
                                    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {module}: {recent_file.name} ({size:,} bytes)")
                                else:
                                    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {module}: Directory with {len(files)} files")
                                    
                                # Show additional files if there are more than 1
                                if len(files) > 1:
                                    other_files = [f for f in files if f != recent_file][:2]  # Show 2 more
                                    for f in other_files:
                                        if f.is_file():
                                            size = f.stat().st_size
                                            print(f"    └─ {f.name} ({size:,} bytes)")
                                else:
                                    print(f"  {Colors.WARNING}!{Colors.ENDC} {module}: Empty directory")
                else:
                    print(f"  {Colors.WARNING}!{Colors.ENDC} {module}: Not created")

        # Success rate
        successful = sum(1 for r in self.results.values() if r.get('status') in ['success', 'partial'])
        total = len(self.results)
        success_rate = (successful / total * 100) if total > 0 else 0

        print(f"\n{Colors.BOLD}Success Rate: {successful}/{total} ({success_rate:.0f}%){Colors.ENDC}")
        print(f"{Colors.BOLD}Research Focus: Homelessness Crisis{Colors.ENDC}")

    def run(self):
        """Execute all scrapers sequentially with comprehensive data collection"""
        self.print_header(f"COMPREHENSIVE HOMELESSNESS RESEARCH SCRAPER ({self.total_duration}s)")
        print(f"{Colors.BOLD}Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
        print(f"{Colors.BOLD}Time Budget:{Colors.ENDC}")
        for module, budget in self.time_budget.items():
            print(f"  ��� {module.replace('_', ' ').title()}: {budget}s")
        print()

        # Run all modules sequentially
        self.run_google_trends()
        self.run_news_api()
        self.run_reddit()
        self.run_bluesky()

        # Save comprehensive master log
        self.save_master_log()

        # Summary
        self.generate_summary()

def main():
    parser = argparse.ArgumentParser(
        description='NGO Intelligence Platform - Comprehensive Homelessness Research Master Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python master_scraper.py                    # Run with default 60s duration
  python master_scraper.py --duration 120     # Run for 2 minutes
  python master_scraper.py --duration 300     # Run for 5 minutes (comprehensive)
  python master_scraper.py --duration 600     # Run for 10 minutes (extensive)

Research Focus: Homelessness crisis, housing insecurity, affordable housing
        """
    )

    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Total scraping duration in seconds (30-3600, default: 60)'
    )

    args = parser.parse_args()

    orchestrator = HomelessnessMasterOrchestrator(duration_seconds=args.duration)

    try:
        orchestrator.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
        orchestrator.generate_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Fatal error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
