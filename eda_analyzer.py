#!/usr/bin/env python3
"""
FAANG-Level EDA Analysis for Bluesky Social Justice Data
DFP F25 Social Media Blue Team

Comprehensive data analysis with professional visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from datetime import datetime, timedelta
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Set professional styling
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

class BlueskyEDAAnalyzer:
    """Professional EDA analyzer for Bluesky social justice data"""
    
    def __init__(self, data_path="data/alltime_socmed/merged_alltime_20250928_221708.csv"):
        self.data_path = data_path
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load and preprocess data"""
        print("🔄 Loading data...")
        try:
            self.df = pd.read_csv(self.data_path)
            print(f"✅ Loaded {len(self.df):,} posts")
            
            # Convert datetime columns
            if 'created_at' in self.df.columns:
                try:
                    self.df['created_at'] = pd.to_datetime(self.df['created_at'], utc=True)
                except:
                    # Fallback for mixed datetime formats
                    self.df['created_at'] = pd.to_datetime(self.df['created_at'], errors='coerce')
                
                # Only proceed if conversion was successful
                if self.df['created_at'].dtype.name.startswith('datetime'):
                    self.df['date'] = self.df['created_at'].dt.date
                    self.df['hour'] = self.df['created_at'].dt.hour
                    self.df['day_of_week'] = self.df['created_at'].dt.day_name()
                    self.df['month'] = self.df['created_at'].dt.month_name()
            
            # Text preprocessing - use existing columns if available
            if 'text' in self.df.columns:
                if 'text_length' not in self.df.columns:
                    self.df['text_length'] = self.df['text'].str.len()
                if 'word_count' not in self.df.columns:
                    self.df['word_count'] = self.df['text'].str.split().str.len()
                # Use existing char_count if available
                if 'char_count' in self.df.columns:
                    self.df['text_length'] = self.df['char_count']
            
            print("✅ Data preprocessing complete")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.df = pd.DataFrame()
    
    def generate_overview_stats(self):
        """Generate comprehensive overview statistics"""
        if self.df.empty:
            return {}
        
        # Handle datetime range safely
        date_range = {'start': None, 'end': None}
        if 'created_at' in self.df.columns and self.df['created_at'].dtype.name.startswith('datetime'):
            valid_dates = self.df['created_at'].dropna()
            if not valid_dates.empty:
                date_range['start'] = str(valid_dates.min())
                date_range['end'] = str(valid_dates.max())
        
        stats = {
            'total_posts': len(self.df),
            'unique_authors': self.df['author_handle'].nunique() if 'author_handle' in self.df.columns else 0,
            'date_range': date_range,
            'avg_text_length': float(self.df['text_length'].mean()) if 'text_length' in self.df.columns else 0,
            'avg_word_count': float(self.df['word_count'].mean()) if 'word_count' in self.df.columns else 0,
            'posts_with_location': int(self.df['has_location_data'].sum()) if 'has_location_data' in self.df.columns else 0,
            'posts_with_keywords': int(self.df['has_keyword_matches'].sum()) if 'has_keyword_matches' in self.df.columns else 0,
            'recent_posts': int(self.df['is_recent'].sum()) if 'is_recent' in self.df.columns else 0
        }
        
        return stats
    
    def create_temporal_analysis(self):
        """Create temporal analysis visualizations"""
        if self.df.empty or 'created_at' not in self.df.columns:
            return ""
        
        # Check if we have valid datetime data
        if not self.df['created_at'].dtype.name.startswith('datetime'):
            return ""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('📅 Temporal Analysis of Social Justice Posts', fontsize=16, fontweight='bold')
        
        # 1. Posts over time
        if 'date' in self.df.columns:
            daily_posts = self.df.groupby('date').size()
            axes[0, 0].plot(daily_posts.index, daily_posts.values, linewidth=2, color='#2E86AB')
        else:
            # Fallback: use created_at directly
            daily_posts = self.df.groupby(self.df['created_at'].dt.date).size()
            axes[0, 0].plot(daily_posts.index, daily_posts.values, linewidth=2, color='#2E86AB')
        axes[0, 0].set_title('Daily Post Volume', fontweight='bold')
        axes[0, 0].set_xlabel('Date')
        axes[0, 0].set_ylabel('Number of Posts')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Hourly distribution
        if 'hour' in self.df.columns:
            hourly_posts = self.df['hour'].value_counts().sort_index()
            axes[0, 1].bar(hourly_posts.index, hourly_posts.values, color='#A23B72', alpha=0.7)
        else:
            hourly_posts = self.df['created_at'].dt.hour.value_counts().sort_index()
            axes[0, 1].bar(hourly_posts.index, hourly_posts.values, color='#A23B72', alpha=0.7)
        axes[0, 1].set_title('Posts by Hour of Day', fontweight='bold')
        axes[0, 1].set_xlabel('Hour')
        axes[0, 1].set_ylabel('Number of Posts')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Day of week distribution
        if 'day_of_week' in self.df.columns:
            dow_posts = self.df['day_of_week'].value_counts()
        else:
            dow_posts = self.df['created_at'].dt.day_name().value_counts()
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_posts = dow_posts.reindex(dow_order)
        axes[1, 0].bar(dow_posts.index, dow_posts.values, color='#F18F01', alpha=0.7)
        axes[1, 0].set_title('Posts by Day of Week', fontweight='bold')
        axes[1, 0].set_xlabel('Day of Week')
        axes[1, 0].set_ylabel('Number of Posts')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Monthly distribution
        if 'month' in self.df.columns:
            monthly_posts = self.df['month'].value_counts()
        else:
            monthly_posts = self.df['created_at'].dt.month_name().value_counts()
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_posts = monthly_posts.reindex([m for m in month_order if m in monthly_posts.index])
        axes[1, 1].bar(monthly_posts.index, monthly_posts.values, color='#C73E1D', alpha=0.7)
        axes[1, 1].set_title('Posts by Month', fontweight='bold')
        axes[1, 1].set_xlabel('Month')
        axes[1, 1].set_ylabel('Number of Posts')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._fig_to_html(fig)
    
    def create_geographic_analysis(self):
        """Create geographic analysis visualizations"""
        if self.df.empty or 'detected_location' not in self.df.columns:
            return ""
        
        # Filter posts with location data
        location_df = self.df[self.df['detected_location'].notna()]
        if location_df.empty:
            return ""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('🌍 Geographic Analysis of Social Justice Posts', fontsize=16, fontweight='bold')
        
        # 1. Top locations
        top_locations = location_df['detected_location'].value_counts().head(15)
        axes[0, 0].barh(range(len(top_locations)), top_locations.values, color='#2E86AB', alpha=0.7)
        axes[0, 0].set_yticks(range(len(top_locations)))
        axes[0, 0].set_yticklabels(top_locations.index)
        axes[0, 0].set_title('Top 15 Locations', fontweight='bold')
        axes[0, 0].set_xlabel('Number of Posts')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Location distribution pie chart
        location_counts = location_df['detected_location'].value_counts().head(10)
        other_count = location_df['detected_location'].value_counts().iloc[10:].sum()
        if other_count > 0:
            location_counts['Other'] = other_count
        
        axes[0, 1].pie(location_counts.values, labels=location_counts.index, autopct='%1.1f%%', startangle=90)
        axes[0, 1].set_title('Location Distribution (Top 10)', fontweight='bold')
        
        # 3. Location over time
        location_time = location_df.groupby(['date', 'detected_location']).size().unstack(fill_value=0)
        top_5_locations = location_df['detected_location'].value_counts().head(5).index
        for loc in top_5_locations:
            if loc in location_time.columns:
                axes[1, 0].plot(location_time.index, location_time[loc], label=loc, linewidth=2)
        axes[1, 0].set_title('Top 5 Locations Over Time', fontweight='bold')
        axes[1, 0].set_xlabel('Date')
        axes[1, 0].set_ylabel('Number of Posts')
        axes[1, 0].legend()
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Location word cloud
        all_locations = ' '.join(location_df['detected_location'].dropna().astype(str))
        if all_locations:
            wordcloud = WordCloud(width=400, height=300, background_color='white', 
                                colormap='viridis', max_words=50).generate(all_locations)
            axes[1, 1].imshow(wordcloud, interpolation='bilinear')
            axes[1, 1].set_title('Location Word Cloud', fontweight='bold')
            axes[1, 1].axis('off')
        
        plt.tight_layout()
        return self._fig_to_html(fig)
    
    def create_content_analysis(self):
        """Create content analysis visualizations"""
        if self.df.empty:
            return ""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('📝 Content Analysis of Social Justice Posts', fontsize=16, fontweight='bold')
        
        # 1. Text length distribution
        if 'text_length' in self.df.columns:
            axes[0, 0].hist(self.df['text_length'], bins=50, color='#2E86AB', alpha=0.7, edgecolor='black')
            axes[0, 0].set_title('Distribution of Text Length', fontweight='bold')
            axes[0, 0].set_xlabel('Character Count')
            axes[0, 0].set_ylabel('Frequency')
            axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Word count distribution
        if 'word_count' in self.df.columns:
            axes[0, 1].hist(self.df['word_count'], bins=50, color='#A23B72', alpha=0.7, edgecolor='black')
            axes[0, 1].set_title('Distribution of Word Count', fontweight='bold')
            axes[0, 1].set_xlabel('Word Count')
            axes[0, 1].set_ylabel('Frequency')
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Keyword analysis
        if 'keyword_matches' in self.df.columns:
            # Flatten keyword matches
            all_keywords = []
            for keywords in self.df['keyword_matches'].dropna():
                if isinstance(keywords, str):
                    try:
                        import ast
                        keywords_list = ast.literal_eval(keywords)
                        all_keywords.extend(keywords_list)
                    except:
                        all_keywords.extend(keywords.split(','))
                elif isinstance(keywords, list):
                    all_keywords.extend(keywords)
            
            if all_keywords:
                keyword_counts = Counter(all_keywords)
                top_keywords = dict(keyword_counts.most_common(15))
                
                axes[1, 0].barh(range(len(top_keywords)), list(top_keywords.values()), 
                               color='#F18F01', alpha=0.7)
                axes[1, 0].set_yticks(range(len(top_keywords)))
                axes[1, 0].set_yticklabels(list(top_keywords.keys()))
                axes[1, 0].set_title('Top 15 Keywords', fontweight='bold')
                axes[1, 0].set_xlabel('Frequency')
                axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Text word cloud
        if 'text' in self.df.columns:
            all_text = ' '.join(self.df['text'].dropna().astype(str))
            if all_text:
                wordcloud = WordCloud(width=400, height=300, background_color='white', 
                                    colormap='plasma', max_words=100, 
                                    stopwords={'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}).generate(all_text)
                axes[1, 1].imshow(wordcloud, interpolation='bilinear')
                axes[1, 1].set_title('Content Word Cloud', fontweight='bold')
                axes[1, 1].axis('off')
        
        plt.tight_layout()
        return self._fig_to_html(fig)
    
    def create_author_analysis(self):
        """Create author analysis visualizations"""
        if self.df.empty or 'author_handle' not in self.df.columns:
            return ""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('👥 Author Analysis of Social Justice Posts', fontsize=16, fontweight='bold')
        
        # 1. Top authors by post count
        top_authors = self.df['author_handle'].value_counts().head(15)
        axes[0, 0].barh(range(len(top_authors)), top_authors.values, color='#2E86AB', alpha=0.7)
        axes[0, 0].set_yticks(range(len(top_authors)))
        axes[0, 0].set_yticklabels([handle[:20] + '...' if len(handle) > 20 else handle 
                                   for handle in top_authors.index])
        axes[0, 0].set_title('Top 15 Authors by Post Count', fontweight='bold')
        axes[0, 0].set_xlabel('Number of Posts')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Author activity distribution
        author_counts = self.df['author_handle'].value_counts()
        activity_bins = [1, 2, 5, 10, 20, 50, 100, float('inf')]
        activity_labels = ['1', '2-4', '5-9', '10-19', '20-49', '50-99', '100+']
        activity_dist = pd.cut(author_counts, bins=activity_bins, labels=activity_labels, right=False).value_counts()
        
        axes[0, 1].bar(activity_dist.index, activity_dist.values, color='#A23B72', alpha=0.7)
        axes[0, 1].set_title('Author Activity Distribution', fontweight='bold')
        axes[0, 1].set_xlabel('Posts per Author')
        axes[0, 1].set_ylabel('Number of Authors')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Author engagement over time
        if 'date' in self.df.columns:
            author_time = self.df.groupby(['date', 'author_handle']).size().unstack(fill_value=0)
            daily_authors = self.df.groupby('date')['author_handle'].nunique()
        else:
            author_time = self.df.groupby([self.df['created_at'].dt.date, 'author_handle']).size().unstack(fill_value=0)
            daily_authors = self.df.groupby(self.df['created_at'].dt.date)['author_handle'].nunique()
        
        top_5_authors = self.df['author_handle'].value_counts().head(5).index
        for author in top_5_authors:
            if author in author_time.columns:
                axes[1, 0].plot(author_time.index, author_time[author], label=author[:15], linewidth=2)
        axes[1, 0].set_title('Top 5 Authors Over Time', fontweight='bold')
        axes[1, 0].set_xlabel('Date')
        axes[1, 0].set_ylabel('Number of Posts')
        axes[1, 0].legend()
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Author diversity over time
        axes[1, 1].plot(daily_authors.index, daily_authors.values, linewidth=2, color='#F18F01')
        axes[1, 1].set_title('Daily Unique Authors', fontweight='bold')
        axes[1, 1].set_xlabel('Date')
        axes[1, 1].set_ylabel('Number of Unique Authors')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._fig_to_html(fig)
    
    def create_sentiment_analysis(self):
        """Create sentiment analysis visualizations"""
        if self.df.empty:
            return ""
        
        # Simple sentiment analysis based on keywords
        positive_keywords = ['support', 'help', 'community', 'together', 'hope', 'positive', 'good', 'great', 'amazing', 'wonderful']
        negative_keywords = ['problem', 'issue', 'crisis', 'struggle', 'difficult', 'challenge', 'bad', 'terrible', 'awful', 'horrible']
        
        def simple_sentiment(text):
            if pd.isna(text):
                return 'neutral'
            text_lower = str(text).lower()
            pos_count = sum(1 for word in positive_keywords if word in text_lower)
            neg_count = sum(1 for word in negative_keywords if word in text_lower)
            
            if pos_count > neg_count:
                return 'positive'
            elif neg_count > pos_count:
                return 'negative'
            else:
                return 'neutral'
        
        if 'text' in self.df.columns:
            self.df['sentiment'] = self.df['text'].apply(simple_sentiment)
            
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('😊 Sentiment Analysis of Social Justice Posts', fontsize=16, fontweight='bold')
            
            # 1. Sentiment distribution
            sentiment_counts = self.df['sentiment'].value_counts()
            colors = ['#2E86AB', '#A23B72', '#F18F01']
            axes[0, 0].pie(sentiment_counts.values, labels=sentiment_counts.index, 
                          autopct='%1.1f%%', colors=colors, startangle=90)
            axes[0, 0].set_title('Overall Sentiment Distribution', fontweight='bold')
            
            # 2. Sentiment over time
            if 'date' in self.df.columns:
                sentiment_time = self.df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
            else:
                sentiment_time = self.df.groupby([self.df['created_at'].dt.date, 'sentiment']).size().unstack(fill_value=0)
            
            for sentiment in sentiment_counts.index:
                if sentiment in sentiment_time.columns:
                    axes[0, 1].plot(sentiment_time.index, sentiment_time[sentiment], 
                                   label=sentiment, linewidth=2)
            axes[0, 1].set_title('Sentiment Over Time', fontweight='bold')
            axes[0, 1].set_xlabel('Date')
            axes[0, 1].set_ylabel('Number of Posts')
            axes[0, 1].legend()
            axes[0, 1].tick_params(axis='x', rotation=45)
            axes[0, 1].grid(True, alpha=0.3)
            
            # 3. Sentiment by location
            if 'detected_location' in self.df.columns:
                location_sentiment = self.df.groupby(['detected_location', 'sentiment']).size().unstack(fill_value=0)
                top_locations = self.df['detected_location'].value_counts().head(10).index
                location_sentiment = location_sentiment.loc[top_locations]
                
                location_sentiment.plot(kind='bar', ax=axes[1, 0], color=colors)
                axes[1, 0].set_title('Sentiment by Top 10 Locations', fontweight='bold')
                axes[1, 0].set_xlabel('Location')
                axes[1, 0].set_ylabel('Number of Posts')
                axes[1, 0].tick_params(axis='x', rotation=45)
                axes[1, 0].legend()
                axes[1, 0].grid(True, alpha=0.3)
            
            # 4. Sentiment word cloud
            positive_text = ' '.join(self.df[self.df['sentiment'] == 'positive']['text'].dropna().astype(str))
            if positive_text:
                wordcloud = WordCloud(width=400, height=300, background_color='white', 
                                    colormap='Greens', max_words=50).generate(positive_text)
                axes[1, 1].imshow(wordcloud, interpolation='bilinear')
                axes[1, 1].set_title('Positive Sentiment Word Cloud', fontweight='bold')
                axes[1, 1].axis('off')
            
            plt.tight_layout()
            return self._fig_to_html(fig)
        
        return ""
    
    def create_engagement_analysis(self):
        """Create engagement analysis visualizations"""
        if self.df.empty:
            return ""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('📊 Engagement Analysis of Social Justice Posts', fontsize=16, fontweight='bold')
        
        # 1. Post length vs engagement (using text length as proxy)
        if 'text_length' in self.df.columns:
            axes[0, 0].scatter(self.df['text_length'], range(len(self.df)), 
                              alpha=0.6, color='#2E86AB', s=20)
            axes[0, 0].set_title('Post Length Distribution', fontweight='bold')
            axes[0, 0].set_xlabel('Text Length (characters)')
            axes[0, 0].set_ylabel('Post Index')
            axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Keyword density analysis
        if 'keyword_matches' in self.df.columns and 'text_length' in self.df.columns:
            # Calculate keyword density
            keyword_density = []
            for idx, row in self.df.iterrows():
                if pd.notna(row['keyword_matches']) and pd.notna(row['text_length']):
                    try:
                        import ast
                        keywords = ast.literal_eval(str(row['keyword_matches']))
                        density = len(keywords) / row['text_length'] * 100
                        keyword_density.append(density)
                    except:
                        keyword_density.append(0)
                else:
                    keyword_density.append(0)
            
            self.df['keyword_density'] = keyword_density
            axes[0, 1].hist(self.df['keyword_density'], bins=30, color='#A23B72', alpha=0.7, edgecolor='black')
            axes[0, 1].set_title('Keyword Density Distribution', fontweight='bold')
            axes[0, 1].set_xlabel('Keywords per 100 characters')
            axes[0, 1].set_ylabel('Frequency')
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Recent vs historical posts
        if 'is_recent' in self.df.columns:
            recent_counts = self.df['is_recent'].value_counts()
            axes[1, 0].pie(recent_counts.values, labels=['Historical', 'Recent'], 
                          autopct='%1.1f%%', colors=['#F18F01', '#2E86AB'], startangle=90)
            axes[1, 0].set_title('Recent vs Historical Posts', fontweight='bold')
        
        # 4. Content quality metrics
        if 'text_length' in self.df.columns and 'word_count' in self.df.columns:
            # Calculate average words per character
            avg_words_per_char = self.df['word_count'] / self.df['text_length']
            axes[1, 1].hist(avg_words_per_char, bins=30, color='#C73E1D', alpha=0.7, edgecolor='black')
            axes[1, 1].set_title('Content Density (Words per Character)', fontweight='bold')
            axes[1, 1].set_xlabel('Words per Character')
            axes[1, 1].set_ylabel('Frequency')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._fig_to_html(fig)
    
    def _fig_to_html(self, fig):
        """Convert matplotlib figure to HTML"""
        import io
        import base64
        
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f'<img src="data:image/png;base64,{image_base64}" style="width:100%; max-width:800px;">'
    
    def generate_html_report(self):
        """Generate comprehensive HTML report"""
        print("🔄 Generating comprehensive HTML report...")
        
        # Get overview stats
        stats = self.generate_overview_stats()
        
        # Generate all visualizations
        temporal_html = self.create_temporal_analysis()
        geographic_html = self.create_geographic_analysis()
        content_html = self.create_content_analysis()
        author_html = self.create_author_analysis()
        sentiment_html = self.create_sentiment_analysis()
        engagement_html = self.create_engagement_analysis()
        
        # Create HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bluesky Social Justice Data Analysis - FAANG Level EDA</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: rgba(255, 255, 255, 0.95);
                    padding: 30px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .header h1 {{
                    color: #2c3e50;
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 700;
                }}
                .header p {{
                    color: #7f8c8d;
                    font-size: 1.2em;
                    margin: 10px 0 0 0;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background: rgba(255, 255, 255, 0.95);
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    text-align: center;
                    transition: transform 0.3s ease;
                }}
                .stat-card:hover {{
                    transform: translateY(-5px);
                }}
                .stat-number {{
                    font-size: 2.5em;
                    font-weight: 700;
                    color: #2c3e50;
                    margin: 0;
                }}
                .stat-label {{
                    color: #7f8c8d;
                    font-size: 1.1em;
                    margin: 10px 0 0 0;
                }}
                .section {{
                    background: rgba(255, 255, 255, 0.95);
                    padding: 30px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                .section h2 {{
                    color: #2c3e50;
                    font-size: 1.8em;
                    margin: 0 0 20px 0;
                    padding-bottom: 10px;
                    border-bottom: 3px solid #3498db;
                }}
                .chart-container {{
                    text-align: center;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: rgba(255, 255, 255, 0.8);
                    margin-top: 50px;
                    padding: 20px;
                }}
                .badge {{
                    display: inline-block;
                    background: #3498db;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    margin: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Bluesky Social Justice Data Analysis</h1>
                    <p>FAANG-Level Exploratory Data Analysis</p>
                    <div>
                        <span class="badge">Python</span>
                        <span class="badge">Pandas</span>
                        <span class="badge">Matplotlib</span>
                        <span class="badge">Seaborn</span>
                        <span class="badge">WordCloud</span>
                    </div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('total_posts', 0):,}</div>
                        <div class="stat-label">Total Posts</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('unique_authors', 0):,}</div>
                        <div class="stat-label">Unique Authors</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('posts_with_location', 0):,}</div>
                        <div class="stat-label">Posts with Location</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('recent_posts', 0):,}</div>
                        <div class="stat-label">Recent Posts</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('avg_text_length', 0):.0f}</div>
                        <div class="stat-label">Avg Text Length</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('avg_word_count', 0):.0f}</div>
                        <div class="stat-label">Avg Word Count</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📅 Temporal Analysis</h2>
                    <div class="chart-container">
                        {temporal_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>🌍 Geographic Analysis</h2>
                    <div class="chart-container">
                        {geographic_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>📝 Content Analysis</h2>
                    <div class="chart-container">
                        {content_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>👥 Author Analysis</h2>
                    <div class="chart-container">
                        {author_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>😊 Sentiment Analysis</h2>
                    <div class="chart-container">
                        {sentiment_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>📊 Engagement Analysis</h2>
                    <div class="chart-container">
                        {engagement_html}
                    </div>
                </div>
                
                <div class="footer">
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | DFP F25 Social Media Blue Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save HTML report
        with open('eda_analysis_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ HTML report generated: eda_analysis_report.html")
        return html_content

def main():
    """Main execution function"""
    print("🚀 Starting FAANG-Level EDA Analysis...")
    
    # Initialize analyzer
    analyzer = BlueskyEDAAnalyzer()
    
    if analyzer.df.empty:
        print("❌ No data found. Please check the data path.")
        return
    
    # Generate comprehensive report
    analyzer.generate_html_report()
    
    print("🎉 Analysis complete! Open 'eda_analysis_report.html' in your browser.")

if __name__ == "__main__":
    main()
