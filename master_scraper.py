#!/usr/bin/env python3
"""
NGO Intelligence Platform - Master Scraper Orchestrator
Sequential data collection from all sources

Execution Order:
1. Google Trends (gets keywords and zipcodes)
2. News API (uses keywords from Google Trends)
3. Reddit (uses keywords from Google Trends)
4. Bluesky (uses keywords from Google Trends)

Each module runs to completion with status reporting before the next begins.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
import signal

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
    UNDERLINE = '\033[4m'

class MasterOrchestrator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.scripts_dir = self.project_root / "scripts"
        self.start_time = datetime.now()
        self.results = {}

        # Shared data between modules
        self.keywords = []
        self.zipcodes = []

    def print_header(self, message):
        """Print formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
        print(f"{message:^80}")
        print(f"{'='*80}{Colors.ENDC}\n")

    def print_success(self, message):
        """Print success message"""
        print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

    def print_error(self, message):
        """Print error message"""
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

    def print_info(self, message):
        """Print info message"""
        print(f"{Colors.OKCYAN}➜ {message}{Colors.ENDC}")

    def print_warning(self, message):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

    def run_google_trends(self):
        """
        Step 1: Run Google Trends scraper
        Extracts keywords and zipcodes for other modules
        """
        self.print_header("STEP 1/4: GOOGLE TRENDS DATA COLLECTION")

        script_path = self.scripts_dir / "google_trends" / "googletrends.py"

        if not script_path.exists():
            self.print_error(f"Google Trends script not found: {script_path}")
            return False

        self.print_info("Starting Google Trends data collection...")
        self.print_info("This will collect trend data and extract keywords for downstream modules")

        try:
            # Run the script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(script_path.parent),
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )

            if result.returncode == 0:
                self.print_success("Google Trends collection completed successfully")

                # Extract keywords from Google Trends data files
                self._extract_keywords_from_trends()

                self.results['google_trends'] = {
                    'status': 'success',
                    'timestamp': datetime.now().isoformat(),
                    'keywords_extracted': len(self.keywords),
                    'zipcodes_extracted': len(self.zipcodes)
                }
                return True
            else:
                self.print_error(f"Google Trends collection failed with return code {result.returncode}")
                self.print_error(f"Error: {result.stderr}")
                self.results['google_trends'] = {
                    'status': 'failed',
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
                return False

        except subprocess.TimeoutExpired:
            self.print_error("Google Trends collection timed out (30 minutes)")
            return False
        except Exception as e:
            self.print_error(f"Google Trends collection error: {str(e)}")
            return False

    def _extract_keywords_from_trends(self):
        """Extract keywords and zipcodes from Google Trends output"""
        try:
            # Try to load keywords from the Excel file
            trends_data_dir = self.scripts_dir / "google_trends" / "data python files"
            keyword_file = trends_data_dir / "keyword_theme.xlsx"
            zipcode_file = trends_data_dir / "uszips.csv"

            if keyword_file.exists():
                import pandas as pd
                df = pd.read_excel(keyword_file)

                # Extract keywords from all columns
                for col in df.columns:
                    keywords_in_col = df[col].dropna().astype(str).tolist()
                    self.keywords.extend(keywords_in_col)

                # Remove duplicates and clean
                self.keywords = list(set([k.strip() for k in self.keywords if k.strip()]))

                self.print_success(f"Extracted {len(self.keywords)} unique keywords from Google Trends")
            else:
                self.print_warning(f"Keyword file not found: {keyword_file}")
                # Use default homelessness keywords
                self.keywords = [
                    'homelessness', 'homeless', 'housing crisis', 'affordable housing',
                    'homeless shelter', 'unhoused', 'housing insecurity', 'eviction'
                ]
                self.print_info(f"Using {len(self.keywords)} default keywords")

            # Extract zipcodes
            if zipcode_file.exists():
                import pandas as pd
                df_zip = pd.read_csv(zipcode_file)
                if 'zip' in df_zip.columns:
                    self.zipcodes = df_zip['zip'].dropna().astype(str).tolist()[:100]  # Limit to 100 for performance
                    self.print_success(f"Extracted {len(self.zipcodes)} zipcodes")

        except Exception as e:
            self.print_warning(f"Could not extract keywords/zipcodes: {str(e)}")
            # Use defaults
            self.keywords = [
                'homelessness', 'homeless', 'housing crisis', 'affordable housing',
                'homeless shelter', 'unhoused', 'housing insecurity', 'eviction'
            ]
            self.print_info(f"Using {len(self.keywords)} default keywords")

    def run_news_api(self):
        """
        Step 2: Run News API scraper
        Uses keywords from Google Trends
        """
        self.print_header("STEP 2/4: NEWS API DATA COLLECTION")

        if not self.keywords:
            self.print_warning("No keywords from Google Trends, using defaults")
            self.keywords = ['homelessness', 'housing crisis', 'affordable housing']

        script_path = self.scripts_dir / "news_api" / "NewsAPI_Scrape.py"

        if not script_path.exists():
            self.print_error(f"News API script not found: {script_path}")
            return False

        self.print_info(f"Starting News API collection with {len(self.keywords)} keywords")
        self.print_info(f"Keywords: {', '.join(self.keywords[:5])}...")

        try:
            # Add the news_api directory to Python path and run
            env = os.environ.copy()
            env['PYTHONPATH'] = str(script_path.parent) + os.pathsep + env.get('PYTHONPATH', '')

            # Create a wrapper script that runs the news scraper
            wrapper_code = f"""
import sys
sys.path.insert(0, r'{script_path.parent}')
from NewsAPI_Scrape import NewsAPIScraper
from credentials import NEWSAPI_KEY
import json

keywords = {self.keywords}
scraper = NewsAPIScraper(NEWSAPI_KEY)
articles = scraper.fetch_articles(keywords=keywords)

print(f"Collected {{len(articles)}} articles")

# Save to file
output_file = r'{self.data_dir / "news_api" / "news_articles.json"}'
import os
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, 'w') as f:
    json.dump(articles, f, indent=2)

print(f"Saved to {{output_file}}")
"""

            result = subprocess.run(
                [sys.executable, '-c', wrapper_code],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode == 0:
                self.print_success("News API collection completed successfully")
                self.print_info(result.stdout.strip())

                self.results['news_api'] = {
                    'status': 'success',
                    'timestamp': datetime.now().isoformat(),
                    'keywords_used': len(self.keywords)
                }
                return True
            else:
                self.print_error(f"News API collection failed: {result.stderr}")
                self.results['news_api'] = {
                    'status': 'failed',
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
                return False

        except subprocess.TimeoutExpired:
            self.print_error("News API collection timed out (10 minutes)")
            return False
        except Exception as e:
            self.print_error(f"News API collection error: {str(e)}")
            return False

    def run_reddit(self):
        """
        Step 3: Run Reddit scraper
        Uses keywords from Google Trends
        """
        self.print_header("STEP 3/4: REDDIT DATA COLLECTION")

        if not self.keywords:
            self.print_warning("No keywords from Google Trends, using defaults")
            self.keywords = ['homelessness', 'housing crisis']

        script_path = self.scripts_dir / "reddit" / "data_collection.py"

        if not script_path.exists():
            self.print_error(f"Reddit script not found: {script_path}")
            return False

        self.print_info(f"Starting Reddit collection with {len(self.keywords)} keywords")

        try:
            # Create wrapper to run Reddit scraper
            wrapper_code = f"""
import sys
sys.path.insert(0, r'{script_path.parent}')
from config import RedditAuth, ISSUE_CONFIGS
import praw
from data_collection import collect_with_even_distribution
import pandas as pd

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=RedditAuth.client_id,
    client_secret=RedditAuth.client_secret,
    user_agent=RedditAuth.user_agent
)

# Use homelessness config
config = ISSUE_CONFIGS['homelessness']
keywords = {self.keywords[:10]}  # Limit to 10 keywords for Reddit

# Collect data
print(f"Collecting from {{len(config['subreddits'])}} subreddits...")
posts = collect_with_even_distribution(
    reddit=reddit,
    subreddits=config['subreddits'],
    keywords=keywords,
    posts_per_sub=100,
    time_filter='month',
    strategy='balanced'
)

print(f"Collected {{len(posts)}} posts from Reddit")

# Save to file
output_file = r'{self.data_dir / "reddit" / "reddit_posts.csv"}'
import os
os.makedirs(os.path.dirname(output_file), exist_ok=True)

df = pd.DataFrame(posts)
df.to_csv(output_file, index=False)

print(f"Saved to {{output_file}}")
"""

            result = subprocess.run(
                [sys.executable, '-c', wrapper_code],
                capture_output=True,
                text=True,
                timeout=1200  # 20 minute timeout
            )

            if result.returncode == 0:
                self.print_success("Reddit collection completed successfully")
                self.print_info(result.stdout.strip())

                self.results['reddit'] = {
                    'status': 'success',
                    'timestamp': datetime.now().isoformat(),
                    'keywords_used': len(self.keywords[:10])
                }
                return True
            else:
                self.print_error(f"Reddit collection failed: {result.stderr}")
                self.results['reddit'] = {
                    'status': 'failed',
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
                return False

        except subprocess.TimeoutExpired:
            self.print_error("Reddit collection timed out (20 minutes)")
            return False
        except Exception as e:
            self.print_error(f"Reddit collection error: {str(e)}")
            return False

    def run_bluesky(self):
        """
        Step 4: Run Bluesky scraper
        Uses keywords from Google Trends
        """
        self.print_header("STEP 4/4: BLUESKY DATA COLLECTION")

        if not self.keywords:
            self.print_warning("No keywords from Google Trends, using defaults")
            self.keywords = ['homelessness', 'housing crisis']

        script_path = self.scripts_dir / "bluesky" / "bluesky_social_justice_collector.py"

        if not script_path.exists():
            self.print_error(f"Bluesky script not found: {script_path}")
            return False

        self.print_info(f"Starting Bluesky collection with {len(self.keywords)} keywords")
        self.print_info("Using search method for historical data (last 7 days)")

        try:
            # Run Bluesky collector with search method
            # Create a custom keywords file for this run
            keywords_file = self.scripts_dir / "bluesky" / "master_keywords.txt"
            with open(keywords_file, 'w') as f:
                f.write('\n'.join(self.keywords))

            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    '--method', 'search',
                    '--days-back', '7',
                    '--max-posts', '1000'
                ],
                cwd=str(script_path.parent),
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )

            if result.returncode == 0:
                self.print_success("Bluesky collection completed successfully")
                # Extract summary from output
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines[-10:]:  # Last 10 lines
                    if 'posts' in line.lower() or 'saved' in line.lower():
                        self.print_info(line)

                self.results['bluesky'] = {
                    'status': 'success',
                    'timestamp': datetime.now().isoformat(),
                    'keywords_used': len(self.keywords)
                }
                return True
            else:
                self.print_error(f"Bluesky collection failed: {result.stderr}")
                self.results['bluesky'] = {
                    'status': 'failed',
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
                return False

        except subprocess.TimeoutExpired:
            self.print_error("Bluesky collection timed out (30 minutes)")
            return False
        except Exception as e:
            self.print_error(f"Bluesky collection error: {str(e)}")
            return False

    def generate_summary_report(self):
        """Generate final summary report"""
        self.print_header("COLLECTION SUMMARY REPORT")

        end_time = datetime.now()
        duration = end_time - self.start_time

        print(f"{Colors.BOLD}Start Time:{Colors.ENDC} {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Colors.BOLD}End Time:{Colors.ENDC} {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Colors.BOLD}Total Duration:{Colors.ENDC} {duration}")
        print(f"\n{Colors.BOLD}Module Results:{Colors.ENDC}")

        for module, result in self.results.items():
            status_symbol = "✓" if result['status'] == 'success' else "✗"
            status_color = Colors.OKGREEN if result['status'] == 'success' else Colors.FAIL
            print(f"  {status_color}{status_symbol} {module.upper()}: {result['status']}{Colors.ENDC}")

        # Save report to file
        report_file = self.project_root / f"collection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'keywords_used': self.keywords,
            'zipcodes_used': self.zipcodes[:10] if self.zipcodes else [],
            'results': self.results
        }

        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        self.print_success(f"Summary report saved to: {report_file}")

    def run(self):
        """Execute all scrapers in sequence"""
        self.print_header("NGO INTELLIGENCE PLATFORM - MASTER SCRAPER")
        print(f"{Colors.BOLD}Sequential Data Collection Started{Colors.ENDC}")
        print(f"Project Root: {self.project_root}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Step 1: Google Trends
        if not self.run_google_trends():
            self.print_warning("Google Trends failed, continuing with default keywords...")

        # Step 2: News API
        if not self.run_news_api():
            self.print_warning("News API failed, continuing to next module...")

        # Step 3: Reddit
        if not self.run_reddit():
            self.print_warning("Reddit failed, continuing to next module...")

        # Step 4: Bluesky
        if not self.run_bluesky():
            self.print_warning("Bluesky failed...")

        # Generate summary
        self.generate_summary_report()

        # Final status
        successful = sum(1 for r in self.results.values() if r['status'] == 'success')
        total = len(self.results)

        self.print_header(f"COMPLETE: {successful}/{total} MODULES SUCCESSFUL")

def main():
    """Main entry point"""
    orchestrator = MasterOrchestrator()

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print(f"\n{Colors.WARNING}Interrupted by user. Generating partial report...{Colors.ENDC}")
        orchestrator.generate_summary_report()
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        orchestrator.run()
    except Exception as e:
        print(f"{Colors.FAIL}Fatal error: {str(e)}{Colors.ENDC}")
        orchestrator.generate_summary_report()
        sys.exit(1)

if __name__ == "__main__":
    main()
