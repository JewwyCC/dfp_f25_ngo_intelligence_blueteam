import sys
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

def run_news_api(self):
    """Step 2: News API - HUNGRY SCRAPER using DIRECT IMPORT"""
    self.print_header(f"STEP 2/4: NEWS API (HOMELESSNESS ARTICLES - {self.time_budget['news_api']}s)")
    start = time.time()

    self.log_entry('news_api', 'info', f"Starting News API scraping with {self.time_budget['news_api']}s budget")

    try:
        # Add News API directory to path
        sys.path.insert(0, str(self.scripts_dir / "news_api"))

        # Import directly like dfp_socmed_blueteam does
        import combined_news_analyzer
        import NewsPoliticalClassifier
        import news_viz
        import pandas as pd
        from news_configs import KEYWORDS_DEFAULT, MAX_PAGES
        from news_credentials import NEWSAPI_KEY

        loading_dict = {
            'Wordcloud': False,
            'Outlet Article Count': False,
            'Political Pie Chart': False,
            'Political Timeline': False,
            'Media Outlet Political Classification': False
        }

        news_loading_status = False

        # Use targeted homelessness keywords
        if self.keywords:
            # Filter Google Trends keywords to only include homelessness-related ones
            filtered_trends_keywords = [kw for kw in self.keywords if any(
                homeless_term in kw.lower() for homeless_term in
                ['homeless', 'housing', 'unhoused', 'eviction', 'affordable', 'shelter', 'tent', 'encampment'])]
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
        scraper = combined_news_analyzer.CombinedNewsAnalyzer(NEWSAPI_KEY)

        print(
            f"{Colors.OKCYAN}➜ HUNGRY SCRAPER: Using {len(combined_keywords)} keywords, targeting {num_articles} articles{Colors.ENDC}")

        # Fetch articles - NEWS API ALREADY FILTERS BY KEYWORDS!
        # Don't double-filter or we lose all results
        combined_articles = scraper.combine_sources()

        print(f"{Colors.OKCYAN}➜ SUCCESS: Collected {len(combined_articles)} homelessness articles{Colors.ENDC}")

        # Initialize classifier.
        classifier = NewsPoliticalClassifier.PoliticalLeaningClassifier()

        # Classify all articles.
        classified_articles = classifier.classify_batch(combined_articles)

        # Convert classified articles to DataFrame.
        class_df = pd.DataFrame(classified_articles)

        # Update NPR labels.
        class_df.loc[class_df['source'] == 'section_/sections/news/', 'source'] = 'NPR'

        class_df.to_csv('classified.csv', index=False)

        ### Create visualizations ###

        # Initialize visualizer.
        viz = news_viz.Visualizations(class_df, 'homelessness')

        # Get summary stats
        summary_df = viz.analyze_sources(combined_articles)

        # Generate word cloud
        text = scraper.all_text(combined_articles)
        wordcloud = viz.generate_wordcloud(text)
        loading_dict['Wordcloud'] = True
        #
        # Horizontal bar chart
        viz.plot_comparison_horizontal(summary_df, top_n=25)
        loading_dict['Outlet Article Count'] = True

        # Pie Chart of Overall Political Leaning Distribution for All Articles
        viz.pie_chart(class_df)
        loading_dict['Political Pie Chart'] = True

        # Initialize political visualizer.
        poli_viz = news_viz.PoliticalAnalysisVisualizer()

        # Timeline
        poli_viz.political_timeline(class_df)
        loading_dict['Political Timeline'] = True

        # Media Outlet by Political Classification
        poli_viz.create_interactive_visualizations(class_df)
        loading_dict['Media Outlet Political Classification'] = True

        # Update news progress status.
        if all(loading_dict.values()):
            news_loading_status = True

        # Save to MASTER OUTPUT directory
        session_dir = self.master_output_dir / f"session_{self.timestamp}"
        session_dir.mkdir(exist_ok=True)

        output_file = session_dir / 'news_api_classified_articles.json'
        with open(output_file, 'w') as f:
            combined_news_analyzer.json.dump(classified_articles, f, indent=2)

        # Save CSV
        csv_file = session_dir / 'news_api_classified_articles.csv'
        class_df.to_csv(csv_file, index=False)

        print(f"{Colors.OKCYAN}➜ CSV: {csv_file}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}➜ JSON: {output_file}{Colors.ENDC}")

        elapsed = combined_news_analyzer.time.time() - start
        self.print_success(f"🦁 HUNGRY News API completed in {elapsed:.1f}s")

        self.log_entry('news_api', 'success', f"Collected {len(combined_articles)} homelessness articles", {
            'articles_count': len(combined_articles),
            'elapsed_seconds': round(elapsed, 1)
        })

        self.results['news_api'] = {'status': 'SUCCESS', 'duration': elapsed, 'articles': len(combined_articles)}

    except Exception as e:
        elapsed = combined_news_analyzer.time.time() - start
        self.print_failure(f"Failed: {str(e)}")
        self.log_entry('news_api', 'error', f"News API failed: {str(e)}")
        self.results['news_api'] = {'status': 'FAILED', 'duration': elapsed, 'error': str(e)}
        import traceback
        traceback.print_exc()