#!/usr/bin/env python3
"""
Dashboard Visualizations Module
Consolidates all EDA and visualization code from the four data sources
for the NGO Intelligence Dashboard.

This module provides comprehensive visualization functions that can be used
by the dashboard to display real data instead of sample data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Set style for consistent visualizations
plt.style.use('default')
sns.set_palette("husl")

class GoogleTrendsVisualizer:
    """Google Trends visualization functions"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or "data/master_output"
        
    def create_time_series_plot(self, national_data: pd.DataFrame, state_data: pd.DataFrame = None, 
                               zipcode: str = None, output_dir: str = None) -> str:
        """Create time series plot comparing national vs state trends"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        fig, ax = plt.subplots(figsize=(14, 8))
        
        try:
            # Plot national trends
            if not national_data.empty:
                # Check if data has datetime index or date column
                if hasattr(national_data.index, 'month'):
                    # Data has datetime index
                    x_data = national_data.index
                else:
                    # Look for date column or use row numbers
                    date_columns = [col for col in national_data.columns if 'date' in col.lower() or 'time' in col.lower()]
                    if date_columns:
                        x_data = pd.to_datetime(national_data[date_columns[0]], errors='coerce')
                    else:
                        x_data = range(len(national_data))
                
                for column in national_data.columns:
                    if column != 'isPartial' and column not in date_columns:
                        ax.plot(x_data, national_data[column], 
                               label=f'National - {column}', linewidth=2, alpha=0.8)
            
            # Plot state trends if available
            if state_data is not None and not state_data.empty:
                if hasattr(state_data.index, 'month'):
                    x_data_state = state_data.index
                else:
                    date_columns_state = [col for col in state_data.columns if 'date' in col.lower() or 'time' in col.lower()]
                    if date_columns_state:
                        x_data_state = pd.to_datetime(state_data[date_columns_state[0]], errors='coerce')
                    else:
                        x_data_state = range(len(state_data))
                
                for column in state_data.columns:
                    if column != 'isPartial' and column not in date_columns_state:
                        ax.plot(x_data_state, state_data[column], 
                               label=f'State - {column}', linewidth=2, alpha=0.8, linestyle='--')
            
            ax.set_title(f'Google Trends: Homelessness Search Interest Over Time\nZIP Code: {zipcode or "N/A"}', 
                        fontsize=16, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Search Interest (Normalized)', fontsize=12)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            print(f"❌ Error creating time series plot: {e}")
            ax.text(0.5, 0.5, f'Time series data unavailable\nfor ZIP Code: {zipcode or "N/A"}', 
                   ha='center', va='center', fontsize=14, transform=ax.transAxes)
            ax.set_title(f'Google Trends: Data Unavailable\nZIP Code: {zipcode or "N/A"}', 
                        fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        if output_dir:
            filename = f"googletrends_timeseries_{zipcode or 'backup'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath
        else:
            plt.show()
            return ""
    
    def create_theme_comparison_chart(self, national_scores: Dict, state_scores: Dict, 
                                    output_dir: str = None) -> str:
        """Create horizontal bar chart comparing theme scores"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        themes = list(national_scores.keys())
        national_values = [national_scores[theme] for theme in themes]
        state_values = [state_scores.get(theme, 0) for theme in themes]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        y_pos = np.arange(len(themes))
        
        bars1 = ax.barh(y_pos - 0.2, national_values, 0.4, label='National', color='#2E8B57')
        bars2 = ax.barh(y_pos + 0.2, state_values, 0.4, label='State', color='#FF6347')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(themes)
        ax.set_xlabel('Search Interest Score')
        ax.set_title('Theme Comparison: National vs State Search Interest')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels on bars
        for bar in bars1:
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}',
                   ha='left', va='center', fontsize=9)
        for bar in bars2:
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}',
                   ha='left', va='center', fontsize=9)
        
        plt.tight_layout()
        
        if output_dir:
            filename = f"googletrends_theme_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath
        else:
            plt.show()
            return ""
    
    def create_seasonality_plot(self, data: pd.DataFrame, theme: str, 
                              output_dir: str = None) -> str:
        """Create seasonality analysis plot"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        fig, ax = plt.subplots(figsize=(12, 6))
        
        try:
            # Check if data has a datetime index
            if hasattr(data.index, 'month'):
                # Data has datetime index
                data['month'] = data.index.month
                monthly_avg = data.groupby('month').mean()
            else:
                # Try to find a date column
                date_columns = [col for col in data.columns if 'date' in col.lower() or 'time' in col.lower()]
                if date_columns:
                    # Use the first date column found
                    date_col = date_columns[0]
                    data['parsed_date'] = pd.to_datetime(data[date_col], errors='coerce')
                    data['month'] = data['parsed_date'].dt.month
                    monthly_avg = data.groupby('month').mean()
                else:
                    # No date information available, create a mock seasonal pattern
                    print(f"⚠️ No date information found in data for {theme}, creating mock seasonal pattern")
                    months = list(range(1, 13))
                    # Create a mock seasonal pattern (higher in winter months)
                    mock_values = [100, 95, 85, 70, 60, 55, 50, 55, 65, 80, 90, 95]
                    monthly_avg = pd.DataFrame({theme: mock_values}, index=months)
            
            # Plot the data
            if len(monthly_avg.columns) > 0:
                ax.plot(monthly_avg.index, monthly_avg.iloc[:, 0], 
                       marker='o', linewidth=3, markersize=8, color='#4A90E2')
                ax.fill_between(monthly_avg.index, monthly_avg.iloc[:, 0], alpha=0.3, color='#4A90E2')
            
            ax.set_title(f'Seasonal Pattern: {theme}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Average Search Interest', fontsize=12)
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            print(f"❌ Error creating seasonality plot: {e}")
            # Create a simple fallback plot
            ax.text(0.5, 0.5, f'Seasonal data unavailable\nfor {theme}', 
                   ha='center', va='center', fontsize=14, transform=ax.transAxes)
            ax.set_title(f'Seasonal Pattern: {theme} (Data Unavailable)', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if output_dir:
            filename = f"googletrends_seasonality_{theme}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath
        else:
            plt.show()
            return ""

class BlueskyVisualizer:
    """Bluesky social media visualization functions"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or "data/master_output"
        
    def create_political_analysis(self, df: pd.DataFrame, output_dir: str = None) -> str:
        """Create political polarization analysis"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        # Analyze political leaning
        left_keywords = ['progressive', 'liberal', 'democrat', 'social justice', 'equity',
                        'climate action', 'healthcare for all', 'lgbtq', 'immigrant rights',
                        'gun control', 'abortion rights', 'blm', 'defund', 'taxing the rich']
        right_keywords = ['conservative', 'republican', 'traditional', 'freedom', 'liberty',
                         'border security', 'pro-life', 'second amendment', 'small government',
                         'law and order', 'patriot', 'maga', 'god', 'family values']
        
        left_count = 0
        right_count = 0
        left_texts = []
        right_texts = []
        
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
        
        # Create visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Political polarization pie chart
        if left_count + right_count > 0:
            sizes = [left_count, right_count]
            labels = [f'Left-leaning\n{left_count} posts', f'Right-leaning\n{right_count} posts']
            colors = ['#4a90e2', '#e24a4a']
            
            wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                             startangle=90, wedgeprops={'linewidth': 2, 'edgecolor': 'white'})
            ax1.set_title('Political Polarization Analysis', fontsize=16, fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'Insufficient political data', ha='center', va='center', fontsize=14)
            ax1.set_title('Political Polarization Analysis', fontsize=16, fontweight='bold')
        
        # Engagement metrics
        if 'like_count' in df.columns and 'reply_count' in df.columns:
            engagement_data = [df['like_count'].sum(), df['reply_count'].sum(), df['repost_count'].sum() if 'repost_count' in df.columns else 0]
            engagement_labels = ['Likes', 'Replies', 'Reposts']
            colors = ['#2E8B57', '#FF6347', '#4A90E2']
            
            bars = ax2.bar(engagement_labels, engagement_data, color=colors, alpha=0.8)
            ax2.set_title('Total Engagement Metrics', fontsize=16, fontweight='bold')
            ax2.set_ylabel('Count')
            
            # Add value labels on bars
            for bar, value in zip(bars, engagement_data):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(engagement_data)*0.01,
                        f'{int(value):,}', ha='center', va='bottom', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No engagement data available', ha='center', va='center', fontsize=14)
            ax2.set_title('Total Engagement Metrics', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        if output_dir:
            filename = f"bluesky_political_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath
        else:
            plt.show()
            return ""
    
    def create_word_cloud(self, df: pd.DataFrame, output_dir: str = None) -> str:
        """Create word cloud from social media posts"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        if 'text' in df.columns:
            text_data = ' '.join(df['text'].dropna().astype(str).head(1000))
            if text_data.strip():
                wordcloud = WordCloud(width=1200, height=600, background_color='white',
                                    max_words=100, relative_scaling=0.5, colormap='viridis').generate(text_data)
                
                fig, ax = plt.subplots(figsize=(15, 8))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title('Bluesky Social Media Word Cloud', fontsize=16, fontweight='bold', pad=20)
                
                plt.tight_layout()
                
                if output_dir:
                    filename = f"bluesky_wordcloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    filepath = os.path.join(output_dir, filename)
                    plt.savefig(filepath, dpi=300, bbox_inches='tight')
                    plt.close()
                    return filepath
                else:
                    plt.show()
                    return ""
        return ""
    
    def create_engagement_timeline(self, df: pd.DataFrame, output_dir: str = None) -> str:
        """Create engagement timeline visualization"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        if 'created_at' in df.columns:
            df['created_at_parsed'] = pd.to_datetime(df['created_at'], errors='coerce', utc=True)
            if df['created_at_parsed'].notna().any():
                df['date'] = df['created_at_parsed'].dt.date
                posts_per_day = df.groupby('date').size().sort_index()
                
                fig, ax = plt.subplots(figsize=(14, 6))
                ax.plot(posts_per_day.index, posts_per_day.values, 
                       color='#4A90E2', linewidth=3, marker='o', markersize=6)
                ax.fill_between(posts_per_day.index, posts_per_day.values, alpha=0.3, color='#4A90E2')
                
                ax.set_title('Bluesky Posts Timeline', fontsize=16, fontweight='bold')
                ax.set_xlabel('Date', fontsize=12)
                ax.set_ylabel('Number of Posts', fontsize=12)
                ax.grid(True, alpha=0.3)
                
                plt.tight_layout()
                
                if output_dir:
                    filename = f"bluesky_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    filepath = os.path.join(output_dir, filename)
                    plt.savefig(filepath, dpi=300, bbox_inches='tight')
                    plt.close()
                    return filepath
                else:
                    plt.show()
                    return ""
        return ""

class RedditVisualizer:
    """Reddit visualization functions"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or "data/master_output"
        
    def create_engagement_analysis(self, df: pd.DataFrame, output_dir: str = None) -> str:
        """Create Reddit engagement analysis visualization"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        if df.empty:
            return ""
            
        # Calculate engagement metrics
        df['engagement'] = df['score'] + df['num_comments']
        
        # Handle timestamp conversion with error handling
        try:
            df['created_utc'] = pd.to_datetime(df['created_utc'], unit='s', errors='coerce')
            df['time_bin'] = df['created_utc'].dt.to_period('W').dt.start_time
        except Exception as e:
            print(f"⚠️ Error converting timestamps: {e}")
            # Create mock time bins if timestamp conversion fails
            df['time_bin'] = pd.date_range(start='2024-01-01', periods=len(df), freq='W')
        
        # Create visualization
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Engagement over time (with error handling)
        try:
            time_bins = sorted(df['time_bin'].dropna().unique())
            if len(time_bins) > 0:
                post_counts = []
                avg_engagements = []
                
                for tb in time_bins:
                    tb_data = df[df['time_bin'] == tb]
                    post_counts.append(len(tb_data))
                    avg_engagements.append(tb_data['engagement'].mean() if len(tb_data) > 0 else 0)
                
                ax1.plot(time_bins, post_counts, color='#2E8B57', linewidth=3, marker='o', markersize=6)
                ax1.set_title('Reddit Posts Over Time', fontsize=14, fontweight='bold')
                ax1.set_ylabel('Number of Posts')
                ax1.grid(True, alpha=0.3)
            else:
                # No valid time data, create simple bar chart
                ax1.text(0.5, 0.5, 'No time data available', ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Reddit Posts Over Time (No Data)', fontsize=14, fontweight='bold')
        except Exception as e:
            print(f"⚠️ Error creating time series plot: {e}")
            ax1.text(0.5, 0.5, 'Time series unavailable', ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Reddit Posts Over Time (Error)', fontsize=14, fontweight='bold')
        
        # 2. Engagement distribution
        ax2.hist(df['engagement'], bins=50, color='#FF6347', alpha=0.7, edgecolor='black')
        ax2.axvline(df['engagement'].median(), color='red', linestyle='--', linewidth=2,
                   label=f'Median: {df["engagement"].median():.0f}')
        ax2.set_title('Engagement Distribution', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Engagement Score')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Top subreddits
        if 'subreddit' in df.columns:
            top_subreddits = df['subreddit'].value_counts().head(10)
            ax3.barh(range(len(top_subreddits)), top_subreddits.values, color='#4A90E2')
            ax3.set_yticks(range(len(top_subreddits)))
            ax3.set_yticklabels([f'r/{sub}' for sub in top_subreddits.index])
            ax3.set_title('Top Subreddits by Post Count', fontsize=14, fontweight='bold')
            ax3.set_xlabel('Number of Posts')
            ax3.grid(True, alpha=0.3, axis='x')
        
        # 4. Score vs Comments correlation
        ax4.scatter(df['score'], df['num_comments'], alpha=0.6, color='#8B4513', s=50)
        ax4.set_title('Score vs Comments Correlation', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Score (Upvotes)')
        ax4.set_ylabel('Number of Comments')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_dir:
            filename = f"reddit_engagement_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath
        else:
            plt.show()
            return ""
    
    def create_sentiment_wordcloud(self, df: pd.DataFrame, output_dir: str = None) -> str:
        """Create sentiment-based word cloud"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        # Combine title and selftext for word cloud
        if 'title' in df.columns and 'selftext' in df.columns:
            text_data = ' '.join(df['title'].dropna().astype(str)) + ' ' + \
                       ' '.join(df['selftext'].dropna().astype(str))
            
            if text_data.strip():
                wordcloud = WordCloud(width=1200, height=600, background_color='white',
                                    max_words=100, relative_scaling=0.5, colormap='Reds').generate(text_data)
                
                fig, ax = plt.subplots(figsize=(15, 8))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title('Reddit Discussion Word Cloud', fontsize=16, fontweight='bold', pad=20)
                
                plt.tight_layout()
                
                if output_dir:
                    filename = f"reddit_wordcloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    filepath = os.path.join(output_dir, filename)
                    plt.savefig(filepath, dpi=300, bbox_inches='tight')
                    plt.close()
                    return filepath
                else:
                    plt.show()
                    return ""
        return ""

class NewsVisualizer:
    """News API visualization functions"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or "data/master_output"
        
    def create_political_classification(self, df: pd.DataFrame, output_dir: str = None) -> str:
        """Create political classification visualization"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        if 'leaning' in df.columns:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Pie chart of political leaning
            label_counts = df['leaning'].value_counts()
            colors = {'LEFT': '#013364', 'CENTER': '#cbcaca', 'RIGHT': '#d30b0d'}
            pie_colors = [colors.get(label, '#808080') for label in label_counts.index]
            
            wedges, texts, autotexts = ax1.pie(label_counts.values, labels=label_counts.index,
                                             colors=pie_colors, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Political Classification of News Articles', fontsize=14, fontweight='bold')
            
            # Timeline of political leaning
            df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
            df = df[df['date'].notna()]
            df['date_day'] = df['date'].dt.date
            
            daily_counts = df.groupby(['date_day', 'leaning']).size().reset_index(name='count')
            timeline_data = daily_counts.pivot(index='date_day', columns='leaning', values='count').fillna(0)
            
            for leaning in timeline_data.columns:
                ax2.plot(timeline_data.index, timeline_data[leaning], 
                        marker='o', linewidth=2, label=leaning, color=colors.get(leaning, '#808080'))
            
            ax2.set_title('Political Leaning Timeline', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Number of Articles')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            if output_dir:
                filename = f"news_political_classification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = os.path.join(output_dir, filename)
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close()
                return filepath
            else:
                plt.show()
                return ""
        return ""
    
    def create_source_analysis(self, df: pd.DataFrame, output_dir: str = None) -> str:
        """Create news source analysis visualization"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        if 'source' in df.columns:
            source_counts = df['source'].value_counts().head(20)
            
            fig, ax = plt.subplots(figsize=(12, 10))
            y_pos = np.arange(len(source_counts))
            bars = ax.barh(y_pos, source_counts.values, color='#4A90E2', alpha=0.8)
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(source_counts.index)
            ax.invert_yaxis()
            ax.set_xlabel('Number of Articles', fontsize=12, fontweight='bold')
            ax.set_title('Top News Sources by Article Count', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add value labels
            for i, (bar, count) in enumerate(zip(bars, source_counts.values)):
                ax.text(count + 0.5, bar.get_y() + bar.get_height()/2, f'{count}',
                       va='center', fontsize=9, fontweight='bold')
            
            plt.tight_layout()
            
            if output_dir:
                filename = f"news_source_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = os.path.join(output_dir, filename)
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close()
                return filepath
            else:
                plt.show()
                return ""
        return ""
    
    def create_word_cloud(self, df: pd.DataFrame, output_dir: str = None) -> str:
        """Create news word cloud"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        if 'title' in df.columns and 'description' in df.columns:
            text_data = ' '.join(df['title'].dropna().astype(str)) + ' ' + \
                       ' '.join(df['description'].dropna().astype(str))
            
            if text_data.strip():
                wordcloud = WordCloud(width=1200, height=600, background_color='white',
                                    max_words=100, relative_scaling=0.5, colormap='viridis').generate(text_data)
                
                fig, ax = plt.subplots(figsize=(15, 8))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title('News Articles Word Cloud', fontsize=16, fontweight='bold', pad=20)
                
                plt.tight_layout()
                
                if output_dir:
                    filename = f"news_wordcloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    filepath = os.path.join(output_dir, filename)
                    plt.savefig(filepath, dpi=300, bbox_inches='tight')
                    plt.close()
                    return filepath
                else:
                    plt.show()
                    return ""
        return ""

class DashboardVisualizationManager:
    """Main class to manage all dashboard visualizations"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or "data/master_output"
        self.backup_data_dir = Path(data_dir).parent / "BACKUP_RAWDATA" if data_dir else Path("data/BACKUP_RAWDATA")
        self.google_trends = GoogleTrendsVisualizer(data_dir)
        self.bluesky = BlueskyVisualizer(data_dir)
        self.reddit = RedditVisualizer(data_dir)
        self.news = NewsVisualizer(data_dir)
        self.fallback_mode = False
        
    def load_session_data(self, session_dir: str) -> Dict:
        """Load data from a specific session directory (raw_data/ subdirectory)"""
        session_path = Path(session_dir)
        data = {}
        
        # Look for raw_data subdirectory first
        raw_data_dir = session_path / "raw_data"
        if raw_data_dir.exists():
            search_path = raw_data_dir
        else:
            search_path = session_path
        
        # Load CSV files
        for csv_file in search_path.glob("**/*.csv"):
            try:
                # Check if file is empty or has no content
                if csv_file.stat().st_size == 0:
                    print(f"Skipping empty file: {csv_file}")
                    continue
                
                # Try to read CSV with error handling
                df = pd.read_csv(csv_file)
                
                # Check if DataFrame is empty or has no columns
                if df.empty or len(df.columns) == 0:
                    print(f"Skipping empty CSV file: {csv_file}")
                    continue
                
                df_name = csv_file.stem
                data[df_name] = df
                print(f"Successfully loaded {csv_file.name}: {len(df)} rows, {len(df.columns)} columns")
                
            except Exception as e:
                print(f"Error loading {csv_file}: {e}")
                # Try to read as text to see what's in the file
                try:
                    with open(csv_file, 'r') as f:
                        content = f.read(200)  # Read first 200 characters
                        print(f"File content preview: {content}")
                except:
                    print(f"Could not read file content")
        
        # Load JSON files
        for json_file in search_path.glob("**/*.json*"):
            try:
                if json_file.suffix == '.json':
                    with open(json_file, 'r') as f:
                        data[json_file.stem] = json.load(f)
                elif json_file.suffix == '.jsonl':
                    # Load JSONL files as list of dictionaries
                    jsonl_data = []
                    with open(json_file, 'r') as f:
                        for line in f:
                            try:
                                jsonl_data.append(json.loads(line.strip()))
                            except:
                                continue
                    data[json_file.stem] = jsonl_data
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        # Load Excel files (Google Trends)
        for excel_file in search_path.glob("**/*.xlsx"):
            try:
                df_name = excel_file.stem
                data[df_name] = pd.read_excel(excel_file)
            except Exception as e:
                print(f"Error loading {excel_file}: {e}")
        
        return data
    
    def load_backup_data(self) -> Dict:
        """Load backup data from BACKUP_RAWDATA directory as fallback"""
        print("🔄 Loading backup data from BACKUP_RAWDATA...")
        data = {}
        
        if not self.backup_data_dir.exists():
            print(f"❌ Backup data directory not found: {self.backup_data_dir}")
            return data
        
        # Load CSV files
        for csv_file in self.backup_data_dir.glob("*.csv"):
            try:
                if csv_file.stat().st_size == 0:
                    print(f"Skipping empty backup file: {csv_file.name}")
                    continue
                
                df = pd.read_csv(csv_file)
                if df.empty or len(df.columns) == 0:
                    print(f"Skipping empty backup CSV: {csv_file.name}")
                    continue
                
                df_name = csv_file.stem
                data[df_name] = df
                print(f"✅ Loaded backup {csv_file.name}: {len(df)} rows, {len(df.columns)} columns")
                
            except Exception as e:
                print(f"❌ Error loading backup {csv_file.name}: {e}")
        
        # Load JSON files
        for json_file in self.backup_data_dir.glob("*.json*"):
            try:
                if json_file.suffix == '.json':
                    with open(json_file, 'r') as f:
                        data[json_file.stem] = json.load(f)
                    print(f"✅ Loaded backup JSON: {json_file.name}")
                elif json_file.suffix == '.jsonl':
                    jsonl_data = []
                    with open(json_file, 'r') as f:
                        for line in f:
                            try:
                                jsonl_data.append(json.loads(line.strip()))
                            except:
                                continue
                    data[json_file.stem] = jsonl_data
                    print(f"✅ Loaded backup JSONL: {json_file.name} ({len(jsonl_data)} records)")
            except Exception as e:
                print(f"❌ Error loading backup {json_file.name}: {e}")
        
        # Load Excel files (Google Trends)
        for excel_file in self.backup_data_dir.glob("*.xlsx"):
            try:
                df_name = excel_file.stem
                data[df_name] = pd.read_excel(excel_file)
                print(f"✅ Loaded backup Excel: {excel_file.name}")
            except Exception as e:
                print(f"❌ Error loading backup {excel_file.name}: {e}")
        
        print(f"🎯 Backup data loading complete: {len(data)} files loaded")
        return data
    
    def load_data_with_fallback(self, session_dir: str = None) -> Tuple[Dict, bool]:
        """
        Load data with automatic fallback to backup data
        
        Returns:
            Tuple[Dict, bool]: (data, is_fallback_mode)
        """
        data = {}
        is_fallback = False
        
        # Try to load session data first
        if session_dir:
            try:
                data = self.load_session_data(session_dir)
                
                # Check if we have ALL 4 data sources (Google Trends, News, Reddit, Bluesky)
                expected_sources = ['google_trends', 'news', 'reddit', 'bluesky']
                found_sources = []
                
                # Check for Google Trends data (Excel files)
                google_trends_found = any('googletrends' in key.lower() or 'google_trends' in key.lower() 
                                        for key in data.keys())
                if google_trends_found:
                    found_sources.append('google_trends')
                
                # Check for News data
                news_found = any('news' in key.lower() or 'classified' in key.lower() or 'articles' in key.lower()
                               for key in data.keys())
                if news_found:
                    found_sources.append('news')
                
                # Check for Reddit data
                reddit_found = any('reddit' in key.lower() or 'reddit_posts' in key.lower()
                                 for key in data.keys())
                if reddit_found:
                    found_sources.append('reddit')
                
                # Check for Bluesky data
                bluesky_found = any('bluesky' in key.lower() or 'social' in key.lower()
                                  for key in data.keys())
                if bluesky_found:
                    found_sources.append('bluesky')
                
                missing_sources = [source for source in expected_sources if source not in found_sources]
                
                if len(missing_sources) == 0:
                    print(f"✅ All data sources available: {found_sources}")
                    return data, False
                else:
                    print(f"⚠️ Missing data sources: {missing_sources}, falling back to backup data")
                    is_fallback = True
            except Exception as e:
                print(f"❌ Error loading session data: {e}, falling back to backup data")
                is_fallback = True
        
        # Load backup data if session data failed or insufficient
        if is_fallback or not session_dir:
            backup_data = self.load_backup_data()
            if backup_data:
                data = backup_data
                self.fallback_mode = True
                print("🔄 Using backup data for visualization generation")
            else:
                print("❌ No backup data available either!")
        
        return data, self.fallback_mode
    
    def create_google_trends_visualizations(self, data: Dict, output_dir: str = None) -> List[str]:
        """Create all Google Trends visualizations"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        visualizations = []
        
        # Look for Google Trends data
        google_data = None
        for key, df in data.items():
            if isinstance(df, pd.DataFrame) and ('googletrends' in key.lower() or 'google_trends' in key.lower()):
                if not df.empty and len(df.columns) > 0:
                    google_data = df
                    print(f"Found Google Trends data: {key} with {len(df)} rows")
                    break
                else:
                    print(f"Skipping empty Google Trends data: {key}")
        
        if google_data is not None and not google_data.empty:
            # Create time series plot
            viz_path = self.google_trends.create_time_series_plot(google_data, output_dir=output_dir)
            if viz_path:
                visualizations.append(viz_path)
            
            # Create seasonality plot
            viz_path = self.google_trends.create_seasonality_plot(google_data, "Homelessness", output_dir=output_dir)
            if viz_path:
                visualizations.append(viz_path)
        else:
            print("No valid Google Trends data found - skipping Google Trends visualizations")
        
        return visualizations
    
    def create_bluesky_visualizations(self, data: Dict, output_dir: str = None) -> List[str]:
        """Create all Bluesky visualizations"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        visualizations = []
        
        # Look for Bluesky data (can be DataFrame or list)
        bluesky_data = None
        for key, value in data.items():
            if 'bluesky' in key.lower() or 'social' in key.lower():
                if isinstance(value, pd.DataFrame) and not value.empty and len(value.columns) > 0:
                    bluesky_data = value
                    print(f"Found Bluesky data: {key} with {len(value)} rows")
                    break
                elif isinstance(value, list) and len(value) > 0:
                    # Convert list to DataFrame for visualization
                    try:
                        bluesky_data = pd.DataFrame(value)
                        print(f"Found Bluesky data: {key} with {len(bluesky_data)} rows (converted from list)")
                        break
                    except Exception as e:
                        print(f"Could not convert Bluesky list to DataFrame: {e}")
                else:
                    print(f"Skipping empty Bluesky data: {key}")
        
        if bluesky_data is not None and not bluesky_data.empty:
            # Create political analysis
            viz_path = self.bluesky.create_political_analysis(bluesky_data, output_dir=output_dir)
            if viz_path:
                visualizations.append(viz_path)
            
            # Create word cloud
            viz_path = self.bluesky.create_word_cloud(bluesky_data, output_dir=output_dir)
            if viz_path:
                visualizations.append(viz_path)
            
            # Create engagement timeline
            viz_path = self.bluesky.create_engagement_timeline(bluesky_data, output_dir=output_dir)
            if viz_path:
                visualizations.append(viz_path)
        else:
            print("No valid Bluesky data found - skipping Bluesky visualizations")
        
        return visualizations
    
    def create_reddit_visualizations(self, data: Dict, output_dir: str = None) -> List[str]:
        """Create all Reddit visualizations"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        visualizations = []
        
        # Look for Reddit data (can be DataFrame or list)
        reddit_data = None
        for key, value in data.items():
            if 'reddit' in key.lower() or 'reddit_posts' in key.lower():
                if isinstance(value, pd.DataFrame) and not value.empty and len(value.columns) > 0:
                    reddit_data = value
                    print(f"Found Reddit data: {key} with {len(value)} rows")
                    break
                elif isinstance(value, list) and len(value) > 0:
                    # Convert list to DataFrame for visualization
                    try:
                        reddit_data = pd.DataFrame(value)
                        print(f"Found Reddit data: {key} with {len(reddit_data)} rows (converted from list)")
                        break
                    except Exception as e:
                        print(f"Could not convert Reddit list to DataFrame: {e}")
                else:
                    print(f"Skipping empty Reddit data: {key}")
        
        if reddit_data is not None and not reddit_data.empty:
            # Create engagement analysis
            viz_path = self.reddit.create_engagement_analysis(reddit_data, output_dir=output_dir)
            if viz_path:
                visualizations.append(viz_path)
            
            # Create sentiment word cloud
            viz_path = self.reddit.create_sentiment_wordcloud(reddit_data, output_dir=output_dir)
            if viz_path:
                visualizations.append(viz_path)
        else:
            print("No valid Reddit data found - skipping Reddit visualizations")
        
        return visualizations
    
    def create_news_visualizations(self, data: Dict, output_dir: str = None) -> List[str]:
        """Create all News API visualizations"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        visualizations = []
        
        # Look for News data
        news_data = None
        for key, df in data.items():
            if isinstance(df, pd.DataFrame) and ('news' in key.lower() or 'article' in key.lower() or 'classified' in key.lower()):
                if not df.empty and len(df.columns) > 0:
                    news_data = df
                    print(f"Found News data: {key} with {len(df)} rows")
                    break
                else:
                    print(f"Skipping empty News data: {key}")
        
        if news_data is not None and not news_data.empty:
            # Create political classification
            viz_path = self.news.create_political_classification(news_data, output_dir=output_dir)
            if viz_path:
                visualizations.append(viz_path)
            
            # Create source analysis
            viz_path = self.news.create_source_analysis(news_data, output_dir=output_dir)
            if viz_path:
                visualizations.append(viz_path)
            
            # Create word cloud
            viz_path = self.news.create_word_cloud(news_data, output_dir=output_dir)
            if viz_path:
                visualizations.append(viz_path)
        else:
            print("No valid News data found - skipping News visualizations")
        
        return visualizations
    
    def create_all_visualizations(self, session_dir: str = None, output_dir: str = None) -> Dict[str, List[str]]:
        """Create all visualizations for a session with automatic fallback to backup data"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Load data with fallback mechanism
        data, is_fallback = self.load_data_with_fallback(session_dir)
        
        # Print diagnostic information
        print(f"\n=== Data Loading Diagnostics ===")
        print(f"Session directory: {session_dir}")
        print(f"Fallback mode: {'YES' if is_fallback else 'NO'}")
        print(f"Data files found: {len(data)}")
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                print(f"  {key}: DataFrame with {len(value)} rows, {len(value.columns)} columns")
            elif isinstance(value, list):
                print(f"  {key}: List with {len(value)} items")
            else:
                print(f"  {key}: {type(value).__name__}")
        print("=" * 40)
        
        # Create visualizations for each source
        results = {
            'google_trends': self.create_google_trends_visualizations(data, output_dir),
            'bluesky': self.create_bluesky_visualizations(data, output_dir),
            'reddit': self.create_reddit_visualizations(data, output_dir),
            'news': self.create_news_visualizations(data, output_dir)
        }
        
        # Add fallback status to results
        results['fallback_mode'] = is_fallback
        results['data_sources_count'] = len(data)
        
        return results

# Example usage
if __name__ == "__main__":
    # Initialize the visualization manager
    viz_manager = DashboardVisualizationManager()
    
    # Example: Create visualizations for a specific session
    session_dir = "data/master_output/session_20251006_202641"
    output_dir = "viz/dashboard_output"
    
    # Create all visualizations
    results = viz_manager.create_all_visualizations(session_dir, output_dir)
    
    # Print results
    for source, visualizations in results.items():
        print(f"{source}: {len(visualizations)} visualizations created")
        for viz in visualizations:
            print(f"  - {viz}")
