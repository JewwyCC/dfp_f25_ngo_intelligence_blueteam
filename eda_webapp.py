#!/usr/bin/env python3
"""
FAANG-Level EDA Web Application
Bluesky Social Justice Data Analysis Platform

Professional web interface for data analysis
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
from datetime import datetime, timedelta
import io
import base64
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Set professional styling
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

app = Flask(__name__)

class EDAWebAnalyzer:
    """Web-based EDA analyzer"""
    
    def __init__(self, data_path="data/alltime_socmed/merged_alltime_20250928_221708.csv"):
        self.data_path = data_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load and preprocess data"""
        try:
            self.df = pd.read_csv(self.data_path)
            
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
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df = pd.DataFrame()
    
    def get_overview_stats(self):
        """Get overview statistics"""
        if self.df.empty:
            return {}
        
        stats = {
            'total_posts': len(self.df),
            'unique_authors': self.df['author_handle'].nunique() if 'author_handle' in self.df.columns else 0,
            'date_range': {
                'start': str(self.df['created_at'].min()) if 'created_at' in self.df.columns else None,
                'end': str(self.df['created_at'].max()) if 'created_at' in self.df.columns else None
            },
            'avg_text_length': float(self.df['text_length'].mean()) if 'text_length' in self.df.columns else 0,
            'avg_word_count': float(self.df['word_count'].mean()) if 'word_count' in self.df.columns else 0,
            'posts_with_location': int(self.df['has_location_data'].sum()) if 'has_location_data' in self.df.columns else 0,
            'posts_with_keywords': int(self.df['has_keyword_matches'].sum()) if 'has_keyword_matches' in self.df.columns else 0,
            'recent_posts': int(self.df['is_recent'].sum()) if 'is_recent' in self.df.columns else 0
        }
        
        return stats
    
    def create_temporal_chart(self):
        """Create temporal analysis chart"""
        if self.df.empty or 'created_at' not in self.df.columns:
            return None
        
        daily_posts = self.df.groupby('date').size().reset_index()
        daily_posts.columns = ['date', 'posts']
        
        fig = px.line(daily_posts, x='date', y='posts', 
                     title='Daily Post Volume Over Time',
                     labels={'date': 'Date', 'posts': 'Number of Posts'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def create_geographic_chart(self):
        """Create geographic analysis chart"""
        if self.df.empty or 'detected_location' not in self.df.columns:
            return None
        
        location_df = self.df[self.df['detected_location'].notna()]
        if location_df.empty:
            return None
        
        top_locations = location_df['detected_location'].value_counts().head(15).reset_index()
        top_locations.columns = ['location', 'count']
        
        fig = px.bar(top_locations, x='count', y='location', orientation='h',
                     title='Top 15 Locations by Post Count',
                     labels={'count': 'Number of Posts', 'location': 'Location'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def create_content_chart(self):
        """Create content analysis chart"""
        if self.df.empty or 'text_length' not in self.df.columns:
            return None
        
        fig = px.histogram(self.df, x='text_length', nbins=50,
                          title='Distribution of Text Length',
                          labels={'text_length': 'Character Count', 'count': 'Frequency'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def create_author_chart(self):
        """Create author analysis chart"""
        if self.df.empty or 'author_handle' not in self.df.columns:
            return None
        
        top_authors = self.df['author_handle'].value_counts().head(15).reset_index()
        top_authors.columns = ['author', 'count']
        
        fig = px.bar(top_authors, x='count', y='author', orientation='h',
                     title='Top 15 Authors by Post Count',
                     labels={'count': 'Number of Posts', 'author': 'Author'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def create_sentiment_chart(self):
        """Create sentiment analysis chart"""
        if self.df.empty or 'text' not in self.df.columns:
            return None
        
        # Simple sentiment analysis
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
        
        self.df['sentiment'] = self.df['text'].apply(simple_sentiment)
        sentiment_counts = self.df['sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['sentiment', 'count']
        
        fig = px.pie(sentiment_counts, values='count', names='sentiment',
                     title='Sentiment Distribution',
                     color_discrete_map={'positive': '#2E86AB', 'negative': '#A23B72', 'neutral': '#F18F01'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def create_wordcloud(self):
        """Create word cloud"""
        if self.df.empty or 'text' not in self.df.columns:
            return None
        
        all_text = ' '.join(self.df['text'].dropna().astype(str))
        if not all_text:
            return None
        
        wordcloud = WordCloud(width=800, height=400, background_color='white', 
                            colormap='viridis', max_words=100,
                            stopwords={'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}).generate(all_text)
        
        # Convert to base64
        buffer = io.BytesIO()
        wordcloud.to_image().save(buffer, format='PNG')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{image_base64}"

# Initialize analyzer
analyzer = EDAWebAnalyzer()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('eda_dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get overview statistics"""
    return jsonify(analyzer.get_overview_stats())

@app.route('/api/charts/temporal')
def get_temporal_chart():
    """Get temporal analysis chart"""
    chart = analyzer.create_temporal_chart()
    return chart if chart else jsonify({'error': 'No data available'})

@app.route('/api/charts/geographic')
def get_geographic_chart():
    """Get geographic analysis chart"""
    chart = analyzer.create_geographic_chart()
    return chart if chart else jsonify({'error': 'No data available'})

@app.route('/api/charts/content')
def get_content_chart():
    """Get content analysis chart"""
    chart = analyzer.create_content_chart()
    return chart if chart else jsonify({'error': 'No data available'})

@app.route('/api/charts/authors')
def get_author_chart():
    """Get author analysis chart"""
    chart = analyzer.create_author_chart()
    return chart if chart else jsonify({'error': 'No data available'})

@app.route('/api/charts/sentiment')
def get_sentiment_chart():
    """Get sentiment analysis chart"""
    chart = analyzer.create_sentiment_chart()
    return chart if chart else jsonify({'error': 'No data available'})

@app.route('/api/wordcloud')
def get_wordcloud():
    """Get word cloud"""
    wordcloud = analyzer.create_wordcloud()
    return jsonify({'wordcloud': wordcloud}) if wordcloud else jsonify({'error': 'No data available'})

if __name__ == '__main__':
    print("🚀 Starting FAANG-Level EDA Web Application...")
    print("📊 Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
