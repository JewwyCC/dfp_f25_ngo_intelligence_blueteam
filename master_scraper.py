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
        """Copy Google Trends output files to master output directory"""
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
                recent_files = sorted(all_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
                for src_file in recent_files:
                    dst_file = session_dir / src_file.name
                    import shutil
                    shutil.copy2(src_file, dst_file)
                    copied_files.append(str(dst_file))
            
            # Also copy visualization files if they exist
            viz_dir = self.project_root / "viz" / "google_trends"
            if viz_dir.exists():
                viz_files = list(viz_dir.glob("*"))
                if viz_files:
                    recent_viz = sorted(viz_files, key=lambda p: p.stat().st_mtime, reverse=True)[:3]
                    for src_file in recent_viz:
                        dst_file = session_dir / f"viz_{src_file.name}"
                        import shutil
                        shutil.copy2(src_file, dst_file)
                        copied_files.append(str(dst_file))

        except Exception as e:
            self.log_entry('google_trends', 'warning', f'Error copying output files: {str(e)}')
            
        return copied_files

    def copy_bluesky_outputs(self):
        """Copy Bluesky output files to master_output with session format and rename to homelessness"""
        copied_files = []
        try:
            # Find the most recent Bluesky session (created after our session started)
            bluesky_sessions_dir = self.data_dir / "bluesky" / "sessions"
            if bluesky_sessions_dir.exists():
                session_dirs = [d for d in bluesky_sessions_dir.iterdir() if d.is_dir()]
                if session_dirs:
                    # Get sessions created after our start time
                    session_start_time = self.start_time.timestamp()
                    recent_sessions = [d for d in session_dirs if d.stat().st_mtime > session_start_time]
                    
                    if recent_sessions:
                        # Get the most recent session created during our run
                        latest_session = max(recent_sessions, key=lambda p: p.stat().st_mtime)
                        
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
                        self.log_entry('bluesky', 'warning', 'No new Bluesky sessions created during this run - skipping copy')
                        # Create empty placeholder files to indicate no data
                        master_session_dir = self.master_output_dir / f"session_{self.timestamp}"
                        master_session_dir.mkdir(exist_ok=True)
                        
                        # Create empty placeholder files
                        placeholder_files = [
                            "homelessness_posts.jsonl",
                            "homelessness_posts.csv"
                        ]
                        
                        for filename in placeholder_files:
                            placeholder_file = master_session_dir / filename
                            placeholder_file.write_text("[]" if filename.endswith('.jsonl') else "text,created_at,author_handle\n")
                            copied_files.append(str(placeholder_file))

        except Exception as e:
            self.log_entry('bluesky', 'warning', f'Error copying Bluesky output files: {str(e)}')
            
        return copied_files

    def run_news_api(self):
        """Step 2: News API - HUNGRY SCRAPER using EXACT script configuration"""
        self.print_header(f"STEP 2/4: NEWS API (HOMELESSNESS ARTICLES - {self.time_budget['news_api']}s)")
        start = time.time()

        self.log_entry('news_api', 'info', f"Starting News API scraping with {self.time_budget['news_api']}s budget")

        # Use EXACT keywords from news_configs.py - BE HUNGRY!
        from scripts.news_api.news_configs import KEYWORDS_DEFAULT, MAX_PAGES
        
        # Use targeted homelessness keywords (filter Google Trends keywords)
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

        wrapper_code = f"""
import sys
sys.path.insert(0, r'{self.scripts_dir / "news_api"}')

try:
    from NewsAPI_Scrape import NewsAPIScraper
    from HF_Classifier import PoliticalClassifier
    from credentials import NEWSAPI_KEY, HUGGINGFACE_TOKEN
    from news_configs import KEYWORDS_DEFAULT, MAX_PAGES
    import json
    import os
    import signal
    import time

    # Timeout handler for classifier
    def timeout_handler(signum, frame):
        raise TimeoutError('Classification timeout')

    # Use EXACT keywords from config + Google Trends keywords
    keywords = {repr(combined_keywords)}
    timestamp = '{self.timestamp}'
    scraper = NewsAPIScraper(NEWSAPI_KEY)

    print(f"HUNGRY SCRAPER: Using {{len(keywords)}} keywords, targeting {num_articles} articles")

    # Use the EXACT same method as the NewsAPI_Scrape.py script
    all_articles = scraper.fetch_articles(keywords=keywords, page_size={num_articles})
    
    # Filter articles to ensure they're actually about homelessness
    homelessness_terms = ['homeless', 'homelessness', 'unhoused', 'housing crisis', 'affordable housing', 'eviction', 'shelter', 'tent city', 'encampment', 'housing insecurity']
    articles = []
    for article in all_articles:
        text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        if any(term in text for term in homelessness_terms):
            articles.append(article)
    
    print(f"SUCCESS: Collected {{len(articles)}} homelessness articles (filtered from {{len(all_articles)}} total)")

    # Save to MASTER OUTPUT directory
    # Save to master output directory with session format
    session_dir = '{self.master_output_dir}/session_{self.timestamp}'
    os.makedirs(session_dir, exist_ok=True)
    output_file = f'{{session_dir}}/news_api_articles.json'

    with open(output_file, 'w') as f:
        json.dump(articles, f, indent=2)

    # Save CSV to master output
    csv_file = f'{{session_dir}}/news_api_articles.csv'
    import pandas as pd
    if articles:
        df = pd.DataFrame(articles)
    else:
        df = pd.DataFrame(columns=['title', 'description', 'url', 'publishedAt', 'source'])
    df.to_csv(csv_file, index=False)
    print(f"CSV: {{csv_file}}")
    print(f"JSON: {{output_file}}")

    # DUAL CLASSIFICATION: Compare HuggingFace vs Keyword-based (like Bluesky)
    if len(articles) > 0:
        print(f"DUAL CLASSIFIER: Analyzing {{min(len(articles), 5)}} articles...")
        
        # Keyword-based classification (like Bluesky polarization analysis)
        left_keywords = ['progressive', 'liberal', 'democrat', 'social justice', 'equity',
                        'climate action', 'healthcare for all', 'lgbtq', 'immigrant rights',
                        'gun control', 'abortion rights', 'blm', 'defund', 'taxing the rich',
                        'minimum wage', 'union', 'workers rights', 'environmental', 'renewable']
        right_keywords = ['conservative', 'republican', 'traditional', 'freedom', 'liberty',
                         'border security', 'pro-life', 'second amendment', 'small government',
                         'law and order', 'patriot', 'maga', 'god', 'family values',
                         'deregulation', 'free market', 'capitalism', 'tax cuts', 'business']

        def keyword_classify(text):
            text_lower = text.lower()
            left_matches = sum(1 for kw in left_keywords if kw in text_lower)
            right_matches = sum(1 for kw in right_keywords if kw in text_lower)
            
            if left_matches > right_matches and left_matches > 0:
                return 'LEFT', left_matches / (left_matches + right_matches)
            elif right_matches > left_matches and right_matches > 0:
                return 'RIGHT', right_matches / (left_matches + right_matches)
            else:
                return 'NEUTRAL', 0.5

        # HuggingFace classification (with timeout)
        hf_classified = []
        keyword_classified = []
        
        print("Method 1: Keyword-based classification (fast)")
        start_keyword = time.time()
        
        for i, article in enumerate(articles[:5]):
                text = article.get('title', '') + ' ' + article.get('description', '')
                label, confidence = keyword_classify(text)
                
                keyword_classified.append({{
                    'title': article.get('title', ''),
                    'method': 'keyword',
                    'label': label,
                    'confidence': confidence,
                    'source': article.get('source', {{}}).get('name', 'Unknown')
                }})
                print(f"Keyword {{i+1}}: {{label}} ({{confidence:.2f}})")
        
        keyword_time = time.time() - start_keyword
        
        print("Method 2: HuggingFace classification (slow)")
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout

        try:
            start_hf = time.time()
            classifier = PoliticalClassifier(huggingface_token=HUGGINGFACE_TOKEN)

            for i, article in enumerate(articles[:5]):
            text = article.get('title', '') + ' ' + article.get('description', '')
            result = classifier.classify_text(text)

            if result:
                    hf_classified.append({{
                    'title': article.get('title', ''),
                        'method': 'huggingface',
                    'label': result.get('label'),
                        'confidence': result.get('score', 0),
                        'source': article.get('source', {{}}).get('name', 'Unknown')
                    }})
                    print(f"HF {{i+1}}: {{result.get('label')}} ({{result.get('score', 0):.2f}})")
            
            hf_time = time.time() - start_hf
            signal.alarm(0)  # Cancel alarm

        except TimeoutError:
            signal.alarm(0)
            hf_time = 10  # Timeout time
            print("HuggingFace: Timeout - skipped")
        except Exception as e:
            signal.alarm(0)
            hf_time = 10  # Error time
            print(f"HuggingFace: Skipped ({{type(e).__name__}})")

        # Compare results
        print(f"\\nPERFORMANCE COMPARISON:")
        print(f"Keyword method: {{keyword_time:.2f}}s ({{len(keyword_classified)}} results)")
        print(f"HuggingFace method: {{hf_time:.2f}}s ({{len(hf_classified)}} results)")
        if keyword_time > 0:
            print(f"Speed improvement: {{hf_time/keyword_time:.1f}}x faster")
        
        # Save both results
        all_classified = keyword_classified + hf_classified
        
        if all_classified:
            class_json = f'{{session_dir}}/news_api_classified.json'
            with open(class_json, 'w') as f:
                json.dump(all_classified, f, indent=2)

            class_csv = f'{{session_dir}}/news_api_classified.csv'
            pd.DataFrame(all_classified).to_csv(class_csv, index=False)
            print(f"Dual classification saved: {{class_json}}")
        else:
            print("Classification: No results")

except Exception as e:
    print(f"ERROR: {{str(e)}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""

        try:
            result = subprocess.run(
                [sys.executable, '-c', wrapper_code],
                cwd=str(self.project_root),  # Run from project root for proper imports
                capture_output=True,
                text=True,
                timeout=self.time_budget['news_api'] + 10
            )

            elapsed = time.time() - start

            if result.returncode == 0:
                # Print output line by line
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.print_info(line)
                        self.log_entry('news_api', 'info', line.strip())

                self.print_success(f"🦁 HUNGRY News API completed in {elapsed:.1f}s")
                self.log_entry('news_api', 'success', f"News API scraping completed", {
                    'duration': elapsed,
                    'keywords_used': len(combined_keywords),
                    'articles_collected': 'see output files'
                })
                
                self.results['news_api'] = {
                    'status': 'success',
                    'keywords_used': len(combined_keywords),
                    'duration': elapsed
                }
                return True
            else:
                self.print_error(f"Failed: {result.stderr}")
                self.log_entry('news_api', 'error', 'News API execution failed', {'stderr': result.stderr})
                self.results['news_api'] = {'status': 'failed', 'error': result.stderr, 'duration': elapsed}
                return False

        except Exception as e:
            elapsed = time.time() - start
            self.print_error(f"Error: {str(e)}")
            self.log_entry('news_api', 'error', f'Exception: {str(e)}')
            self.results['news_api'] = {'status': 'failed', 'error': str(e), 'duration': elapsed}
            return False

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
    posts = collect_with_even_distribution(
        reddit=reddit,
        subreddits=subreddits,
        keywords=keywords,
        posts_per_sub={posts_per_sub},
        time_filter='month',
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
        """Step 4: Bluesky - Run EXACT script workflow"""
        self.print_header(f"STEP 4/4: BLUESKY (HOMELESSNESS SEARCH - {self.time_budget['bluesky']}s)")
        start = time.time()

        # Use EXACT keywords from successful test (3 broad terms)
        homelessness_search_terms = ['homeless', 'unhoused', 'housing crisis']

        # Use settings from successful test (50 posts per keyword, 3 days back)
        max_posts = 50
        days_back = 3

        self.print_progress(f"Running Bluesky script workflow")
        self.print_progress(f"Searching for homelessness ({max_posts} posts, {days_back} days)")
        self.print_progress(f"Search terms: {', '.join(homelessness_search_terms)}")

        # Create temporary keywords file with comprehensive homelessness terms
        temp_keywords_file = self.scripts_dir / "bluesky" / "temp_homelessness_keywords.txt"
        with open(temp_keywords_file, 'w') as f:
            f.write('\n'.join(homelessness_search_terms))

        try:
            # Create homelessness-focused Bluesky wrapper
            homelessness_wrapper_code = f'''
import sys
import os
import json
import pandas as pd
from datetime import datetime
sys.path.append('{self.scripts_dir}/bluesky')

try:
    # Override the keywords to focus on homelessness
    from bluesky_social_justice_collector import BlueskySocialJusticeCollector, CollectionConfig

    # Create homelessness-focused config  
    # Use SEARCH with broad keywords for better results
    import time as time_module
    session_timestamp = time_module.strftime("%Y%m%d_%H%M%S", time_module.localtime())
    
    config = CollectionConfig(
        method='search',
        max_posts_per_keyword={max_posts},
        days_back={days_back},
        session_name='homelessness_session_' + session_timestamp
    )

    # Create collector and FORCE homelessness keywords
    collector = BlueskySocialJusticeCollector(config)
    
    # CRITICAL: Override keywords BEFORE any initialization (EXACT test setup)
    collector.keywords = {homelessness_search_terms}
    collector.search_queries = {{
        'homeless': ['"homeless"', '#homeless'],
        'unhoused': ['"unhoused"'],
        'housing crisis': ['"housing crisis"', '#housingcrisis']
    }}
    
    print(f"HOMELESSNESS FOCUS: Using {{len(collector.keywords)}} homelessness keywords")
    print(f"Keywords: {{collector.keywords[:5]}}...")

    # Run the collection
    collector.run()
    
    # Convert JSONL to CSV for homelessness data
    session_dir = collector.session_dir
    jsonl_files = [f for f in os.listdir(session_dir) if f.endswith('.jsonl')]
    
    for jsonl_file in jsonl_files:
        jsonl_path = os.path.join(session_dir, jsonl_file)
        csv_path = jsonl_path.replace('.jsonl', '.csv')
        
        # Read JSONL and convert to CSV
        posts = []
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    posts.append(json.loads(line))
        
        if posts:
            df = pd.DataFrame(posts)
            df.to_csv(csv_path, index=False)
            print(f"Created CSV: {{csv_path}} with {{len(posts)}} homelessness posts")
    
    print("Bluesky homelessness collection completed successfully!")
    
except Exception as e:
    print(f"Error in Bluesky wrapper: {{str(e)}}")
    import traceback
    traceback.print_exc()
'''
            
            # Run the homelessness-focused Bluesky wrapper
            result = subprocess.run(
                [sys.executable, '-c', homelessness_wrapper_code],
                cwd=str(self.project_root),  # Run from project root for auth path
                capture_output=True,
                text=True,
                timeout=180  # Very patient timeout for Bluesky search collection
            )

            elapsed = time.time() - start

            if result.returncode == 0:
                # Extract key info from output (following script's output pattern)
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if any(keyword in line.lower() for keyword in ['saved', 'posts', 'collected', 'session', 'success']):
                        self.print_info(line.strip())

                self.print_success(f"Bluesky script workflow completed in {elapsed:.1f}s")
                
                # Copy Bluesky output to master_output with session format
                output_files = self.copy_bluesky_outputs()
                
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
            self.print_error(f"Timeout ({self.time_budget['bluesky']}s)")
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
