#!/usr/bin/env python3
"""
Improved EDA Analysis for Bluesky Homelessness Data
Reuters/NY Times Style Analysis

Clean, professional data analysis with proper distribution and clickable links
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

# Set minimalist styling
plt.style.use('dark_background')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['figure.facecolor'] = '#0a0a0a'
plt.rcParams['axes.facecolor'] = '#0a0a0a'
plt.rcParams['text.color'] = '#ffffff'
plt.rcParams['axes.labelcolor'] = '#ffffff'
plt.rcParams['xtick.color'] = '#ffffff'
plt.rcParams['ytick.color'] = '#ffffff'

class ImprovedEDAAnalyzer:
    """Improved EDA analyzer for Bluesky homelessness data"""
    
    def __init__(self, data_path="../../data/bluesky/alltime_socmed/alltime_socmed.csv"):
        self.data_path = data_path
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load and preprocess data"""
        print("Loading data...")
        try:
            self.df = pd.read_csv(self.data_path)
            print(f"Loaded {len(self.df):,} posts")
            
            # Filter for homelessness-related posts
            homelessness_keywords = ['homeless', 'homelessness', 'unhoused', 'housing crisis', 
                                   'shelter', 'street homeless', 'rough sleeper', 'tent city']
            
            if 'text' in self.df.columns:
                self.df['is_homelessness_related'] = self.df['text'].str.lower().str.contains(
                    '|'.join(homelessness_keywords), na=False
                )
                self.df = self.df[self.df['is_homelessness_related']]
                print(f"Filtered to {len(self.df):,} homelessness-related posts")
            
            # Use existing columns
            if 'char_count' in self.df.columns:
                self.df['text_length'] = self.df['char_count']
            
            print("Data preprocessing complete")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df = pd.DataFrame()
    
    def generate_overview_stats(self):
        """Generate overview statistics"""
        if self.df.empty:
            return {}
        
        stats = {
            'total_posts': len(self.df),
            'unique_authors': self.df['author_handle'].nunique() if 'author_handle' in self.df.columns else 0,
            'avg_text_length': float(self.df['text_length'].mean()) if 'text_length' in self.df.columns else 0,
            'avg_word_count': float(self.df['word_count'].mean()) if 'word_count' in self.df.columns else 0,
            'total_likes': int(self.df['like_count'].sum()) if 'like_count' in self.df.columns else 0,
            'total_reposts': int(self.df['repost_count'].sum()) if 'repost_count' in self.df.columns else 0,
            'avg_likes': float(self.df['like_count'].mean()) if 'like_count' in self.df.columns else 0,
            'avg_reposts': float(self.df['repost_count'].mean()) if 'repost_count' in self.df.columns else 0
        }
        
        return stats
    
    def create_content_analysis(self):
        """Create content analysis with auto-binned histograms"""
        if self.df.empty:
            return ""
        
        # Filter out posts with less than 20 characters and zero values
        filtered_df = self.df[
            (self.df['text'].str.len() >= 20) & 
            (self.df['text_length'] > 0) & 
            (self.df['word_count'] > 0)
        ]
        if filtered_df.empty:
            return ""
        
        # Create subplots with histograms and violin plots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Text Length Distribution', 'Word Count Distribution', 
                          'Text Length Distribution Shape', 'Word Count Distribution Shape'),
            specs=[[{"type": "histogram"}, {"type": "histogram"}],
                   [{"type": "violin"}, {"type": "violin"}]]
        )
        
        # 1. Text length histogram with auto bins (outliers removed)
        if 'text_length' in filtered_df.columns:
            # Remove outliers using IQR method
            Q1 = filtered_df['text_length'].quantile(0.25)
            Q3 = filtered_df['text_length'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            text_length_filtered = filtered_df[(filtered_df['text_length'] >= lower_bound) & (filtered_df['text_length'] <= upper_bound)]['text_length']
            
            fig.add_trace(
                go.Histogram(x=text_length_filtered, nbinsx=0, name='Text Length',
                           marker_color='#1f77b4', opacity=0.7),
                row=1, col=1
            )
        
        # 2. Word count histogram with auto bins (outliers removed)
        if 'word_count' in filtered_df.columns:
            # Remove outliers using IQR method
            Q1 = filtered_df['word_count'].quantile(0.25)
            Q3 = filtered_df['word_count'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            word_count_filtered = filtered_df[(filtered_df['word_count'] >= lower_bound) & (filtered_df['word_count'] <= upper_bound)]['word_count']
            
            fig.add_trace(
                go.Histogram(x=word_count_filtered, nbinsx=0, name='Word Count',
                           marker_color='#ff7f0e', opacity=0.7),
                row=1, col=2
            )
        
        # 3. Text length violin plot (better than boxplot for distribution shape)
        if 'text_length' in filtered_df.columns:
            fig.add_trace(
                go.Violin(y=filtered_df['text_length'], name='Text Length',
                         marker_color='#1f77b4', opacity=0.7,
                         box_visible=True, meanline_visible=True,
                         fillcolor='rgba(31, 119, 180, 0.3)',
                         line_color='#1f77b4'),
                row=2, col=1
            )
        
        # 4. Word count violin plot (better than boxplot for distribution shape)
        if 'word_count' in filtered_df.columns:
            fig.add_trace(
                go.Violin(y=filtered_df['word_count'], name='Word Count',
                         marker_color='#ff7f0e', opacity=0.7,
                         box_visible=True, meanline_visible=True,
                         fillcolor='rgba(255, 127, 14, 0.3)',
                         line_color='#ff7f0e'),
                row=2, col=2
            )
        
        
        # Update layout
        fig.update_layout(
            title="Content Analysis - Homelessness Posts",
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=600
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def create_daily_trend(self):
        """Create daily trend line chart for homelessness conversation"""
        if self.df.empty:
            return ""
        
        # Filter out posts with less than 20 characters
        filtered_df = self.df[self.df['text'].str.len() >= 20]
        if filtered_df.empty:
            return ""
        
        # Check if date column exists, if not create it from created_at
        if 'date' not in filtered_df.columns and 'created_at' in filtered_df.columns:
            try:
                # Use format='mixed' to handle different datetime formats
                filtered_df['created_at'] = pd.to_datetime(filtered_df['created_at'], format='mixed', utc=True)
                filtered_df['date'] = filtered_df['created_at'].dt.date
            except Exception as e:
                return ""
        
        # Group by date and count posts
        if 'date' in filtered_df.columns:
            daily_counts = filtered_df.groupby('date').size().reset_index(name='post_count')
            daily_counts = daily_counts.sort_values('date')
            
            # Create trend line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily_counts['date'],
                y=daily_counts['post_count'],
                mode='lines+markers',
                name='Daily Posts',
                line=dict(color='#00ff00', width=3),
                marker=dict(color='#00ff00', size=6),
                fill='tonexty'
            ))
            
            # Add trend line
            if len(daily_counts) > 1:
                # Calculate trend line using numpy polyfit
                import numpy as np
                x_numeric = np.arange(len(daily_counts))
                z = np.polyfit(x_numeric, daily_counts['post_count'], 1)
                p = np.poly1d(z)
                trend_line = p(x_numeric)
                
                fig.add_trace(go.Scatter(
                    x=daily_counts['date'],
                    y=trend_line,
                    mode='lines',
                    name='Trend',
                    line=dict(color='#ff6b6b', width=2, dash='dash')
                ))
            
            fig.update_layout(
                title="Period Data Pulled",
                xaxis_title="Date",
                yaxis_title="Number of Posts",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400,
                showlegend=True
            )
            
            return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return ""
    
    def create_author_analysis(self):
        """Create author analysis with followers vs engagement scatter"""
        if self.df.empty or 'author_handle' not in self.df.columns:
            return ""
        
        # Filter out posts with less than 20 characters (less restrictive for author analysis)
        filtered_df = self.df[self.df['text'].str.len() >= 20]
        if filtered_df.empty:
            return ""
        
        # Calculate engagement (likes + reposts)
        if 'like_count' in filtered_df.columns and 'repost_count' in filtered_df.columns:
            filtered_df['total_engagement'] = filtered_df['like_count'] + filtered_df['repost_count']
        else:
            return ""
        
        # Filter out zero engagement
        engagement_df = filtered_df[filtered_df['total_engagement'] > 0]
        if engagement_df.empty:
            return ""
        
        # Create scatter plot
        fig = go.Figure()
        
        if 'author_followers_count' in engagement_df.columns:
            fig.add_trace(go.Scatter(
                x=engagement_df['author_followers_count'],
                y=engagement_df['total_engagement'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=engagement_df['total_engagement'],
                    colorscale='Viridis',
                    opacity=0.6,
                    showscale=True,
                    colorbar=dict(title="Total Engagement")
                ),
                text=engagement_df['author_handle'],
                hovertemplate='<b>@%{text}</b><br>' +
                            'Followers: %{x:,}<br>' +
                            'Engagement: %{y}<br>' +
                            '<extra></extra>'
            ))
        
        fig.update_layout(
            title="Author Followers vs Engagement - Homelessness Posts",
            xaxis_title="Follower Count",
            yaxis_title="Total Engagement (Likes + Reposts)",
            xaxis_type="log",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def create_engagement_analysis(self):
        """Create engagement analysis with auto-binned histograms"""
        if self.df.empty:
            return ""
        
        # Filter out posts with less than 20 characters (less restrictive for engagement)
        filtered_df = self.df[self.df['text'].str.len() >= 20]
        if filtered_df.empty:
            return ""
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Like Distribution', 'Repost Distribution'),
            specs=[[{"type": "violin"}, {"type": "violin"}]]
        )
        
        # 1. Like distribution violin plot (exclude zero values, filter to upper fence)
        if 'like_count' in filtered_df.columns:
            likes_data = filtered_df[filtered_df['like_count'] > 0]['like_count']
            if not likes_data.empty and likes_data.min() >= 0:
                # Filter to upper fence using IQR method
                Q1 = likes_data.quantile(0.25)
                Q3 = likes_data.quantile(0.75)
                IQR = Q3 - Q1
                upper_fence = Q3 + 1.5 * IQR
                likes_filtered = likes_data[likes_data <= upper_fence]
                
                fig.add_trace(
                    go.Violin(y=likes_filtered, name='Likes',
                             marker_color='#1f77b4', opacity=0.7,
                             box_visible=True, meanline_visible=True,
                             fillcolor='rgba(31, 119, 180, 0.3)',
                             line_color='#1f77b4'),
                    row=1, col=1
                )
        
        # 2. Repost distribution violin plot (exclude zero values, filter to upper fence)
        if 'repost_count' in filtered_df.columns:
            reposts_data = filtered_df[filtered_df['repost_count'] > 0]['repost_count']
            if not reposts_data.empty and reposts_data.min() >= 0:
                # Filter to upper fence using IQR method
                Q1 = reposts_data.quantile(0.25)
                Q3 = reposts_data.quantile(0.75)
                IQR = Q3 - Q1
                upper_fence = Q3 + 1.5 * IQR
                reposts_filtered = reposts_data[reposts_data <= upper_fence]
                
                fig.add_trace(
                    go.Violin(y=reposts_filtered, name='Reposts',
                             marker_color='#ff7f0e', opacity=0.7,
                             box_visible=True, meanline_visible=True,
                             fillcolor='rgba(255, 127, 14, 0.3)',
                             line_color='#ff7f0e'),
                    row=1, col=2
                )
        
        fig.update_layout(
            title="Engagement Analysis - Homelessness Posts",
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def create_detailed_content_features(self):
        """Create detailed content features with top 5 items based on engagement"""
        if self.df.empty:
            return ""
        
        # Use the original full dataset for content features (not just homelessness filtered)
        # Load the original data
        import pandas as pd
        from pathlib import Path
        
        data_dir = Path("../../data/bluesky/alltime_socmed")
        csv_files = list(data_dir.glob("alltime_socmed*.csv"))
        if not csv_files:
            return ""
        
        latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
        full_df = pd.read_csv(latest_file)
        
        # Filter out posts with less than 20 characters
        filtered_df = full_df[full_df['text'].str.len() >= 20].copy()
        if filtered_df.empty:
            return ""
        
        # Calculate total engagement safely
        engagement_cols = ['like_count', 'repost_count', 'reply_count']
        filtered_df['total_engagement'] = 0
        for col in engagement_cols:
            if col in filtered_df.columns:
                filtered_df['total_engagement'] += filtered_df[col].fillna(0)
        
        # Don't filter by engagement for content features - we want all posts with content
        engagement_df = filtered_df
        
        features_html = []
        
        # Top 5 Hashtags by engagement
        if 'hashtags' in engagement_df.columns:
            hashtag_engagement = []
            hashtag_count = 0
            for _, row in engagement_df.iterrows():
                if pd.notna(row['hashtags']) and row['hashtags']:
                    try:
                        import ast
                        hashtags = ast.literal_eval(row['hashtags']) if isinstance(row['hashtags'], str) else row['hashtags']
                        if isinstance(hashtags, list) and hashtags:
                            hashtag_count += 1
                            for hashtag in hashtags:
                                hashtag_engagement.append({
                                    'hashtag': hashtag,
                                    'engagement': row['total_engagement']
                                })
                    except:
                        continue
            
            if hashtag_engagement:
                hashtag_df = pd.DataFrame(hashtag_engagement)
                top_hashtags = hashtag_df.groupby('hashtag')['engagement'].sum().nlargest(5)
                
                if not top_hashtags.empty:
                    features_html.append('<div class="feature-card">')
                    features_html.append('<h3>🔥 Top 5 Hashtags by Engagement</h3>')
                    features_html.append('<div class="feature-list">')
                    for i, (hashtag, engagement) in enumerate(top_hashtags.items(), 1):
                        # Link to search for this hashtag on Bluesky
                        search_link = f"https://bsky.app/search?q={hashtag}"
                        features_html.append(f'<div class="feature-item"><span class="rank">{i}.</span> #{hashtag} <a href="{search_link}" target="_blank" class="post-link">View Hashtag</a></div>')
                    features_html.append('</div></div>')
                else:
                    # If no hashtags with engagement, show top hashtags by count
                    top_hashtag_posts = engagement_df.nlargest(5, 'hashtag_count')
                    if not top_hashtag_posts.empty:
                        features_html.append('<div class="feature-card">')
                        features_html.append('<h3>🔥 Top 5 Posts with Most Hashtags</h3>')
                        features_html.append('<div class="feature-list">')
                        for i, (_, post) in enumerate(top_hashtag_posts.iterrows(), 1):
                            text_preview = post['text'][:80] + '...' if len(post['text']) > 80 else post['text']
                            if pd.notna(post['author_handle']) and pd.notna(post['uri']):
                                post_id = post['uri'].split('/')[-1]
                                post_link = f"https://bsky.app/profile/{post['author_handle']}/post/{post_id}"
                                features_html.append(f'<div class="feature-item"><span class="rank">{i}.</span> "{text_preview}" <a href="{post_link}" target="_blank" class="post-link">View Post</a></div>')
                            else:
                                features_html.append(f'<div class="feature-item"><span class="rank">{i}.</span> "{text_preview}"</div>')
                        features_html.append('</div></div>')
        
        # Top 5 Mentions by engagement
        if 'mentions' in engagement_df.columns:
            mention_engagement = []
            for _, row in engagement_df.iterrows():
                if pd.notna(row['mentions']) and row['mentions']:
                    try:
                        import ast
                        mentions = ast.literal_eval(row['mentions']) if isinstance(row['mentions'], str) else row['mentions']
                        if isinstance(mentions, list) and mentions:
                            for mention in mentions:
                                mention_engagement.append({
                                    'mention': mention,
                                    'engagement': row['total_engagement']
                                })
                    except:
                        continue
            
            if mention_engagement:
                mention_df = pd.DataFrame(mention_engagement)
                top_mentions = mention_df.groupby('mention')['engagement'].sum().nlargest(5)
                
                if not top_mentions.empty:
                    features_html.append('<div class="feature-card">')
                    features_html.append('<h3>👥 Top 5 Mentions by Engagement</h3>')
                    features_html.append('<div class="feature-list">')
                    for i, (mention, engagement) in enumerate(top_mentions.items(), 1):
                        # Link to the mentioned user's profile
                        profile_link = f"https://bsky.app/profile/{mention}"
                        features_html.append(f'<div class="feature-item"><span class="rank">{i}.</span> @{mention} <a href="{profile_link}" target="_blank" class="post-link">View Profile</a></div>')
                    features_html.append('</div></div>')
                else:
                    # If no mentions with engagement, show top mentions by count
                    top_mention_posts = engagement_df.nlargest(5, 'mention_count')
                    if not top_mention_posts.empty:
                        features_html.append('<div class="feature-card">')
                        features_html.append('<h3>👥 Top 5 Posts with Most Mentions</h3>')
                        features_html.append('<div class="feature-list">')
                        for i, (_, post) in enumerate(top_mention_posts.iterrows(), 1):
                            text_preview = post['text'][:80] + '...' if len(post['text']) > 80 else post['text']
                            if pd.notna(post['author_handle']) and pd.notna(post['uri']):
                                post_id = post['uri'].split('/')[-1]
                                post_link = f"https://bsky.app/profile/{post['author_handle']}/post/{post_id}"
                                features_html.append(f'<div class="feature-item"><span class="rank">{i}.</span> "{text_preview}" <a href="{post_link}" target="_blank" class="post-link">View Post</a></div>')
                            else:
                                features_html.append(f'<div class="feature-item"><span class="rank">{i}.</span> "{text_preview}"</div>')
                        features_html.append('</div></div>')
        
        # Top 5 URLs by engagement
        if 'urls' in engagement_df.columns:
            url_engagement = []
            url_count = 0
            for _, row in engagement_df.iterrows():
                if pd.notna(row['urls']) and row['urls']:
                    try:
                        import ast
                        urls = ast.literal_eval(row['urls']) if isinstance(row['urls'], str) else row['urls']
                        if isinstance(urls, list) and urls:
                            url_count += 1
                            for url in urls:
                                url_engagement.append({
                                    'url': url,
                                    'engagement': row['total_engagement']
                                })
                    except:
                        continue
            
            if url_engagement:
                url_df = pd.DataFrame(url_engagement)
                top_urls = url_df.groupby('url')['engagement'].sum().nlargest(5)
                
                if not top_urls.empty:
                    features_html.append('<div class="feature-card">')
                    features_html.append('<h3>🔗 Top 5 URLs by Engagement</h3>')
                    features_html.append('<div class="feature-list">')
                    for i, (url, engagement) in enumerate(top_urls.items(), 1):
                        # Find the post with this URL for the link
                        url_post = None
                        for _, row in engagement_df.iterrows():
                            if pd.notna(row['urls']) and row['urls']:
                                try:
                                    import ast
                                    urls = ast.literal_eval(row['urls']) if isinstance(row['urls'], str) else row['urls']
                                    if isinstance(urls, list) and url in urls:
                                        url_post = row
                                        break
                                except:
                                    continue
                        
                        short_url = url[:50] + '...' if len(url) > 50 else url
                        if url_post is not None and pd.notna(url_post['author_handle']):
                            post_id = url_post['uri'].split('/')[-1] if pd.notna(url_post['uri']) else ''
                            post_link = f"https://bsky.app/profile/{url_post['author_handle']}/post/{post_id}"
                            features_html.append(f'<div class="feature-item"><span class="rank">{i}.</span> <a href="{url}" target="_blank" class="url-link">{short_url}</a> <a href="{post_link}" target="_blank" class="post-link">View Post</a></div>')
                        else:
                            features_html.append(f'<div class="feature-item"><span class="rank">{i}.</span> <a href="{url}" target="_blank" class="url-link">{short_url}</a> <span class="engagement">({int(engagement):,})</span></div>')
                    features_html.append('</div></div>')
                else:
                    # If no URLs with engagement, show top URLs by count
                    top_url_posts = engagement_df.nlargest(5, 'url_count')
                    if not top_url_posts.empty:
                        features_html.append('<div class="feature-card">')
                        features_html.append('<h3>🔗 Top 5 Posts with Most URLs</h3>')
                        features_html.append('<div class="feature-list">')
                        for i, (_, post) in enumerate(top_url_posts.iterrows(), 1):
                            text_preview = post['text'][:80] + '...' if len(post['text']) > 80 else post['text']
                            if pd.notna(post['author_handle']) and pd.notna(post['uri']):
                                post_id = post['uri'].split('/')[-1]
                                post_link = f"https://bsky.app/profile/{post['author_handle']}/post/{post_id}"
                                features_html.append(f'<div class="feature-item"><span class="rank">{i}.</span> "{text_preview}" <a href="{post_link}" target="_blank" class="post-link">View Post</a></div>')
                            else:
                                features_html.append(f'<div class="feature-item"><span class="rank">{i}.</span> "{text_preview}"</div>')
                        features_html.append('</div></div>')
        
        # Top 5 Media by engagement
        if 'has_images' in engagement_df.columns:
            media_posts = engagement_df[engagement_df['has_images'] == True].nlargest(5, 'total_engagement')
            
            if not media_posts.empty:
                features_html.append('<div class="feature-card">')
                features_html.append('<h3>📸 Top 5 Media Posts by Engagement</h3>')
                features_html.append('<div class="feature-list">')
                for i, (_, post) in enumerate(media_posts.iterrows(), 1):
                    text_preview = post['text'][:100] + '...' if len(post['text']) > 100 else post['text']
                    # Add media indicator
                    media_indicator = "📷 " if post.get('has_images', False) else ""
                    
                    # Create link to original post
                    if pd.notna(post['author_handle']) and pd.notna(post['uri']):
                        post_id = post['uri'].split('/')[-1]
                        post_link = f"https://bsky.app/profile/{post['author_handle']}/post/{post_id}"
                        features_html.append(f'<div class="feature-item"><span class="rank">{i}.</span> {media_indicator}"{text_preview}" <a href="{post_link}" target="_blank" class="post-link">View Post</a></div>')
                    else:
                        features_html.append(f'<div class="feature-item"><span class="rank">{i}.</span> {media_indicator}"{text_preview}"</div>')
                features_html.append('</div></div>')
        
        return ''.join(features_html)
    
    def create_wordcloud(self):
        """Create word cloud with better filtering"""
        if self.df.empty or 'text' not in self.df.columns:
            return ""
        
        # Filter out posts with less than 20 characters (less restrictive for word cloud)
        filtered_df = self.df[self.df['text'].str.len() >= 20]
        if filtered_df.empty:
            return ""
        
        all_text = ' '.join(filtered_df['text'].dropna().astype(str))
        if not all_text:
            return ""
        
        # Enhanced stopwords list
        stopwords = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
            'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'among', 'under', 'over', 'around', 'near', 'far', 'here', 'there', 'where',
            'when', 'why', 'how', 'what', 'who', 'which', 'whom', 'whose', 'if', 'then', 'else',
            'because', 'so', 'as', 'than', 'like', 'just', 'now', 'then', 'also', 'only', 'even',
            'still', 'yet', 'already', 'again', 'more', 'most', 'some', 'any', 'all', 'both',
            'each', 'every', 'other', 'another', 'same', 'such', 'no', 'not', 'nor', 'neither',
            'either', 'both', 'few', 'many', 'much', 'little', 'less', 'least', 'most', 'more',
            'very', 'quite', 'rather', 'pretty', 'too', 'so', 'enough', 'almost', 'nearly',
            'quite', 'rather', 'somewhat', 'somehow', 'anyway', 'anyhow', 'somewhere', 'anywhere',
            'everywhere', 'nowhere', 'somewhere', 'anywhere', 'everywhere', 'nowhere',
            'homeless', 'homelessness'  # Exclude the literal words from word cloud
        }
        
        wordcloud = WordCloud(
            width=800, height=400, 
            background_color='black',
            colormap='viridis', 
            max_words=100,
            stopwords=stopwords,
            min_font_size=10,
            max_font_size=100,
            relative_scaling=0.5
        ).generate(all_text)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Content Word Cloud - Homelessness Posts', fontsize=16, fontweight='bold', color='white', pad=20)
        
        # Center the word cloud
        plt.tight_layout()
        
        return self._fig_to_html(fig)
    
    def create_geolocation_analysis(self):
        """Create geolocation cloud and world map for location mentions"""
        if self.df.empty:
            return "", ""
        
        try:
            import re
            from collections import Counter
            
            # Location patterns to search for
            us_states = ['california', 'texas', 'florida', 'new york', 'washington', 'oregon', 'nevada', 'arizona', 'colorado', 'utah', 'illinois', 'pennsylvania', 'ohio', 'georgia', 'north carolina', 'michigan', 'new jersey', 'virginia', 'tennessee', 'indiana', 'missouri', 'maryland', 'wisconsin', 'minnesota', 'louisiana', 'alabama', 'kentucky', 'south carolina', 'oklahoma', 'connecticut', 'iowa', 'utah', 'nevada', 'arkansas', 'mississippi', 'kansas', 'new mexico', 'nebraska', 'west virginia', 'idaho', 'hawaii', 'new hampshire', 'maine', 'montana', 'rhode island', 'delaware', 'south dakota', 'north dakota', 'alaska', 'vermont', 'wyoming']
            
            cities = ['los angeles', 'san francisco', 'seattle', 'portland', 'denver', 'phoenix', 'las vegas', 'miami', 'chicago', 'boston', 'new york', 'austin', 'dallas', 'houston', 'atlanta', 'detroit', 'philadelphia', 'pittsburgh', 'cleveland', 'columbus', 'cincinnati', 'indianapolis', 'milwaukee', 'minneapolis', 'st paul', 'kansas city', 'st louis', 'nashville', 'memphis', 'birmingham', 'new orleans', 'jacksonville', 'tampa', 'orlando', 'miami', 'atlanta', 'charlotte', 'raleigh', 'richmond', 'norfolk', 'baltimore', 'washington', 'pittsburgh', 'philadelphia', 'newark', 'jersey city', 'buffalo', 'rochester', 'syracuse', 'albany', 'hartford', 'providence', 'worcester', 'springfield', 'bridgeport', 'new haven', 'stamford', 'waterbury', 'norwalk', 'danbury', 'bristol', 'meriden', 'west hartford', 'east hartford', 'hamden', 'milford', 'stratford', 'trumbull', 'fairfield', 'greenwich', 'stamford', 'norwalk', 'westport', 'darien', 'new canaan', 'ridgefield', 'wilton', 'redding', 'easton', 'weston', 'wilton', 'newtown', 'shelton', 'derby', 'ansonia', 'naugatuck', 'beacon falls', 'oxford', 'southbury', 'woodbury', 'bethlehem', 'roxbury', 'washington', 'bridgewater', 'sherman', 'kent', 'cornwall', 'sharon', 'canaan', 'north canaan', 'salisbury', 'lakeville', 'sharon', 'cornwall', 'canaan', 'north canaan', 'salisbury', 'lakeville', 'sharon', 'cornwall', 'canaan', 'north canaan', 'salisbury', 'lakeville']
            
            countries = ['usa', 'united states', 'america', 'canada', 'uk', 'united kingdom', 'australia', 'germany', 'france', 'spain', 'italy', 'netherlands', 'sweden', 'norway', 'denmark', 'finland', 'belgium', 'switzerland', 'austria', 'portugal', 'ireland', 'new zealand', 'japan', 'south korea', 'china', 'india', 'brazil', 'mexico', 'argentina', 'chile', 'colombia', 'peru', 'venezuela', 'ecuador', 'bolivia', 'paraguay', 'uruguay', 'guyana', 'suriname', 'french guiana']
            
            all_locations = us_states + cities + countries
            
            # Count location mentions
            location_mentions = Counter()
            for _, row in self.df.iterrows():
                text = str(row['text']).lower()
                for location in all_locations:
                    if location in text:
                        location_mentions[location] += 1
            
            # Get top locations (more locations for better cloud)
            top_locations = dict(location_mentions.most_common(50))
            
            if not top_locations:
                return "", ""
            
            # Create geolocation cloud
            geolocation_cloud_html = self._create_location_cloud(top_locations)
            
            # Create world map
            world_map_html = self._create_world_map(top_locations)
            
            return geolocation_cloud_html, world_map_html
            
        except Exception as e:
            print(f"Geolocation analysis error: {e}")
            return "", ""
    
    def _create_location_cloud(self, locations):
        """Create a location cloud similar to word cloud"""
        try:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
            from io import BytesIO
            import base64
            
            # Create frequency dictionary for wordcloud
            location_freq = {loc: count for loc, count in locations.items()}
            
            # Create location cloud (same size as word cloud)
            wordcloud = WordCloud(
                width=800, height=400,
                background_color='black',
                colormap='plasma',
                max_words=100,
                relative_scaling=0.5,
                min_font_size=10,
                max_font_size=100,
                random_state=42
            ).generate_from_frequencies(location_freq)
            
            # Convert to base64 (same size as word cloud)
            img_buffer = BytesIO()
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title('Geolocation Cloud - Homelessness Posts', fontsize=16, fontweight='bold', color='white', pad=20)
            plt.tight_layout()
            plt.savefig(img_buffer, format='png', facecolor='#0a0a0a', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return f'<div class="wordcloud-container"><img src="data:image/png;base64,{img_base64}" alt="Location Cloud" style="max-width: 100%; height: auto; border-radius: 8px;"></div>'
            
        except Exception as e:
            print(f"Location cloud error: {e}")
            return ""
    
    def _create_world_map(self, locations):
        """Create a world map showing location mentions"""
        try:
            import plotly.graph_objects as go
            
            # Location coordinates (simplified mapping)
            location_coords = {
                'california': {'lat': 36.7783, 'lon': -119.4179, 'country': 'USA'},
                'texas': {'lat': 31.9686, 'lon': -99.9018, 'country': 'USA'},
                'florida': {'lat': 27.7663, 'lon': -81.6868, 'country': 'USA'},
                'new york': {'lat': 42.1657, 'lon': -74.9481, 'country': 'USA'},
                'washington': {'lat': 47.7511, 'lon': -120.7401, 'country': 'USA'},
                'oregon': {'lat': 43.8041, 'lon': -120.5542, 'country': 'USA'},
                'nevada': {'lat': 38.4199, 'lon': -117.1219, 'country': 'USA'},
                'arizona': {'lat': 33.7298, 'lon': -111.4312, 'country': 'USA'},
                'colorado': {'lat': 39.0598, 'lon': -105.3111, 'country': 'USA'},
                'utah': {'lat': 40.1500, 'lon': -111.8624, 'country': 'USA'},
                'seattle': {'lat': 47.6062, 'lon': -122.3321, 'country': 'USA'},
                'los angeles': {'lat': 34.0522, 'lon': -117.2437, 'country': 'USA'},
                'san francisco': {'lat': 37.7749, 'lon': -122.4194, 'country': 'USA'},
                'chicago': {'lat': 41.8781, 'lon': -87.6298, 'country': 'USA'},
                'boston': {'lat': 42.3601, 'lon': -71.0589, 'country': 'USA'},
                'miami': {'lat': 25.7617, 'lon': -80.1918, 'country': 'USA'},
                'houston': {'lat': 29.7604, 'lon': -95.3698, 'country': 'USA'},
                'dallas': {'lat': 32.7767, 'lon': -96.7970, 'country': 'USA'},
                'austin': {'lat': 30.2672, 'lon': -97.7431, 'country': 'USA'},
                'portland': {'lat': 45.5152, 'lon': -122.6784, 'country': 'USA'},
                'denver': {'lat': 39.7392, 'lon': -104.9903, 'country': 'USA'},
                'phoenix': {'lat': 33.4484, 'lon': -112.0740, 'country': 'USA'},
                'las vegas': {'lat': 36.1699, 'lon': -115.1398, 'country': 'USA'},
                'usa': {'lat': 39.8283, 'lon': -98.5795, 'country': 'USA'},
                'united states': {'lat': 39.8283, 'lon': -98.5795, 'country': 'USA'},
                'america': {'lat': 39.8283, 'lon': -98.5795, 'country': 'USA'},
                'canada': {'lat': 56.1304, 'lon': -106.3468, 'country': 'Canada'},
                'uk': {'lat': 55.3781, 'lon': -3.4360, 'country': 'UK'},
                'united kingdom': {'lat': 55.3781, 'lon': -3.4360, 'country': 'UK'},
                'australia': {'lat': -25.2744, 'lon': 133.7751, 'country': 'Australia'},
                'germany': {'lat': 51.1657, 'lon': 10.4515, 'country': 'Germany'},
                'france': {'lat': 46.2276, 'lon': 2.2137, 'country': 'France'}
            }
            
            # Prepare data for map
            lats, lons, texts, sizes, colors = [], [], [], [], []
            
            # Get min and max counts for color scaling
            counts = list(locations.values())
            min_count = min(counts) if counts else 1
            max_count = max(counts) if counts else 1
            
            for location, count in locations.items():
                if location in location_coords:
                    coords = location_coords[location]
                    lats.append(coords['lat'])
                    lons.append(coords['lon'])
                    texts.append(f"{location.title()}<br>Mentions: {count}")
                    # Smaller, more distinct bubble sizes
                    sizes.append(min(max(count * 0.8, 5), 25))
                    # Color based on mention count (normalized)
                    colors.append(count)
            
            if not lats:
                return ""
            
            # Create map
            fig = go.Figure()
            
            # Add scatter plot
            fig.add_trace(go.Scattergeo(
                lat=lats,
                lon=lons,
                text=texts,
                mode='markers',
                marker=dict(
                    size=sizes,
                    color=colors,
                    colorscale='Plasma',
                    showscale=True,
                    colorbar=dict(
                        title="Mention Count",
                        titleside="right",
                        tickmode='linear',
                        tick0=min_count,
                        dtick=(max_count - min_count) / 5
                    ),
                    line=dict(width=2, color='white'),
                    opacity=0.9,
                    sizemode='diameter',
                    sizemin=3
                ),
                hovertemplate='%{text}<extra></extra>'
            ))
            
            # Update layout
            fig.update_layout(
                title="Geographic Distribution of Homelessness Discussions",
                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    projection_type='equirectangular',
                    bgcolor='#0a0a0a',
                    showland=True,
                    landcolor='#1a1a1a',
                    showocean=True,
                    oceancolor='#0a0a0a'
                ),
                plot_bgcolor='#0a0a0a',
                paper_bgcolor='#0a0a0a',
                font=dict(color='white'),
                height=500
            )
            
            return fig.to_html(full_html=False, include_plotlyjs='cdn')
            
        except Exception as e:
            print(f"World map error: {e}")
            return ""
    
    def create_top_posts_feed(self, sort_by='like_count', title="Top 10 Posts by Likes"):
        """Create top posts feed with clickable links"""
        if self.df.empty or sort_by not in self.df.columns:
            return ""
        
        # Filter out posts with less than 20 characters (less restrictive for post feeds)
        filtered_df = self.df[self.df['text'].str.len() >= 20]
        if filtered_df.empty:
            return ""
        
        # Get top 10 posts
        if sort_by == 'author_followers_count':
            # Top post per author by followers
            top_authors = filtered_df.nlargest(10, 'author_followers_count').drop_duplicates('author_handle')
            top_posts = top_authors.head(10)
        else:
            top_posts = filtered_df.nlargest(10, sort_by)
        
        html_posts = []
        for i, (_, post) in enumerate(top_posts.iterrows(), 1):
            author = post.get('author_handle', 'Unknown')
            text = post.get('text', 'No text available')
            likes = post.get('like_count', 0)
            reposts = post.get('repost_count', 0)
            created_at = post.get('created_at', 'Unknown date')
            uri = post.get('uri', '')
            
            # Create clickable link to original post
            if uri:
                # Convert Bluesky URI to web URL
                if 'at://' in uri:
                    # Extract handle and post ID from at:// URI
                    uri_parts = uri.replace('at://', '').split('/')
                    if len(uri_parts) >= 3:
                        handle = uri_parts[0]
                        post_id = uri_parts[2]
                        web_url = f"https://bsky.app/profile/{handle}/post/{post_id}"
                    else:
                        web_url = f"https://bsky.app/profile/{author}"
                else:
                    web_url = f"https://bsky.app/profile/{author}"
            else:
                web_url = f"https://bsky.app/profile/{author}"
            
            # Show full text without truncation
            post_html = f"""
            <div class="post-item">
                <div class="post-header">
                    <span class="post-number">#{i}</span>
                    <a href="{web_url}" target="_blank" class="post-author">@{author}</a>
                    <span class="post-date">{created_at}</span>
                </div>
                <div class="post-content">
                    {text}
                </div>
                <div class="post-stats">
                    <span class="likes">❤️ {likes}</span>
                    <span class="reposts">🔄 {reposts}</span>
                    <a href="{web_url}" target="_blank" class="view-original">View Original →</a>
                </div>
            </div>
            """
            html_posts.append(post_html)
        
        return ''.join(html_posts)
    
    def _fig_to_html(self, fig):
        """Convert matplotlib figure to HTML"""
        import io
        import base64
        
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='#0a0a0a', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f'<img src="data:image/png;base64,{image_base64}" style="width:100%; max-width:800px;">'
    
    def generate_html_report(self):
        """Generate improved HTML report"""
        print("Generating analysis report...")
        
        # Get overview stats
        stats = self.generate_overview_stats()
        
        # Generate all visualizations
        content_html = self.create_content_analysis()
        daily_trend_html = self.create_daily_trend()
        author_html = self.create_author_analysis()
        engagement_html = self.create_engagement_analysis()
        wordcloud_html = self.create_wordcloud()
        detailed_features_html = self.create_detailed_content_features()
        
        # Generate geolocation analysis
        geolocation_cloud_html, world_map_html = self.create_geolocation_analysis()
        
        # Generate different post feeds
        top_likes_html = self.create_top_posts_feed('like_count', "Top 10 Posts by Likes")
        top_followers_html = self.create_top_posts_feed('author_followers_count', "Top 10 Posts by Most Followed Authors")
        top_reposts_html = self.create_top_posts_feed('repost_count', "Top 10 Posts by Reposts")
        
        # Create HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bluesky Homelessness Data Analysis</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
                    background: #0a0a0a;
                    color: #ffffff;
                    line-height: 1.6;
                    padding: 20px;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                
                .header {{
                    border-bottom: 2px solid #00ff00;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                
                .header h1 {{
                    color: #00ff00;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    font-weight: bold;
                }}
                
                .header p {{
                    color: #888;
                    font-size: 1.2em;
                }}
                
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                    margin-bottom: 40px;
                }}
                
                .stat {{
                    background: #111;
                    border: 1px solid #333;
                    padding: 20px;
                    text-align: center;
                }}
                
                .stat-number {{
                    color: #00ff00;
                    font-size: 2.5em;
                    font-weight: bold;
                }}
                
                .stat-label {{
                    color: #888;
                    margin-top: 5px;
                    font-size: 0.9em;
                }}
                
                .section {{
                    margin-bottom: 40px;
                    background: #111;
                    border: 1px solid #333;
                    padding: 30px;
                }}
                
                .section h2 {{
                    color: #00ff00;
                    font-size: 1.8em;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #00ff00;
                    padding-bottom: 10px;
                }}
                
                .chart-container {{
                    margin: 20px 0;
                }}
                
                .wordcloud-container {{
                    text-align: center;
                    margin: 20px 0;
                }}
                
                .keywords-section {{
                    text-align: center;
                }}
                
                .post-item {{
                    background: #1a1a1a;
                    border: 1px solid #333;
                    margin-bottom: 15px;
                    padding: 20px;
                    border-radius: 5px;
                }}
                
                .post-header {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                    font-size: 0.9em;
                    color: #888;
                }}
                
                .post-number {{
                    color: #00ff00;
                    font-weight: bold;
                }}
                
                .post-author {{
                    color: #00aaff;
                    text-decoration: none;
                }}
                
                .post-author:hover {{
                    text-decoration: underline;
                    color: #00ccff;
                }}
                
                .post-content {{
                    margin: 15px 0;
                    font-size: 1.1em;
                    line-height: 1.5;
                    color: #ffffff;
                }}
                
                .post-stats {{
                    display: flex;
                    gap: 20px;
                    font-size: 0.9em;
                    color: #888;
                }}
                
                .likes {{
                    color: #ff6b6b;
                }}
                
                .reposts {{
                    color: #4ecdc4;
                }}
                
                .view-original {{
                    color: #00aaff;
                    text-decoration: none;
                }}
                
                .view-original:hover {{
                    text-decoration: underline;
                    color: #00ccff;
                }}
                
                .footer {{
                    text-align: center;
                    color: #888;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #333;
                }}
                
                .keywords-section {{
                    margin: 20px 0;
                }}
                
                .keywords-title {{
                    color: #00ff00;
                    font-size: 1.2em;
                    margin-bottom: 15px;
                    font-weight: bold;
                }}
                
                .keywords-grid {{
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                    margin: 15px auto;
                    max-width: 800px;
                    align-items: center;
                }}
                
                .keywords-row1, .keywords-row2 {{
                    display: flex;
                    gap: 10px;
                    justify-content: center;
                    flex-wrap: wrap;
                }}
                
                
                .keyword-box {{
                    background: #111;
                    border: 1px solid #333;
                    padding: 10px;
                    text-align: center;
                    border-radius: 5px;
                    transition: all 0.3s ease;
                }}
                
                .keyword-box:hover {{
                    background: #1a1a1a;
                    border-color: #00ff00;
                    transform: translateY(-2px);
                }}
                
                .keyword-link {{
                    color: #00aaff;
                    text-decoration: none;
                    font-weight: bold;
                }}
                
                .keyword-link:hover {{
                    color: #00ccff;
                    text-decoration: underline;
                }}
                
                .data-source {{
                    margin-top: 15px;
                    font-style: italic;
                    color: #666;
                }}
                
                .feature-cards {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    margin: 20px 0;
                }}
                
                .feature-card {{
                    background: #1a1a1a;
                    border: 1px solid #333;
                    padding: 20px;
                    border-radius: 8px;
                }}
                
                .feature-card h3 {{
                    color: #00ff00;
                    margin-bottom: 15px;
                    font-size: 1.1em;
                }}
                
                .feature-list {{
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }}
                
                .feature-item {{
                    display: flex;
                    align-items: center;
                    padding: 8px;
                    background: #111;
                    border-radius: 4px;
                    font-size: 0.9em;
                }}
                
                .rank {{
                    color: #00ff00;
                    font-weight: bold;
                    margin-right: 10px;
                    min-width: 20px;
                }}
                
                .engagement {{
                    color: #00aaff;
                    font-weight: bold;
                    margin-left: auto;
                }}
                
                .url-link {{
                    color: #00aaff;
                    text-decoration: none;
                }}
                
                .url-link:hover {{
                    text-decoration: underline;
                    color: #00ccff;
                }}
                
                .post-link {{
                    color: #00ff00;
                    text-decoration: none;
                    font-size: 0.9em;
                    margin-left: 10px;
                }}
                
                .post-link:hover {{
                    text-decoration: underline;
                }}
                
                /* Scraper Control Styles */
                .scraper-controls {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                
                .control-group {{
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }}
                
                .control-group label {{
                    color: #00ff00;
                    font-weight: bold;
                    font-size: 0.9em;
                }}
                
                .control-group select,
                .control-group input {{
                    background: #1a1a1a;
                    border: 1px solid #333;
                    color: #ffffff;
                    padding: 10px;
                    border-radius: 4px;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
                }}
                
                .control-group select:focus,
                .control-group input:focus {{
                    outline: none;
                    border-color: #00ff00;
                    box-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
                }}
                
                .help-text {{
                    color: #888;
                    font-size: 0.8em;
                    margin-top: 5px;
                    display: block;
                }}
                
                .relevance-check {{
                    margin-top: 10px;
                    padding: 10px;
                    border-radius: 4px;
                    font-size: 0.9em;
                }}
                
                .relevance-check.relevant {{
                    background: #1a3a1a;
                    border: 1px solid #00ff00;
                    color: #00ff00;
                }}
                
                .relevance-check.not-relevant {{
                    background: #1a1a3a;
                    border: 1px solid #6666ff;
                    color: #6666ff;
                }}
                
                .button-group {{
                    display: flex;
                    gap: 15px;
                    align-items: end;
                }}
                
                .run-button,
                .refresh-button {{
                    background: #00ff00;
                    color: #000000;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 4px;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                
                .run-button:hover,
                .refresh-button:hover {{
                    background: #00cc00;
                    transform: translateY(-2px);
                }}
                
                .run-button:disabled {{
                    background: #666;
                    cursor: not-allowed;
                    transform: none;
                }}
                
                .scraper-status,
                .refresh-status {{
                    background: #1a1a1a;
                    border: 1px solid #333;
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 20px;
                }}
                
                .status-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }}
                
                .status-header h3 {{
                    color: #00ff00;
                    margin: 0;
                }}
                
                .status-indicator {{
                    font-size: 1.2em;
                    font-weight: bold;
                }}
                
                .status-details {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                
                .status-item {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #333;
                }}
                
                .status-item .label {{
                    color: #888;
                }}
                
                .status-item span:last-child {{
                    color: #00ff00;
                    font-weight: bold;
                }}
                
                .progress-bar {{
                    width: 100%;
                    height: 8px;
                    background: #333;
                    border-radius: 4px;
                    overflow: hidden;
                }}
                
                .progress-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #00ff00, #00cc00);
                    width: 0%;
                    transition: width 0.3s ease;
                }}
                
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Bluesky Homelessness Data Analysis</h1>
                    <p>Data Journalist Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">{stats.get('total_posts', 0):,}</div>
                        <div class="stat-label">Homelessness Posts</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{stats.get('unique_authors', 0):,}</div>
                        <div class="stat-label">Unique Authors</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{stats.get('total_likes', 0):,}</div>
                        <div class="stat-label">Total Likes</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{stats.get('total_reposts', 0):,}</div>
                        <div class="stat-label">Total Reposts</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{stats.get('avg_likes', 0):.1f}</div>
                        <div class="stat-label">Avg Likes/Post</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{stats.get('avg_reposts', 0):.1f}</div>
                        <div class="stat-label">Avg Reposts/Post</div>
                    </div>
                </div>
                
                <!-- Interactive Scraper Control Panel -->
                <div class="section">
                    <h2>🚀 Run Scraper Again</h2>
                    <div class="scraper-controls">
                        <div class="control-group">
                            <label for="duration">Duration (seconds):</label>
                            <select id="duration">
                                <option value="60">1 minute</option>
                                <option value="300" selected>5 minutes</option>
                                <option value="900">15 minutes</option>
                                <option value="1800">30 minutes</option>
                                <option value="3600">1 hour</option>
                            </select>
                        </div>
                        
                        <div class="control-group">
                            <label for="customKeywords">Keywords (comma-separated):</label>
                            <input type="text" id="customKeywords" placeholder="e.g., homeless, unhoused, housing crisis, tuna wisma" required>
                            <small class="help-text">Enter any keywords separated by commas. You can use any language or terms.</small>
                            <div id="relevanceCheck" class="relevance-check" style="display:none;"></div>
                        </div>
                        
                        <div class="button-group">
                            <button id="runScraper" class="run-button">🚀 Run Scraper</button>
                            <button id="refreshData" class="refresh-button" style="display:none;">🔄 Refresh Data</button>
                        </div>
                        
                        <div id="refreshStatus" class="refresh-status" style="display:none;">
                            <div class="status-header">
                                <h3>🔄 Data Refresh Progress</h3>
                                <div class="status-indicator" id="refreshIndicator">⏳ Starting...</div>
                            </div>
                            <div class="status-details">
                                <div class="status-item">
                                    <span class="label">Status:</span>
                                    <span id="refreshText">Initializing...</span>
                                </div>
                                <div class="status-item">
                                    <span class="label">Progress:</span>
                                    <span id="refreshProgress">0%</span>
                                </div>
                                <div class="status-item">
                                    <span class="label">Duration:</span>
                                    <span id="refreshDuration">0s</span>
                                </div>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" id="refreshProgressFill"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div id="scraperStatus" class="scraper-status" style="display:none;">
                        <div class="status-header">
                            <h3>📊 Collection Status</h3>
                            <div class="status-indicator" id="statusIndicator">⏳ Preparing...</div>
                        </div>
                        <div class="status-details">
                            <div class="status-item">
                                <span class="label">Status:</span>
                                <span id="statusText">Initializing...</span>
                            </div>
                            <div class="status-item">
                                <span class="label">Posts Collected:</span>
                                <span id="postsCollected">0</span>
                            </div>
                            <div class="status-item">
                                <span class="label">Duration:</span>
                                <span id="durationElapsed">0s</span>
                            </div>
                            <div class="status-item">
                                <span class="label">New Posts Added:</span>
                                <span id="newPostsAdded">0</span>
                            </div>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill"></div>
                        </div>
                    </div>
                </div>
                
                <!-- Keywords Searched -->
                <div class="section">
                    <h2>Keywords Searched</h2>
                    <div class="keywords-section">
                        <div class="keywords-title">Search Terms Used</div>
                        <div class="keywords-grid">
                            <div class="keywords-row1">
                                <div class="keyword-box"><a href="https://bsky.app/search?q=homelessness" target="_blank" class="keyword-link">homelessness</a></div>
                                <div class="keyword-box"><a href="https://bsky.app/search?q=homeless" target="_blank" class="keyword-link">homeless</a></div>
                                <div class="keyword-box"><a href="https://bsky.app/search?q=unhoused" target="_blank" class="keyword-link">unhoused</a></div>
                                <div class="keyword-box"><a href="https://bsky.app/search?q=housing%20crisis" target="_blank" class="keyword-link">housing crisis</a></div>
                                <div class="keyword-box"><a href="https://bsky.app/search?q=shelter" target="_blank" class="keyword-link">shelter</a></div>
                            </div>
                            <div class="keywords-row2">
                                <div class="keyword-box"><a href="https://bsky.app/search?q=street%20homeless" target="_blank" class="keyword-link">street homeless</a></div>
                                <div class="keyword-box"><a href="https://bsky.app/search?q=rough%20sleeper" target="_blank" class="keyword-link">rough sleeper</a></div>
                                <div class="keyword-box"><a href="https://bsky.app/search?q=tent%20city" target="_blank" class="keyword-link">tent city</a></div>
                                <div class="keyword-box"><a href="https://bsky.app/search?q=homeless%20services" target="_blank" class="keyword-link">homeless services</a></div>
                                <div class="keyword-box"><a href="https://bsky.app/search?q=end%20homelessness" target="_blank" class="keyword-link">end homelessness</a></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Period Data Pulled</h2>
                    <div class="chart-container">
                        {daily_trend_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Content Word Cloud</h2>
                    <div class="wordcloud-container">
                        {wordcloud_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Geolocation Cloud</h2>
                    <div class="wordcloud-container">
                        {geolocation_cloud_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>World Map - Geographic Distribution</h2>
                    <div class="chart-container">
                        {world_map_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Content Analysis</h2>
                    <div class="chart-container">
                        {content_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Detailed Content Analysis</h2>
                    <div class="feature-cards">
                        {detailed_features_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Engagement Analysis</h2>
                    <div class="chart-container">
                        {engagement_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Author Analysis</h2>
                    <div class="chart-container">
                        {author_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Top 10 Posts by Likes</h2>
                    <div class="posts-feed">
                        {top_likes_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Top 10 Posts by Most Followed Authors</h2>
                    <div class="posts-feed">
                        {top_followers_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Top 10 Posts by Reposts</h2>
                    <div class="posts-feed">
                        {top_reposts_html}
                    </div>
                </div>
                
                <div class="footer">
                    <p>Analysis completed | DFP F25 Social Media Blue Team</p>
                    <div class="data-source">
                        <em>Data collected from Bluesky social media platform focusing on homelessness-related content</em>
                    </div>
                </div>
            </div>
            
            <script>
                // Scraper Control Functionality
                let scraperRunning = false;
                let startTime = null;
                let progressInterval = null;
                
                // Relevance checking for custom keywords
                function checkKeywordRelevance(keywords) {{
                    const homelessnessTerms = [
                        'homeless', 'homelessness', 'unhoused', 'housing crisis', 'affordable housing',
                        'homeless shelter', 'street homelessness', 'housing first', 'homeless veterans',
                        'homeless families', 'homeless youth', 'chronic homelessness', 'temporary housing',
                        'transitional housing', 'supportive housing', 'homeless services', 'homeless outreach',
                        'homeless encampment', 'housing insecurity', 'homeless population', 'end homelessness',
                        'rough sleeper', 'tent city', 'no home', 'houseless', 'precarious housing',
                        'eviction', 'foreclosure', 'poverty', 'destitute', 'beggar', 'vagran', 'squatter',
                        'migrant crisis', 'refugee crisis', 'displaced people', 'asylum seeker', 'tent encampment',
                        'sleeping rough', 'food bank', 'soup kitchen', 'charity for homeless', 'homeless charity',
                        'homeless aid', 'homeless support', 'homeless advocacy', 'homeless solutions',
                        'homeless prevention', 'housing solutions', 'housing advocacy', 'housing support',
                        'housing initiatives', 'housing programs', 'housing policy', 'housing justice',
                        'housing rights', 'housing stability', 'housing affordability', 'housing equity',
                        'housing for all', 'housing needs', 'housing challenges', 'housing crisis solutions'
                    ];
                    
                    const keywordList = keywords.toLowerCase().split(',').map(k => k.trim()).filter(k => k);
                    const relevantKeywords = [];
                    const irrelevantKeywords = [];
                    
                    keywordList.forEach(keyword => {{
                        const isRelevant = homelessnessTerms.some(term => 
                            term.includes(keyword) || keyword.includes(term) ||
                            term.split(' ').some(word => word.includes(keyword)) ||
                            keyword.split(' ').some(word => word.includes(term))
                        );
                        
                        if (isRelevant) {{
                            relevantKeywords.push(keyword);
                        }} else {{
                            irrelevantKeywords.push(keyword);
                        }}
                    }});
                    
                    return {{ relevantKeywords, irrelevantKeywords, totalKeywords: keywordList.length }};
                }}
                
                // Add event listener for custom keyword checking
                document.getElementById('customKeywords').addEventListener('input', function() {{
                    const keywords = this.value;
                    const relevanceDiv = document.getElementById('relevanceCheck');
                    
                    if (keywords.trim()) {{
                        const result = checkKeywordRelevance(keywords);
                        relevanceDiv.style.display = 'block';
                        
                        if (result.relevantKeywords.length > 0) {{
                            relevanceDiv.className = 'relevance-check relevant';
                            relevanceDiv.innerHTML = `💡 <strong>Tip:</strong> ${{result.relevantKeywords.length}}/${{result.totalKeywords}} keywords are related to homelessness: ${{result.relevantKeywords.join(', ')}}`;
                        }} else {{
                            relevanceDiv.className = 'relevance-check not-relevant';
                            relevanceDiv.innerHTML = `💡 <strong>Tip:</strong> For homelessness-related data, consider adding terms like: homeless, unhoused, housing crisis, affordable housing, etc.`;
                        }}
                        
                        if (result.irrelevantKeywords.length > 0) {{
                            relevanceDiv.innerHTML += `<br/>📝 Your keywords: ${{result.irrelevantKeywords.join(', ')}}`;
                        }}
                    }} else {{
                        relevanceDiv.style.display = 'none';
                    }}
                }});
                
                document.getElementById('runScraper').addEventListener('click', async function() {{
                    if (scraperRunning) return;
                    
                    const duration = document.getElementById('duration').value;
                    const customKeywords = document.getElementById('customKeywords').value;
                    
                    // Validate input
                    if (!customKeywords.trim()) {{
                        alert('Please enter some keywords to search for.');
                        return;
                    }}
                    
                    // Show status panel
                    document.getElementById('scraperStatus').style.display = 'block';
                    document.getElementById('runScraper').disabled = true;
                    document.getElementById('runScraper').textContent = '⏳ Running...';
                    scraperRunning = true;
                    startTime = Date.now();
                    
                    // Update status
                    document.getElementById('statusIndicator').textContent = '🚀 Starting...';
                    document.getElementById('statusText').textContent = 'Initializing scraper...';
                    document.getElementById('postsCollected').textContent = '0';
                    document.getElementById('durationElapsed').textContent = '0s';
                    document.getElementById('newPostsAdded').textContent = '0';
                    document.getElementById('progressFill').style.width = '0%';
                    
                    // Start progress tracking
                    progressInterval = setInterval(updateProgress, 1000);
                    
                    try {{
                        // Call the scraper API
                        const response = await fetch('/api/run-scraper', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                duration: parseInt(duration),
                                keywords: customKeywords.trim()
                            }})
                        }});
                        
                        if (!response.ok) {{
                            throw new Error('Scraper failed to start');
                        }}
                        
                        // Start polling for status updates
                        const statusInterval = setInterval(async () => {{
                            try {{
                                const statusResponse = await fetch('/api/scraper-status');
                                const status = await statusResponse.json();
                                
                                if (status.running) {{
                                    document.getElementById('statusIndicator').textContent = '🚀 Running...';
                                    document.getElementById('statusText').textContent = 'Collecting data...';
                                    document.getElementById('postsCollected').textContent = status.posts_collected || '0';
                                    document.getElementById('newPostsAdded').textContent = status.new_posts || '0';
                                }} else {{
                                    clearInterval(statusInterval);
                                    
                                    if (status.error) {{
                                        document.getElementById('statusIndicator').textContent = '❌ Error';
                                        document.getElementById('statusText').textContent = 'Collection failed: ' + status.error;
                                    }} else {{
                                        document.getElementById('statusIndicator').textContent = '✅ Complete';
                                        document.getElementById('statusText').textContent = 'Collection completed successfully';
                                        document.getElementById('postsCollected').textContent = status.posts_collected || '0';
                                        document.getElementById('newPostsAdded').textContent = status.new_posts || '0';
                                        document.getElementById('progressFill').style.width = '100%';
                                        
                                        // Show refresh button
                                        document.getElementById('refreshData').style.display = 'inline-block';
                                    }}
                                    
                                    // Reset button
                                    document.getElementById('runScraper').disabled = false;
                                    document.getElementById('runScraper').textContent = '🚀 Run Scraper';
                                    scraperRunning = false;
                                    clearInterval(progressInterval);
                                }}
                            }} catch (error) {{
                                console.error('Status check error:', error);
                                clearInterval(statusInterval);
                            }}
                        }}, 2000); // Check every 2 seconds
                        
                    }} catch (error) {{
                        console.error('Scraper error:', error);
                        document.getElementById('statusIndicator').textContent = '❌ Error';
                        document.getElementById('statusText').textContent = 'Collection failed: ' + error.message;
                        
                        // Reset button
                        document.getElementById('runScraper').disabled = false;
                        document.getElementById('runScraper').textContent = '🚀 Run Scraper';
                        scraperRunning = false;
                        clearInterval(progressInterval);
                    }}
                }});
                
                document.getElementById('refreshData').addEventListener('click', async function() {{
                    // Show refresh status panel
                    document.getElementById('refreshStatus').style.display = 'block';
                    document.getElementById('refreshData').disabled = true;
                    document.getElementById('refreshData').textContent = '⏳ Refreshing...';
                    
                    // Update status
                    document.getElementById('refreshIndicator').textContent = '⏳ Starting...';
                    document.getElementById('refreshText').textContent = 'Initializing refresh...';
                    document.getElementById('refreshProgress').textContent = '0%';
                    document.getElementById('refreshDuration').textContent = '0s';
                    document.getElementById('refreshProgressFill').style.width = '0%';
                    
                    const startTime = Date.now();
                    
                    // Start progress tracking
                    const progressInterval = setInterval(() => {{
                        const elapsed = Math.floor((Date.now() - startTime) / 1000);
                        document.getElementById('refreshDuration').textContent = elapsed + 's';
                    }}, 1000);
                    
                    try {{
                        const response = await fetch('/api/refresh-data', {{ method: 'POST' }});
                        if (response.ok) {{
                            // Start polling for refresh status
                            const statusInterval = setInterval(async () => {{
                                try {{
                                    const statusResponse = await fetch('/api/refresh-status');
                                    const status = await statusResponse.json();
                                    
                                    if (status.running) {{
                                        document.getElementById('refreshIndicator').textContent = '🔄 Refreshing...';
                                        document.getElementById('refreshText').textContent = status.current_step || 'Processing...';
                                        document.getElementById('refreshProgress').textContent = status.progress + '%';
                                        document.getElementById('refreshProgressFill').style.width = status.progress + '%';
                                    }} else {{
                                        clearInterval(statusInterval);
                                        clearInterval(progressInterval);
                                        
                                        if (status.error) {{
                                            document.getElementById('refreshIndicator').textContent = '❌ Error';
                                            document.getElementById('refreshText').textContent = 'Refresh failed: ' + status.error;
                                        }} else {{
                                            document.getElementById('refreshIndicator').textContent = '✅ Complete';
                                            document.getElementById('refreshText').textContent = 'Refresh completed successfully!';
                                            document.getElementById('refreshProgress').textContent = '100%';
                                            document.getElementById('refreshProgressFill').style.width = '100%';
                                            
                                            // Reload the page to show updated data after a short delay
                                            setTimeout(() => {{
                                                window.location.reload();
                                            }}, 2000);
                                        }}
                                        
                                        // Reset button
                                        document.getElementById('refreshData').disabled = false;
                                        document.getElementById('refreshData').textContent = '🔄 Refresh Data';
                                    }}
                                }} catch (error) {{
                                    console.error('Status check error:', error);
                                    clearInterval(statusInterval);
                                    clearInterval(progressInterval);
                                }}
                            }}, 1000); // Check every second
                        }} else {{
                            clearInterval(progressInterval);
                            console.error('Failed to start refresh');
                            document.getElementById('refreshIndicator').textContent = '❌ Error';
                            document.getElementById('refreshText').textContent = 'Failed to start refresh';
                            
                            // Reset button
                            document.getElementById('refreshData').disabled = false;
                            document.getElementById('refreshData').textContent = '🔄 Refresh Data';
                        }}
                    }} catch (error) {{
                        clearInterval(progressInterval);
                        console.error('Refresh error:', error);
                        document.getElementById('refreshIndicator').textContent = '❌ Error';
                        document.getElementById('refreshText').textContent = 'Refresh failed: ' + error.message;
                        
                        // Reset button
                        document.getElementById('refreshData').disabled = false;
                        document.getElementById('refreshData').textContent = '🔄 Refresh Data';
                    }}
                }});
                
                function updateProgress() {{
                    if (!startTime) return;
                    
                    const elapsed = Math.floor((Date.now() - startTime) / 1000);
                    const duration = parseInt(document.getElementById('duration').value);
                    const progress = Math.min((elapsed / duration) * 100, 100);
                    
                    document.getElementById('durationElapsed').textContent = elapsed + 's';
                    document.getElementById('progressFill').style.width = progress + '%';
                    
                    // Simulate posts collected (in real implementation, this would come from the API)
                    const estimatedPosts = Math.floor(elapsed * 2); // Rough estimate
                    document.getElementById('postsCollected').textContent = estimatedPosts;
                    
                    if (elapsed >= duration) {{
                        clearInterval(progressInterval);
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        # Save HTML report
        with open('interactive_eda_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Interactive analysis report generated: interactive_eda_report.html")
        return html_content

def main():
    """Main execution function"""
    print("Starting homelessness data analysis...")
    
    # Initialize analyzer
    analyzer = ImprovedEDAAnalyzer()
    
    if analyzer.df.empty:
        print("No data found. Please check the data path.")
        return
    
    # Generate report
    analyzer.generate_html_report()
    
    print("Analysis complete. Open 'improved_eda_report.html' in your browser.")

if __name__ == "__main__":
    main()
