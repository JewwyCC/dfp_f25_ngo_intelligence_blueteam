#!/usr/bin/env python3
"""
NGO Intelligence Platform - Fast Master Scraper (60-second test mode)
Sequential data collection with real-time output

All modules complete in ~60 seconds total
"""

import os
import sys
import json
import subprocess
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

class FastMasterOrchestrator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.scripts_dir = self.project_root / "scripts"
        self.start_time = datetime.now()
        self.results = {}
        self.keywords = []

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

    def run_google_trends_fast(self):
        """Step 1: Quick Google Trends - extract keywords only (5 seconds)"""
        self.print_header("STEP 1/4: GOOGLE TRENDS (FAST MODE - KEYWORDS ONLY)")
        start = time.time()

        try:
            self.print_progress("Reading keyword_theme.xlsx...")

            trends_data_dir = self.scripts_dir / "google_trends" / "data python files"
            keyword_file = trends_data_dir / "keyword_theme.xlsx"

            if keyword_file.exists():
                import pandas as pd
                df = pd.read_excel(keyword_file)

                # Extract all keywords
                for col in df.columns:
                    keywords = df[col].dropna().astype(str).tolist()
                    self.keywords.extend(keywords)

                # Clean and deduplicate
                self.keywords = list(set([k.strip() for k in self.keywords if k.strip() and len(k.strip()) > 2]))

                elapsed = time.time() - start
                self.print_success(f"Extracted {len(self.keywords)} keywords in {elapsed:.1f}s")
                self.print_info(f"Sample: {', '.join(self.keywords[:5])}")

                self.results['google_trends'] = {
                    'status': 'success',
                    'keywords_extracted': len(self.keywords),
                    'duration': elapsed
                }
                return True
            else:
                self.print_error("keyword_theme.xlsx not found")
                # Use defaults
                self.keywords = ['homelessness', 'housing crisis', 'affordable housing', 'homeless shelter']
                self.print_info(f"Using {len(self.keywords)} default keywords")

                self.results['google_trends'] = {
                    'status': 'partial',
                    'keywords_extracted': len(self.keywords),
                    'duration': time.time() - start
                }
                return True

        except Exception as e:
            elapsed = time.time() - start
            self.print_error(f"Error: {str(e)}")
            self.keywords = ['homelessness', 'housing crisis', 'affordable housing']
            self.results['google_trends'] = {'status': 'failed', 'error': str(e), 'duration': elapsed}
            return False

    def run_news_api_fast(self):
        """Step 2: News API - Quick test with 10 articles (15 seconds)"""
        self.print_header("STEP 2/4: NEWS API (FAST MODE - 10 ARTICLES)")
        start = time.time()

        if not self.keywords:
            self.keywords = ['homelessness', 'housing crisis']

        # Limit to top 3 keywords for speed
        test_keywords = self.keywords[:3]

        self.print_progress(f"Fetching articles for: {', '.join(test_keywords)}")

        wrapper_code = f"""
import sys
sys.path.insert(0, r'{self.scripts_dir / "news_api"}')

try:
    from NewsAPI_Scrape import NewsAPIScraper
    from HF_Classifier import PoliticalClassifier
    from credentials import NEWSAPI_KEY, HUGGINGFACE_TOKEN
    import json
    import os
    import signal

    # Timeout handler for classifier
    def timeout_handler(signum, frame):
        raise TimeoutError('Classification timeout')

    keywords = {test_keywords}
    scraper = NewsAPIScraper(NEWSAPI_KEY)

    # Fast mode: only 10 articles
    articles = scraper.fetch_articles(keywords=keywords, page_size=10)
    print(f"SUCCESS: Collected {{len(articles)}} articles")

    # Save raw articles
    output_file = r'{self.data_dir / "news_api" / "news_articles_fast.json"}'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(articles, f, indent=2)

    print(f"Saved to {{output_file}}")

    # Try classification with strict timeout (max 10 seconds total)
    if len(articles) > 0:
        print("Classifying political bias (max 10s)...")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout

        try:
            classifier = PoliticalClassifier(huggingface_token=HUGGINGFACE_TOKEN)

            # Classify only first article to stay within timeout
            classified = []
            article = articles[0]
            text = article.get('title', '') + ' ' + article.get('description', '')
            result = classifier.classify_text(text)

            signal.alarm(0)  # Cancel alarm

            if result:
                classified.append({{
                    'title': article.get('title', ''),
                    'label': result.get('label'),
                    'confidence': result.get('score', 0)
                }})

                print(f"Classified: {{result.get('label')}} (confidence: {{result.get('score', 0):.2f}})")

                # Save classification
                class_file = r'{self.data_dir / "news_api" / "classified_fast.json"}'
                with open(class_file, 'w') as f:
                    json.dump(classified, f, indent=2)
            else:
                print("Classification: No result")

        except TimeoutError:
            signal.alarm(0)
            print("Classification: Timeout - skipped")
        except Exception as e:
            signal.alarm(0)
            print(f"Classification: Skipped ({{type(e).__name__}})")

except Exception as e:
    print(f"ERROR: {{str(e)}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""

        try:
            result = subprocess.run(
                [sys.executable, '-c', wrapper_code],
                capture_output=True,
                text=True,
                timeout=20
            )

            elapsed = time.time() - start

            if result.returncode == 0:
                # Print output line by line
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.print_info(line)

                self.print_success(f"News API completed in {elapsed:.1f}s")
                self.results['news_api'] = {
                    'status': 'success',
                    'keywords_used': len(test_keywords),
                    'duration': elapsed
                }
                return True
            else:
                self.print_error(f"Failed: {result.stderr}")
                self.results['news_api'] = {'status': 'failed', 'error': result.stderr, 'duration': elapsed}
                return False

        except Exception as e:
            elapsed = time.time() - start
            self.print_error(f"Error: {str(e)}")
            self.results['news_api'] = {'status': 'failed', 'error': str(e), 'duration': elapsed}
            return False

    def run_reddit_fast(self):
        """Step 3: Reddit - Quick test with 20 posts (15 seconds)"""
        self.print_header("STEP 3/4: REDDIT (FAST MODE - 20 POSTS)")
        start = time.time()

        if not self.keywords:
            self.keywords = ['homelessness']

        # Limit to 2 keywords for speed
        test_keywords = self.keywords[:2]

        self.print_progress(f"Collecting posts for: {', '.join(test_keywords)}")

        wrapper_code = f"""
import sys
sys.path.insert(0, r'{self.scripts_dir / "reddit"}')

try:
    from config import RedditAuth, ISSUE_CONFIGS
    import praw
    from data_collection import collect_with_even_distribution
    import pandas as pd
    import os

    # Initialize Reddit
    reddit = praw.Reddit(
        client_id=RedditAuth.client_id,
        client_secret=RedditAuth.client_secret,
        user_agent=RedditAuth.user_agent
    )

    # Use Housing/Homelessness config
    config = ISSUE_CONFIGS['Housing/Homelessness']

    # Fast mode: only 2 subreddits, 10 posts each
    subreddits = config['subreddits'][:2]
    keywords = {test_keywords}

    print(f"Collecting from: {{', '.join(subreddits)}}")

    posts = collect_with_even_distribution(
        reddit=reddit,
        subreddits=subreddits,
        keywords=keywords,
        posts_per_sub=10,  # Only 10 posts per subreddit
        time_filter='week',
        strategy='balanced'
    )

    print(f"SUCCESS: Collected {{len(posts)}} posts")

    # Save
    output_file = r'{self.data_dir / "reddit" / "reddit_posts_fast.csv"}'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    df = pd.DataFrame(posts)
    df.to_csv(output_file, index=False)

    print(f"Saved to {{output_file}}")

except Exception as e:
    print(f"ERROR: {{str(e)}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""

        try:
            result = subprocess.run(
                [sys.executable, '-c', wrapper_code],
                capture_output=True,
                text=True,
                timeout=20
            )

            elapsed = time.time() - start

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.print_info(line)

                self.print_success(f"Reddit completed in {elapsed:.1f}s")
                self.results['reddit'] = {
                    'status': 'success',
                    'keywords_used': len(test_keywords),
                    'duration': elapsed
                }
                return True
            else:
                self.print_error(f"Failed: {result.stderr}")
                self.results['reddit'] = {'status': 'failed', 'error': result.stderr, 'duration': elapsed}
                return False

        except Exception as e:
            elapsed = time.time() - start
            self.print_error(f"Error: {str(e)}")
            self.results['reddit'] = {'status': 'failed', 'error': str(e), 'duration': elapsed}
            return False

    def run_bluesky_fast(self):
        """Step 4: Bluesky - Quick test with 50 posts (25 seconds)"""
        self.print_header("STEP 4/4: BLUESKY (FAST MODE - 50 POSTS, 1 DAY)")
        start = time.time()

        if not self.keywords:
            self.keywords = ['homelessness']

        # Use top 3 keywords
        test_keywords = self.keywords[:3]

        self.print_progress(f"Searching Bluesky for: {', '.join(test_keywords)}")

        # Create temporary keywords file
        temp_keywords_file = self.scripts_dir / "bluesky" / "temp_keywords_fast.txt"
        with open(temp_keywords_file, 'w') as f:
            f.write('\n'.join(test_keywords))

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.scripts_dir / "bluesky" / "bluesky_social_justice_collector.py"),
                    '--method', 'search',
                    '--days-back', '1',  # Only 1 day
                    '--max-posts', '50'   # Only 50 posts
                ],
                cwd=str(self.project_root),  # Run from project root for auth path
                capture_output=True,
                text=True,
                timeout=45  # Increased timeout
            )

            elapsed = time.time() - start

            if result.returncode == 0:
                # Extract key info from output
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if any(keyword in line.lower() for keyword in ['saved', 'posts', 'collected', 'session']):
                        self.print_info(line.strip())

                self.print_success(f"Bluesky completed in {elapsed:.1f}s")
                self.results['bluesky'] = {
                    'status': 'success',
                    'keywords_used': len(test_keywords),
                    'duration': elapsed
                }
                return True
            else:
                self.print_error(f"Failed: {result.stderr[:200]}")
                self.results['bluesky'] = {'status': 'failed', 'error': result.stderr[:200], 'duration': elapsed}
                return False

        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            self.print_error("Timeout (30s)")
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
        self.print_header("FAST SCRAPER SUMMARY")

        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        print(f"{Colors.BOLD}Total Duration: {total_duration:.1f} seconds{Colors.ENDC}\n")
        print(f"{Colors.BOLD}Module Results:{Colors.ENDC}")

        for module, result in self.results.items():
            status = result.get('status', 'unknown')
            duration = result.get('duration', 0)

            if status == 'success':
                symbol = f"{Colors.OKGREEN}✓{Colors.ENDC}"
                status_text = f"{Colors.OKGREEN}SUCCESS{Colors.ENDC}"
            elif status == 'partial':
                symbol = f"{Colors.WARNING}!{Colors.ENDC}"
                status_text = f"{Colors.WARNING}PARTIAL{Colors.ENDC}"
            else:
                symbol = f"{Colors.FAIL}✗{Colors.ENDC}"
                status_text = f"{Colors.FAIL}FAILED{Colors.ENDC}"

            print(f"  {symbol} {module.upper()}: {status_text} ({duration:.1f}s)")

        # Data output locations
        print(f"\n{Colors.BOLD}Output Files:{Colors.ENDC}")

        output_files = [
            ('Google Trends', 'Keywords extracted (in memory)'),
            ('News API', self.data_dir / 'news_api' / 'news_articles_fast.json'),
            ('Reddit', self.data_dir / 'reddit' / 'reddit_posts_fast.csv'),
            ('Bluesky', self.data_dir / 'bluesky' / 'alltime_socmed' / 'socmed_search_*.csv')
        ]

        for module, path in output_files:
            if isinstance(path, str):
                print(f"  • {module}: {path}")
            elif isinstance(path, Path) and path.exists():
                size = path.stat().st_size
                print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {module}: {path} ({size:,} bytes)")
            elif isinstance(path, Path):
                # Check with glob for Bluesky
                if '*' in str(path):
                    matching = list(path.parent.glob(path.name))
                    if matching:
                        latest = max(matching, key=lambda p: p.stat().st_mtime)
                        size = latest.stat().st_size
                        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {module}: {latest.name} ({size:,} bytes)")
                    else:
                        print(f"  {Colors.WARNING}!{Colors.ENDC} {module}: Not found")
                else:
                    print(f"  {Colors.WARNING}!{Colors.ENDC} {module}: {path} (not created)")

        # Success rate
        successful = sum(1 for r in self.results.values() if r.get('status') == 'success')
        total = len(self.results)
        success_rate = (successful / total * 100) if total > 0 else 0

        print(f"\n{Colors.BOLD}Success Rate: {successful}/{total} ({success_rate:.0f}%){Colors.ENDC}")

    def run(self):
        """Execute all scrapers sequentially in fast mode"""
        self.print_header("FAST MASTER SCRAPER - 60 SECOND TEST")
        print(f"{Colors.BOLD}Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")

        # Run all modules
        self.run_google_trends_fast()
        self.run_news_api_fast()
        self.run_reddit_fast()
        self.run_bluesky_fast()

        # Summary
        self.generate_summary()

def main():
    orchestrator = FastMasterOrchestrator()

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
