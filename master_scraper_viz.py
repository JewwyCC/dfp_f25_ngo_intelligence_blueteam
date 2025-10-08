#!/usr/bin/env python3
"""
NGO Intelligence Platform - Visualization Generation Only
Generates visualizations from raw data collected by master_scraper_data.py

Usage: python master_scraper_viz.py --session session_TIMESTAMP
Input: data/master_output/session_*/raw_data/
Output: data/master_output/session_*/artifacts/
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
import time

# Reuse the original master scraper's core functionality
from master_scraper import HomelessnessMasterOrchestrator, Colors

class VisualizationOrchestrator(HomelessnessMasterOrchestrator):
    """Focused on visualization generation only"""
    
    def __init__(self, session_id):
        # Initialize with dummy duration (not used for viz)
        super().__init__(duration_seconds=0)
        
        self.session_id = session_id
        self.session_dir = self.master_output_dir / session_id
        
        if not self.session_dir.exists():
            raise FileNotFoundError(f"Session directory not found: {self.session_dir}")
        
        self.raw_data_dir = self.session_dir / "raw_data"
        if not self.raw_data_dir.exists():
            raise FileNotFoundError(f"Raw data directory not found: {self.raw_data_dir}")
        
        self.artifacts_dir = self.session_dir / "artifacts"
        self.artifacts_dir.mkdir(exist_ok=True)
        
        self.print_info(f"📁 Session: {session_id}")
        self.print_info(f"📊 Input: raw_data/")
        self.print_info(f"🎨 Output: artifacts/")
        
        # Override timestamp to match session
        self.timestamp = session_id.replace('session_', '')
        self.start_time = datetime.now()
    
    def generate_google_trends_viz(self):
        """Copy latest Google Trends data and visualizations"""
        self.print_header("GOOGLE TRENDS VISUALIZATIONS")
        start = time.time()
        
        try:
            import shutil
            
            # Check for Google Trends data files (with google_trends_ prefix)
            trends_files = list(self.raw_data_dir.glob("google_trends_*.xlsx"))
            
            # If no data, copy latest from scripts/google_trends
            if not trends_files:
                self.print_info("📊 No Google Trends data in raw_data, copying latest...")
                trends_script_dir = self.scripts_dir / "google_trends"
                
                for pattern in ['googletrends_national_*.xlsx', 'googletrends_state_*.xlsx']:
                    files = sorted(trends_script_dir.glob(pattern), 
                                 key=lambda p: p.stat().st_mtime, reverse=True)
                    if files:
                        src = files[0]
                        dst = self.raw_data_dir / f"google_trends_{src.name}"
                        shutil.copy2(src, dst)
                        trends_files.append(dst)
            
            self.print_progress(f"📊 Processing {len(trends_files)} Google Trends data files")
            
            # Copy ALL visualizations from viz/google_trends
            viz_dir = self.project_root / "viz" / "google_trends"
            
            if viz_dir.exists():
                viz_files = list(viz_dir.glob("*.png")) + list(viz_dir.glob("*.html"))
                if viz_files:
                    # Copy with google_trends_ prefix
                    for viz_file in viz_files:
                        new_name = f"google_trends_{viz_file.name}" if not viz_file.name.startswith('google_trends_') else viz_file.name
                        dst = self.artifacts_dir / new_name
                        shutil.copy2(viz_file, dst)
                    
                    self.print_success(f"✓ Copied {len(viz_files)} Google Trends visualizations")
                    
                    duration = time.time() - start
                    self.results['google_trends_viz'] = {
                        'status': 'success',
                        'duration': duration,
                        'visualizations': len(viz_files)
                    }
                else:
                    self.print_info("⚠️  No Google Trends visualizations found in viz/ directory")
            else:
                self.print_info("⚠️  viz/google_trends directory not found, skipping")
            
        except Exception as e:
            self.print_error(f"Google Trends viz failed: {str(e)}")
            self.results['google_trends_viz'] = {'status': 'FAILED', 'error': str(e)}
    
    def generate_news_api_viz(self):
        """Generate News API visualizations from raw data"""
        self.print_header("NEWS API VISUALIZATIONS")
        start = time.time()
        
        try:
            # Check for News API data (with news_ prefix)
            classified_file = self.raw_data_dir / "news_classified.csv"
            
            if not classified_file.exists():
                self.print_info("⚠️  No News API data found, skipping")
                return
            
            self.print_progress("📰 Generating News API visualizations...")
            
            sys.path.insert(0, str(self.scripts_dir / "news_api"))
            from news_viz import Visualizations, PoliticalAnalysisVisualizer
            import pandas as pd
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            # Load classified data
            df = pd.read_csv(classified_file)
            
            # Generate visualizations (Visualizations needs keyword parameter)
            viz = Visualizations(df, keyword='homelessness')
            pol_viz = PoliticalAnalysisVisualizer()
            
            viz_count = 0
            
            # Word cloud - generate manually to avoid path issues
            try:
                from wordcloud import WordCloud, STOPWORDS
                # Use 'text' column (not 'description')
                all_text = ' '.join(df['title'].fillna('')) + ' ' + ' '.join(df['text'].fillna(''))
                
                stopwords = set(STOPWORDS)
                wordcloud = WordCloud(width=1600, height=800, background_color='white', 
                                     stopwords=stopwords, max_words=200, colormap='magma').generate(all_text)
                
                fig, ax = plt.subplots(figsize=(16, 8))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.set_title('Word Cloud for Media Coverage of Homelessness in the Last 30 Days', fontsize=16, fontweight='bold')
                ax.axis('off')
                
                output_file = self.artifacts_dir / f"news_wordcloud_{self.timestamp}.png"
                fig.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            except Exception as e:
                self.print_error(f"Word cloud failed: {str(e)}")
            
            # Outlet comparison - simple bar chart
            try:
                fig, ax = plt.subplots(figsize=(12, 8))
                source_counts = df['source'].value_counts().head(15)
                source_counts.plot(kind='barh', ax=ax, color='#D98586')
                ax.set_title('News Outlets Covering Homelessness in the Last 30 Days', fontsize=14, fontweight='bold')
                ax.set_xlabel('Number of Articles')
                ax.set_ylabel('News Outlet')
                ax.grid(axis='x', alpha=0.3)
                plt.tight_layout()
                
                output_file = self.artifacts_dir / f"news_outlet_comparison_{self.timestamp}.png"
                fig.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            except Exception as e:
                self.print_error(f"Outlet comparison failed: {str(e)}")
            
            # Political pie chart
            try:
                fig, ax = plt.subplots(figsize=(10, 8))
                leaning_counts = df['leaning'].value_counts()
                colors = {'LEFT': '#013364', 'CENTER': '#333333', 'RIGHT': '#d30b0d'}
                colors_list = [colors.get(x, 'gray') for x in leaning_counts.index]
                
                ax.pie(leaning_counts, labels=leaning_counts.index, autopct='%1.1f%%', 
                      colors=colors_list, startangle=90, textprops={'color': 'white', 'fontweight': 'bold', 'fontsize': 14})
                ax.set_title('Political Leaning of Homelessness News Coverage', fontsize=14, fontweight='bold')
                ax.legend(loc='lower left')
                plt.tight_layout()
                
                output_file = self.artifacts_dir / f"news_political_pie_{self.timestamp}.png"
                fig.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            except Exception as e:
                self.print_error(f"Political pie failed: {str(e)}")
            
            # Political timeline
            try:
                # Use 'date' column (not 'publishedAt')
                df['published'] = pd.to_datetime(df['date'])
                fig, ax = plt.subplots(figsize=(14, 6))
                
                for leaning in ['LEFT', 'CENTER', 'RIGHT']:
                    leaning_df = df[df['leaning'] == leaning]
                    if len(leaning_df) > 0:
                        leaning_df['published'].hist(bins=30, alpha=0.5, label=leaning, 
                                                     color=colors.get(leaning, 'gray'), ax=ax)
                
                ax.set_title('Timeline of News Coverage by Political Leaning', fontsize=14, fontweight='bold')
                ax.set_xlabel('Date')
                ax.set_ylabel('Number of Articles')
                ax.legend()
                ax.grid(alpha=0.3)
                plt.tight_layout()
                
                output_file = self.artifacts_dir / f"news_political_timeline_{self.timestamp}.png"
                fig.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            except Exception as e:
                self.print_error(f"Political timeline failed: {str(e)}")
            
            duration = time.time() - start
            self.results['news_api_viz'] = {
                'status': 'success',
                'duration': duration,
                'visualizations': viz_count
            }
            self.print_success(f"Generated {viz_count} News API visualizations")
            
        except Exception as e:
            self.print_error(f"News API viz failed: {str(e)}")
            self.results['news_api_viz'] = {'status': 'FAILED', 'error': str(e)}
    
    def generate_reddit_viz(self):
        """Generate individual Reddit visualizations from comprehensive dashboard components"""
        self.print_header("REDDIT VISUALIZATIONS")
        start = time.time()
        
        try:
            reddit_file = self.raw_data_dir / "reddit_posts.csv"
            
            if not reddit_file.exists():
                self.print_info("⚠️  No Reddit data found, skipping")
                return
            
            self.print_progress("🔍 Generating individual Reddit visualizations from comprehensive dashboard...")
            
            import pandas as pd
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import sys
            
            # Add reddit module to path for comprehensive viz functions
            reddit_path = str(self.scripts_dir / "reddit")
            if reddit_path not in sys.path:
                sys.path.insert(0, reddit_path)
            
            # Import visualization functions
            import importlib.util
            
            # Load analysis module
            analysis_spec = importlib.util.spec_from_file_location(
                "scripts.reddit.analysis",
                self.scripts_dir / "reddit" / "analysis.py"
            )
            analysis_module = importlib.util.module_from_spec(analysis_spec)
            sys.modules['scripts.reddit.analysis'] = analysis_module
            analysis_spec.loader.exec_module(analysis_module)
            
            # Load visualization module
            viz_spec = importlib.util.spec_from_file_location(
                "scripts.reddit.visualization",
                self.scripts_dir / "reddit" / "visualization.py"
            )
            viz_module = importlib.util.module_from_spec(viz_spec)
            sys.modules['scripts.reddit.visualization'] = viz_module
            sys.modules['scripts.reddit'] = type(sys)('scripts.reddit')
            sys.modules['scripts.reddit'].analysis = analysis_module
            viz_spec.loader.exec_module(viz_module)
            
            # Import functions
            _time_bin = viz_module._time_bin
            _create_smooth_density_plot = viz_module._create_smooth_density_plot
            _remove_outliers_iqr = viz_module._remove_outliers_iqr
            _remove_outliers_zscore = viz_module._remove_outliers_zscore
            get_top_topic_keywords_by_frequency = analysis_module.get_top_topic_keywords_by_frequency
            
            # Load data
            df = pd.read_csv(reddit_file)
            if 'created_utc' in df.columns:
                df['created_utc'] = pd.to_datetime(df['created_utc'])
            
            viz_count = 0
            
            # FIRST: Generate comprehensive dashboard (like original)
            try:
                build_dashboard = viz_module.build_dashboard
                fig_comp = plt.figure(figsize=(16, 18))
                build_dashboard(fig_comp, df)
                output_file = self.artifacts_dir / f"reddit_comprehensive_dashboard_{self.timestamp}.png"
                fig_comp.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close(fig_comp)
                viz_count += 1
                self.print_info("  Generated comprehensive dashboard")
            except Exception as e:
                self.print_info(f"  Comprehensive dashboard failed: {str(e)[:50]}")
            
            # THEN: Generate individual visualizations matching comprehensive dashboard style
            
            # Prepare data like in comprehensive dashboard
            df_sorted = df.sort_values('created_utc')
            df_sorted['time_bin'] = _time_bin(df_sorted)
            df_sorted['engagement'] = df_sorted['score'] + df_sorted['num_comments']
            
            # 1. Housing Crisis Engagement Trends (from comprehensive dashboard)
            fig, ax1 = plt.subplots(figsize=(16, 10))
            time_bins = sorted(df_sorted['time_bin'].unique())
            post_counts = []
            engagement_densities = []
            
            for tb in time_bins:
                tb_data = df_sorted[df_sorted['time_bin'] == tb]
                post_counts.append(len(tb_data))
                engagement_densities.append(tb_data['engagement'].sum())
            
            # Dual axis plot
            ax1_twin = ax1.twinx()
            _create_smooth_density_plot(ax1, time_bins, post_counts, color='#2E8B57', alpha=0.3, label='Post Count Density')
            _create_smooth_density_plot(ax1_twin, time_bins, engagement_densities, color='#FF6347', alpha=0.3, label='Total Engagement Density')
            
            # Add scatter points with color intensity
            for i, (tb, count, engagement) in enumerate(zip(time_bins, post_counts, engagement_densities)):
                intensity = min(1.0, engagement / max(engagement_densities) if max(engagement_densities) > 0 else 0)
                color = plt.cm.Reds(intensity)
                ax1.scatter(tb, count, c=[color], s=100, alpha=0.7, edgecolors='black', linewidth=1)
                ax1_twin.scatter(tb, engagement, c=[color], s=100, alpha=0.7, edgecolors='black', linewidth=1)
            
            ax1.set_title('Housing Crisis Engagement Trends - Weekly Analysis', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Time (Weekly Bins)', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Post Count (Weekly Aggregation)', color='#2E8B57', fontsize=11, fontweight='bold')
            ax1_twin.set_ylabel('Total Engagement Density (Upvotes + Comments)', color='#FF6347', fontsize=11, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9, framealpha=0.9)
            plt.tight_layout()
            fig.savefig(self.artifacts_dir / f"reddit_engagement_trends_{self.timestamp}.png", dpi=300, bbox_inches='tight')
            plt.close(fig)
            viz_count += 1
            
            # 2. Sentiment Word Cloud (from comprehensive dashboard)
            fig, ax = plt.subplots(figsize=(16, 8))
            top_keywords = get_top_topic_keywords_by_frequency(df, topic='housing_crisis', top_n=30)
            word_frequencies = {}
            word_sentiments = {}
            
            for keyword, frequency, sentiment_sum in top_keywords:
                word_frequencies[keyword] = frequency
                word_sentiments[keyword] = sentiment_sum
            
            if word_frequencies:
                from wordcloud import WordCloud
                from matplotlib.colors import LinearSegmentedColormap
                wc = WordCloud(width=800, height=400, background_color='white', max_words=50)
                wc.generate_from_frequencies(word_frequencies)
                
                # Create sentiment spectrum colormap (green to red)
                colors_list = ['#2E8B57', '#FFD700', '#FF6347']
                n_bins = 100
                cmap = LinearSegmentedColormap.from_list('sentiment', colors_list, N=n_bins)
                
                # Color words by sentiment
                def sentiment_color_func(word, **kwargs):
                    sentiment = word_sentiments.get(word, 0)
                    max_sentiment = max(abs(min(word_sentiments.values())), max(word_sentiments.values())) if word_sentiments else 1
                    normalized = float((sentiment / max_sentiment + 1) / 2 if max_sentiment > 0 else 0.5)
                    rgb = cmap(normalized)[:3]  # Get RGB tuple
                    return 'rgb({},{},{})'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
                
                wc.recolor(color_func=sentiment_color_func)
                ax.imshow(wc, interpolation='bilinear')
            ax.set_title('Housing Crisis Keywords Word Cloud (Sentiment-Colored)', fontsize=14, fontweight='bold')
            ax.axis('off')
            plt.tight_layout()
            fig.savefig(self.artifacts_dir / f"reddit_sentiment_wordcloud_{self.timestamp}.png", dpi=300, bbox_inches='tight')
            plt.close(fig)
            viz_count += 1
            
            # 3. Featured Posts (from comprehensive dashboard)
            fig, ax = plt.subplots(figsize=(16, 12))
            ax.axis('off')
            
            df_sorted['engagement'] = df_sorted['score'] + df_sorted['num_comments']
            df_clean_posts = _remove_outliers_iqr(df_sorted, 'engagement')
            if len(df_clean_posts) < len(df_sorted) * 0.3:
                df_clean_posts = _remove_outliers_zscore(df_sorted, 'engagement', threshold=2.0)
            
            top_posts = df_clean_posts.nlargest(3, 'engagement')
            ax.set_title('Featured Posts - Top 3 Highest Engagement (Personal Stories)', fontsize=14, fontweight='bold')
            
            y_positions = [0.85, 0.5, 0.15]
            for i, (_, post) in enumerate(top_posts.iterrows()):
                if i >= 3:
                    break
                y_pos = y_positions[i]
                title = post['title'][:100] + "..." if len(post['title']) > 100 else post['title']
                engagement = post['engagement']
                score = post['score']
                comments = post['num_comments']
                subreddit = post['subreddit']
                created_date = post['created_utc'].strftime('%Y-%m-%d')
                
                post_text = f"#{i+1} r/{subreddit} | {created_date}\n"
                post_text += f"Title: {title}\n"
                post_text += f"Engagement: {engagement} (↑{score} | 💬{comments})\n"
                
                if pd.notna(post.get('selftext')) and str(post.get('selftext', '')).strip():
                    content_snippet = str(post['selftext'])[:200] + "..." if len(str(post['selftext'])) > 200 else str(post['selftext'])
                    post_text += f"Content: {content_snippet}\n"
                
                color = '#FF0000' if engagement > 1000 else '#FF8000' if engagement > 500 else '#000000'
                ax.text(0.02, y_pos, post_text, transform=ax.transAxes, fontsize=10,
                       verticalalignment='top', color=color, weight='bold' if engagement > 500 else 'normal',
                       bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9, edgecolor=color, linewidth=2))
            
            plt.tight_layout()
            fig.savefig(self.artifacts_dir / f"reddit_featured_posts_{self.timestamp}.png", dpi=300, bbox_inches='tight')
            plt.close(fig)
            viz_count += 1
            
            # 4. Top subreddits (keep this as it's still useful)
            if 'subreddit' in df.columns:
                fig, ax = plt.subplots(figsize=(10, 8))
                top_subs = df['subreddit'].value_counts().head(15)
                top_subs.plot(kind='barh', ax=ax, color='coral')
                ax.set_title('Top Subreddits - Homelessness Posts', fontweight='bold', fontsize=14)
                ax.set_xlabel('Number of Posts')
                ax.set_ylabel('Subreddit')
                ax.grid(axis='x', alpha=0.3)
                plt.tight_layout()
                fig.savefig(self.artifacts_dir / f"reddit_top_subreddits_{self.timestamp}.png", dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            
            self.print_success(f"✅ Reddit: {viz_count} individual visualizations generated ({len(df)} posts)")
            
        except Exception as e:
            self.print_error(f"Reddit viz failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def generate_bluesky_viz(self):
        """Generate individual Bluesky visualizations"""
        self.print_header("BLUESKY VISUALIZATIONS")
        start = time.time()
        
        try:
            bluesky_file = self.raw_data_dir / "bluesky_homelessness_posts.csv"
            
            if not bluesky_file.exists():
                self.print_info("⚠️  No Bluesky data found, skipping")
                return
            
            self.print_progress("🦋 Generating individual Bluesky visualizations...")
            
            import pandas as pd
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from wordcloud import WordCloud
            
            # Load data
            df = pd.read_csv(bluesky_file)
            viz_count = 0
            
            # FIRST: Generate comprehensive narrative (like original)
            try:
                # Add bluesky module to path
                bluesky_path = str(self.scripts_dir / "bluesky")
                if bluesky_path not in sys.path:
                    sys.path.insert(0, bluesky_path)
                
                from gui_viz import create_narrative_visualizations
                fig_comp = create_narrative_visualizations(df)
                output_file = self.artifacts_dir / f"bluesky_comprehensive_narrative_{self.timestamp}.png"
                fig_comp.savefig(output_file, dpi=100, bbox_inches='tight', facecolor='#f8f8f8')
                viz_count += 1
                self.print_info("  Generated comprehensive narrative")
            except Exception as e:
                self.print_info(f"  Comprehensive narrative failed: {str(e)[:50]}")
            
            # THEN: Generate individual visualizations matching comprehensive narrative style
            viz_count = 0
            
            # NYT-style settings (from comprehensive narrative)
            text_color = '#121212'  # Near black
            bg_color = 'white'  # Card background
            page_bg = '#f8f8f8'  # Page background
            grid_color = '#e5e5e5'  # Light gray
            accent_color = '#4a4a4a'  # Dark grey
            border_color = '#d0d0d0'  # Card border
            left_color = '#4a90e2'  # Blue for left
            right_color = '#e24a4a'  # Red for right
            
            # 1. Period Data Pulled (Timeline) - NYT style
            if 'created_at' in df.columns:
                fig, ax = plt.subplots(figsize=(16, 6), facecolor=page_bg)
                ax.set_facecolor(bg_color)
                ax.patch.set_edgecolor(border_color)
                ax.patch.set_linewidth(1)
                
                df['created_at_parsed'] = pd.to_datetime(df['created_at'], errors='coerce', utc=True)
                if df['created_at_parsed'].notna().any():
                    df['date'] = df['created_at_parsed'].dt.date
                    posts_per_day = df.groupby('date').size().sort_index()
                    
                    ax.plot(posts_per_day.index, posts_per_day.values,
                           color=accent_color, linewidth=2.5, marker='o', markersize=5)
                    ax.fill_between(posts_per_day.index, posts_per_day.values, alpha=0.1, color=accent_color)
                    
                    ax.set_title('Period Data Pulled', fontsize=16, color=text_color,
                               weight='normal', pad=20, family='serif', loc='left')
                    ax.set_xlabel('Date', fontsize=11, color='#666666', family='sans-serif')
                    ax.set_ylabel('Posts', fontsize=11, color='#666666', family='sans-serif')
                    ax.grid(True, alpha=0.3, color=grid_color, linestyle='-', linewidth=0.5)
                    ax.tick_params(colors='#666666', labelsize=9)
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['bottom'].set_color(grid_color)
                    ax.spines['left'].set_color(grid_color)
                
                plt.tight_layout()
                fig.savefig(self.artifacts_dir / f"bluesky_timeline_{self.timestamp}.png", dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            
            # 2. Content Word Cloud - NYT style
            if 'text' in df.columns:
                fig, ax = plt.subplots(figsize=(16, 8), facecolor=page_bg)
                ax.set_facecolor(bg_color)
                ax.axis('off')
                for spine in ax.spines.values():
                    spine.set_edgecolor(border_color)
                    spine.set_linewidth(1)
                    spine.set_visible(True)
                
                text_data = ' '.join(df['text'].dropna().astype(str).head(1000))
                if text_data.strip():
                    try:
                        wc = WordCloud(width=1400, height=400, background_color='white',
                                     color_func=lambda *args, **kwargs: accent_color,
                                     max_words=80, relative_scaling=0.4).generate(text_data)
                        ax.imshow(wc, interpolation='bilinear')
                        ax.set_title('Content Word Cloud (All Posts)', fontsize=16, color=text_color,
                                   weight='normal', pad=15, family='serif', loc='left')
                    except:
                        ax.text(0.5, 0.5, 'No word cloud data', ha='center', va='center',
                               color='#999999', family='sans-serif')
                
                plt.tight_layout()
                fig.savefig(self.artifacts_dir / f"bluesky_wordcloud_all_{self.timestamp}.png", dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            
            # 3. Political Analysis - Calculate counts first
            left_keywords = ['progressive', 'liberal', 'democrat', 'social justice', 'equity',
                           'climate action', 'healthcare for all', 'lgbtq', 'immigrant rights',
                           'gun control', 'abortion rights', 'blm', 'defund', 'taxing the rich']
            right_keywords = ['conservative', 'republican', 'traditional', 'freedom', 'liberty',
                            'border security', 'pro-life', 'second amendment', 'small government',
                            'law and order', 'patriot', 'maga', 'god', 'family values']
            
            left_texts = []
            right_texts = []
            left_count = 0
            right_count = 0
            
            if 'text' in df.columns:
                for text in df['text'].dropna().astype(str):
                    text_lower = text.lower()
                    left_matches = sum(1 for kw in left_keywords if kw in text_lower)
                    right_matches = sum(1 for kw in right_keywords if kw in text_lower)
                    
                    if left_matches > right_matches and left_matches > 0:
                        left_count += 1
                        left_texts.append(text)
                    elif right_matches > left_matches and right_matches > 0:
                        right_count += 1
                        right_texts.append(text)
            
            # 3a. Polarization Gauge - NYT style
            total_polar = left_count + right_count
            if total_polar > 0:
                fig, ax = plt.subplots(figsize=(14, 8), facecolor=page_bg)
                ax.set_facecolor(bg_color)
                ax.patch.set_edgecolor(border_color)
                ax.patch.set_linewidth(1)
                
                left_pct = (left_count / total_polar) * 100
                right_pct = (right_count / total_polar) * 100
                
                sizes = [left_pct, right_pct]
                colors = [left_color, right_color]
                labels = [f'Left-leaning\n{left_count} posts\n({left_pct:.1f}%)',
                         f'Right-leaning\n{right_count} posts\n({right_pct:.1f}%)']
                
                wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                                  autopct='', startangle=180,
                                                  wedgeprops={'width': 0.4, 'linewidth': 1, 'edgecolor': 'white'})
                ax.set_ylim(-1, 0.2)
                
                for text in texts:
                    text.set_fontsize(10)
                    text.set_family('sans-serif')
                
                ax.set_title('Political Polarization Analysis',
                           fontsize=18, color=text_color, weight='normal', pad=20,
                           family='serif', loc='center')
                
                ax.text(0, -0.5, f'{total_polar}\npolarized posts',
                       ha='center', va='center', fontsize=12, color='#666666',
                       family='sans-serif', weight='bold')
                
                plt.tight_layout()
                fig.savefig(self.artifacts_dir / f"bluesky_polarization_gauge_{self.timestamp}.png", dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            
            # 3b. Left-Leaning Word Cloud - NYT style
            if len(left_texts) > 0:
                fig, ax = plt.subplots(figsize=(14, 8), facecolor=page_bg)
                ax.set_facecolor(bg_color)
                ax.axis('off')
                for spine in ax.spines.values():
                    spine.set_edgecolor(border_color)
                    spine.set_linewidth(1)
                    spine.set_visible(True)
                
                left_text_data = ' '.join(left_texts)
                if left_text_data.strip():
                    try:
                        wc_left = WordCloud(width=700, height=450, background_color='white',
                                          color_func=lambda *args, **kwargs: left_color,
                                          max_words=50, relative_scaling=0.4).generate(left_text_data)
                        ax.imshow(wc_left, interpolation='bilinear')
                        ax.set_title(f'Left-Leaning Content ({len(left_texts)} posts)',
                                   fontsize=14, color=text_color, weight='normal',
                                   pad=15, family='serif', loc='left')
                    except:
                        ax.text(0.5, 0.5, 'No left-leaning data', ha='center', va='center',
                               color='#999999', family='sans-serif')
                
                plt.tight_layout()
                fig.savefig(self.artifacts_dir / f"bluesky_wordcloud_left_{self.timestamp}.png", dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            
            # 3c. Right-Leaning Word Cloud - NYT style
            if len(right_texts) > 0:
                fig, ax = plt.subplots(figsize=(14, 8), facecolor=page_bg)
                ax.set_facecolor(bg_color)
                ax.axis('off')
                for spine in ax.spines.values():
                    spine.set_edgecolor(border_color)
                    spine.set_linewidth(1)
                    spine.set_visible(True)
                
                right_text_data = ' '.join(right_texts)
                if right_text_data.strip():
                    try:
                        wc_right = WordCloud(width=700, height=450, background_color='white',
                                           color_func=lambda *args, **kwargs: right_color,
                                           max_words=50, relative_scaling=0.4).generate(right_text_data)
                        ax.imshow(wc_right, interpolation='bilinear')
                        ax.set_title(f'Right-Leaning Content ({len(right_texts)} posts)',
                                   fontsize=14, color=text_color, weight='normal',
                                   pad=15, family='serif', loc='left')
                    except:
                        ax.text(0.5, 0.5, 'No right-leaning data', ha='center', va='center',
                               color='#999999', family='sans-serif')
                
                plt.tight_layout()
                fig.savefig(self.artifacts_dir / f"bluesky_wordcloud_right_{self.timestamp}.png", dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            
            # 4. Engagement: Total Counts - NYT style
            if 'like_count' in df.columns:
                fig, ax = plt.subplots(figsize=(12, 6), facecolor=page_bg)
                ax.set_facecolor(bg_color)
                ax.patch.set_edgecolor(border_color)
                ax.patch.set_linewidth(1)
                
                engagement_types = []
                engagement_values = []
                
                if 'like_count' in df.columns:
                    engagement_types.append('Likes')
                    engagement_values.append(df['like_count'].sum())
                if 'reply_count' in df.columns:
                    engagement_types.append('Replies')
                    engagement_values.append(df['reply_count'].sum())
                if 'repost_count' in df.columns:
                    engagement_types.append('Reposts')
                    engagement_values.append(df['repost_count'].sum())
                
                bars = ax.bar(engagement_types, engagement_values, color=accent_color, width=0.6)
                ax.set_title('Engagement: Total Counts', fontsize=14, color=text_color,
                           weight='normal', pad=20, family='serif', loc='left')
                ax.set_ylabel('Count', fontsize=11, color='#666666', family='sans-serif')
                ax.tick_params(colors='#666666', labelsize=9)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_color(grid_color)
                ax.spines['left'].set_color(grid_color)
                ax.grid(True, alpha=0.3, axis='y', color=grid_color, linestyle='-', linewidth=0.5)
                
                plt.tight_layout()
                fig.savefig(self.artifacts_dir / f"bluesky_engagement_totals_{self.timestamp}.png", dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            
            # 5. Engagement: Hourly Posting Pattern - NYT style
            if 'created_at' in df.columns:
                fig, ax = plt.subplots(figsize=(14, 6), facecolor=page_bg)
                ax.set_facecolor(bg_color)
                ax.patch.set_edgecolor(border_color)
                ax.patch.set_linewidth(1)
                
                df['hour'] = pd.to_datetime(df['created_at'], errors='coerce').dt.hour
                hourly_counts = df['hour'].value_counts().sort_index()
                
                ax.plot(hourly_counts.index, hourly_counts.values,
                       marker='o', linewidth=2.5, markersize=6, color=accent_color)
                ax.fill_between(hourly_counts.index, hourly_counts.values, alpha=0.1, color=accent_color)
                
                ax.set_title('Engagement: Hourly Posting Pattern', fontsize=14, color=text_color,
                           weight='normal', pad=20, family='serif', loc='left')
                ax.set_xlabel('Hour of Day (UTC)', fontsize=11, color='#666666', family='sans-serif')
                ax.set_ylabel('Number of Posts', fontsize=11, color='#666666', family='sans-serif')
                ax.set_xticks(range(0, 24))
                ax.tick_params(colors='#666666', labelsize=9)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_color(grid_color)
                ax.spines['left'].set_color(grid_color)
                ax.grid(True, alpha=0.3, color=grid_color, linestyle='-', linewidth=0.5)
                
                plt.tight_layout()
                fig.savefig(self.artifacts_dir / f"bluesky_hourly_pattern_{self.timestamp}.png", dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            
            # 6. Author Analysis: Top 15 Contributors - NYT style
            if 'author_handle' in df.columns:
                fig, ax = plt.subplots(figsize=(14, 10), facecolor=page_bg)
                ax.set_facecolor(bg_color)
                ax.patch.set_edgecolor(border_color)
                ax.patch.set_linewidth(1)
                
                top_authors = df['author_handle'].value_counts().head(15)
                if len(top_authors) > 0:
                    bars = ax.barh(range(len(top_authors)), top_authors.values,
                                  color=accent_color, height=0.7)
                    ax.set_yticks(range(len(top_authors)))
                    ax.set_yticklabels(top_authors.index, fontsize=10, family='sans-serif')
                    ax.invert_yaxis()
                    ax.set_title('Author Analysis: Top 15 Contributors', fontsize=16,
                               color=text_color, weight='normal', pad=20, family='serif', loc='left')
                    ax.set_xlabel('Number of Posts', fontsize=11, color='#666666', family='sans-serif')
                    ax.tick_params(colors='#666666', labelsize=9)
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['bottom'].set_color(grid_color)
                    ax.spines['left'].set_color(grid_color)
                    ax.grid(True, alpha=0.3, axis='x', color=grid_color, linestyle='-', linewidth=0.5)
                
                plt.tight_layout()
                fig.savefig(self.artifacts_dir / f"bluesky_top_authors_{self.timestamp}.png", dpi=300, bbox_inches='tight')
                plt.close(fig)
                viz_count += 1
            
            self.print_success(f"✅ Bluesky: {viz_count} individual visualizations generated ({len(df)} posts)")
            
        except Exception as e:
            self.print_error(f"Bluesky viz failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Execute visualization generation for all modules"""
        self.print_header(f"VISUALIZATION GENERATOR ({self.session_id})")
        print(f"{Colors.BOLD}Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
        print(f"{Colors.BOLD}Input: {self.raw_data_dir}{Colors.ENDC}")
        print(f"{Colors.BOLD}Output: {self.artifacts_dir}{Colors.ENDC}\n")
        
        # Generate all visualizations
        self.generate_google_trends_viz()
        self.generate_news_api_viz()
        self.generate_reddit_viz()
        self.generate_bluesky_viz()
        
        # Save master log
        self.save_master_log()
        
        # Summary
        self.print_header("VISUALIZATION SUMMARY")
        total_duration = time.time() - self.start_time.timestamp()
        print(f"{Colors.BOLD}Total Duration: {total_duration:.1f} seconds{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}📁 Artifacts Directory:{Colors.ENDC}")
        print(f"  {self.artifacts_dir}")
        
        print(f"\n{Colors.BOLD}🎨 Generated Artifacts:{Colors.ENDC}")
        if self.artifacts_dir.exists():
            artifact_files = sorted(self.artifacts_dir.glob("*"))
            for f in artifact_files:
                size_kb = f.stat().st_size / 1024
                file_type = "📊" if f.suffix == ".png" else "🌐" if f.suffix == ".html" else "📄"
                print(f"  {file_type} {f.name:50s} ({size_kb:>8.1f} KB)")
            print(f"\n{Colors.BOLD}Total: {len(artifact_files)} artifacts{Colors.ENDC}")
        
        print(f"\n{Colors.OKGREEN}✅ Visualization generation complete!{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description='NGO Visualization Generator - Artifacts from Raw Data')
    parser.add_argument('--session', type=str, required=True,
                       help='Session ID (e.g., session_20251006_123042) to generate visualizations from')
    
    args = parser.parse_args()
    
    try:
        orchestrator = VisualizationOrchestrator(session_id=args.session)
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
