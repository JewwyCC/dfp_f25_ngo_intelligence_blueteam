#!/usr/bin/env python3
"""
Minimalist EDA Analysis for Bluesky Social Justice Data
Data Journalist Style Analysis

Clean, professional data analysis with minimalist design
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

class MinimalistEDAAnalyzer:
    """Minimalist EDA analyzer for Bluesky social justice data"""
    
    def __init__(self, data_path="data/alltime_socmed/merged_alltime_20250928_221708.csv"):
        self.data_path = data_path
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load and preprocess data"""
        print("Loading data...")
        try:
            self.df = pd.read_csv(self.data_path)
            print(f"Loaded {len(self.df):,} posts")
            
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
        """Create content analysis with Plotly"""
        if self.df.empty:
            return ""
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Text Length Distribution', 'Word Count Distribution', 
                          'Text Length vs Word Count', 'Content Features'),
            specs=[[{"type": "histogram"}, {"type": "histogram"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # 1. Text length histogram with auto bins
        if 'text_length' in self.df.columns:
            fig.add_trace(
                go.Histogram(x=self.df['text_length'], nbinsx=0, name='Text Length',
                           marker_color='#1f77b4', opacity=0.7),
                row=1, col=1
            )
        
        # 2. Word count histogram with auto bins
        if 'word_count' in self.df.columns:
            fig.add_trace(
                go.Histogram(x=self.df['word_count'], nbinsx=0, name='Word Count',
                           marker_color='#ff7f0e', opacity=0.7),
                row=1, col=2
            )
        
        # 3. Text length vs word count scatter
        if 'text_length' in self.df.columns and 'word_count' in self.df.columns:
            fig.add_trace(
                go.Scatter(x=self.df['text_length'], y=self.df['word_count'],
                          mode='markers', name='Length vs Words',
                          marker=dict(color='#2ca02c', size=4, opacity=0.6)),
                row=2, col=1
            )
        
        # 4. Content features
        features = []
        counts = []
        if 'hashtag_count' in self.df.columns:
            features.append('Hashtags')
            counts.append(int(self.df['hashtag_count'].sum()))
        if 'mention_count' in self.df.columns:
            features.append('Mentions')
            counts.append(int(self.df['mention_count'].sum()))
        if 'url_count' in self.df.columns:
            features.append('URLs')
            counts.append(int(self.df['url_count'].sum()))
        if 'has_images' in self.df.columns:
            features.append('Images')
            counts.append(int(self.df['has_images'].sum()))
        
        if features:
            fig.add_trace(
                go.Bar(x=features, y=counts, name='Features',
                      marker_color='#d62728', opacity=0.7),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title="Content Analysis",
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=600
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def create_author_analysis(self):
        """Create author analysis with followers vs engagement scatter"""
        if self.df.empty or 'author_handle' not in self.df.columns:
            return ""
        
        # Calculate engagement (likes + reposts)
        if 'like_count' in self.df.columns and 'repost_count' in self.df.columns:
            self.df['total_engagement'] = self.df['like_count'] + self.df['repost_count']
        else:
            return ""
        
        # Create scatter plot
        fig = go.Figure()
        
        if 'author_followers_count' in self.df.columns:
            fig.add_trace(go.Scatter(
                x=self.df['author_followers_count'],
                y=self.df['total_engagement'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=self.df['total_engagement'],
                    colorscale='Viridis',
                    opacity=0.6,
                    showscale=True,
                    colorbar=dict(title="Total Engagement")
                ),
                text=self.df['author_handle'],
                hovertemplate='<b>@%{text}</b><br>' +
                            'Followers: %{x:,}<br>' +
                            'Engagement: %{y}<br>' +
                            '<extra></extra>'
            ))
        
        fig.update_layout(
            title="Author Followers vs Engagement",
            xaxis_title="Follower Count",
            yaxis_title="Total Engagement (Likes + Reposts)",
            xaxis_type="log",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def create_engagement_analysis(self):
        """Create engagement analysis"""
        if self.df.empty:
            return ""
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Like Distribution', 'Repost Distribution', 
                          'Likes vs Reposts', 'Engagement Correlation'),
            specs=[[{"type": "histogram"}, {"type": "histogram"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # 1. Like distribution
        if 'like_count' in self.df.columns:
            fig.add_trace(
                go.Histogram(x=self.df['like_count'], nbinsx=0, name='Likes',
                           marker_color='#1f77b4', opacity=0.7),
                row=1, col=1
            )
        
        # 2. Repost distribution
        if 'repost_count' in self.df.columns:
            fig.add_trace(
                go.Histogram(x=self.df['repost_count'], nbinsx=0, name='Reposts',
                           marker_color='#ff7f0e', opacity=0.7),
                row=1, col=2
            )
        
        # 3. Likes vs reposts scatter
        if 'like_count' in self.df.columns and 'repost_count' in self.df.columns:
            correlation = self.df['like_count'].corr(self.df['repost_count'])
            fig.add_trace(
                go.Scatter(x=self.df['like_count'], y=self.df['repost_count'],
                          mode='markers', name='Likes vs Reposts',
                          marker=dict(color='#2ca02c', size=4, opacity=0.6)),
                row=2, col=1
            )
            fig.add_annotation(
                x=0.5, y=0.5, xref="x2 domain", yref="y2 domain",
                text=f"Correlation: {correlation:.2f}",
                showarrow=False, font=dict(color='white', size=12),
                row=2, col=1
            )
        
        # 4. Top engagement metrics
        if 'like_count' in self.df.columns and 'repost_count' in self.df.columns:
            self.df['total_engagement'] = self.df['like_count'] + self.df['repost_count']
            top_engagement = self.df.nlargest(10, 'total_engagement')
            
            fig.add_trace(
                go.Bar(x=[f"Post {i+1}" for i in range(len(top_engagement))], 
                      y=top_engagement['total_engagement'],
                      name='Top Engagement',
                      marker_color='#d62728', opacity=0.7),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Engagement Analysis",
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=600
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def create_wordcloud(self):
        """Create word cloud with better filtering"""
        if self.df.empty or 'text' not in self.df.columns:
            return ""
        
        all_text = ' '.join(self.df['text'].dropna().astype(str))
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
            'everywhere', 'nowhere', 'somewhere', 'anywhere', 'everywhere', 'nowhere'
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
        ax.set_title('Content Word Cloud', fontsize=16, fontweight='bold', color='white', pad=20)
        
        return self._fig_to_html(fig)
    
    def create_top_posts_feed(self):
        """Create top 10 posts feed like Twitter"""
        if self.df.empty or 'like_count' not in self.df.columns:
            return ""
        
        # Get top 10 posts by likes
        top_posts = self.df.nlargest(10, 'like_count')
        
        html_posts = []
        for i, (_, post) in enumerate(top_posts.iterrows(), 1):
            author = post.get('author_handle', 'Unknown')
            text = post.get('text', 'No text available')
            likes = post.get('like_count', 0)
            reposts = post.get('repost_count', 0)
            created_at = post.get('created_at', 'Unknown date')
            
            # Truncate text if too long
            if len(text) > 280:
                text = text[:280] + "..."
            
            post_html = f"""
            <div class="post-item">
                <div class="post-header">
                    <span class="post-number">#{i}</span>
                    <span class="post-author">@{author}</span>
                    <span class="post-date">{created_at}</span>
                </div>
                <div class="post-content">
                    {text}
                </div>
                <div class="post-stats">
                    <span class="likes">❤️ {likes}</span>
                    <span class="reposts">🔄 {reposts}</span>
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
        """Generate minimalist HTML report"""
        print("Generating analysis report...")
        
        # Get overview stats
        stats = self.generate_overview_stats()
        
        # Generate all visualizations
        content_html = self.create_content_analysis()
        author_html = self.create_author_analysis()
        engagement_html = self.create_engagement_analysis()
        wordcloud_html = self.create_wordcloud()
        top_posts_html = self.create_top_posts_feed()
        
        # Create HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bluesky Social Justice Data Analysis</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
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
                    border-bottom: 2px solid #333;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                
                .header h1 {{
                    color: #00ff00;
                    font-size: 2em;
                    margin-bottom: 10px;
                }}
                
                .header p {{
                    color: #888;
                    font-size: 1.1em;
                }}
                
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
                    font-size: 2em;
                    font-weight: bold;
                }}
                
                .stat-label {{
                    color: #888;
                    margin-top: 5px;
                }}
                
                .section {{
                    margin-bottom: 40px;
                    background: #111;
                    border: 1px solid #333;
                    padding: 30px;
                }}
                
                .section h2 {{
                    color: #00ff00;
                    font-size: 1.5em;
                    margin-bottom: 20px;
                    border-bottom: 1px solid #333;
                    padding-bottom: 10px;
                }}
                
                .chart-container {{
                    margin: 20px 0;
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
                }}
                
                .post-content {{
                    margin: 15px 0;
                    font-size: 1.1em;
                    line-height: 1.5;
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
                
                .footer {{
                    text-align: center;
                    color: #666;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #333;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Bluesky Social Justice Data Analysis</h1>
                    <p>Data Journalist Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">{stats.get('total_posts', 0):,}</div>
                        <div class="stat-label">Total Posts</div>
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
                
                <div class="section">
                    <h2>Content Analysis</h2>
                    <div class="chart-container">
                        {content_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Author Analysis</h2>
                    <div class="chart-container">
                        {author_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Engagement Analysis</h2>
                    <div class="chart-container">
                        {engagement_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Content Word Cloud</h2>
                    <div class="chart-container">
                        {wordcloud_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Top 10 Posts by Likes</h2>
                    <div class="posts-feed">
                        {top_posts_html}
                    </div>
                </div>
                
                <div class="footer">
                    <p>Analysis completed | DFP F25 Social Media Blue Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save HTML report
        with open('minimalist_eda_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Analysis report generated: minimalist_eda_report.html")
        return html_content

def main():
    """Main execution function"""
    print("Starting data analysis...")
    
    # Initialize analyzer
    analyzer = MinimalistEDAAnalyzer()
    
    if analyzer.df.empty:
        print("No data found. Please check the data path.")
        return
    
    # Generate report
    analyzer.generate_html_report()
    
    print("Analysis complete. Open 'minimalist_eda_report.html' in your browser.")

if __name__ == "__main__":
    main()
