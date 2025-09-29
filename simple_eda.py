#!/usr/bin/env python3
"""
Simple FAANG-Level EDA Analysis for Bluesky Social Justice Data
DFP F25 Social Media Blue Team

Professional data analysis with comprehensive visualizations
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

class SimpleEDAAnalyzer:
    """Simple EDA analyzer for Bluesky social justice data"""
    
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
            
            # Use existing columns
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
        
        stats = {
            'total_posts': len(self.df),
            'unique_authors': self.df['author_handle'].nunique() if 'author_handle' in self.df.columns else 0,
            'avg_text_length': float(self.df['text_length'].mean()) if 'text_length' in self.df.columns else 0,
            'avg_word_count': float(self.df['word_count'].mean()) if 'word_count' in self.df.columns else 0,
            'posts_with_hashtags': int(self.df['hashtag_count'].sum()) if 'hashtag_count' in self.df.columns else 0,
            'posts_with_mentions': int(self.df['mention_count'].sum()) if 'mention_count' in self.df.columns else 0,
            'posts_with_urls': int(self.df['url_count'].sum()) if 'url_count' in self.df.columns else 0,
            'posts_with_images': int(self.df['has_images'].sum()) if 'has_images' in self.df.columns else 0,
            'avg_likes': float(self.df['like_count'].mean()) if 'like_count' in self.df.columns else 0,
            'avg_reposts': float(self.df['repost_count'].mean()) if 'repost_count' in self.df.columns else 0
        }
        
        return stats
    
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
        
        # 3. Engagement metrics
        if 'like_count' in self.df.columns and 'repost_count' in self.df.columns:
            # Scatter plot of likes vs reposts
            axes[1, 0].scatter(self.df['like_count'], self.df['repost_count'], 
                              alpha=0.6, color='#F18F01', s=20)
            axes[1, 0].set_title('Likes vs Reposts', fontweight='bold')
            axes[1, 0].set_xlabel('Like Count')
            axes[1, 0].set_ylabel('Repost Count')
            axes[1, 0].grid(True, alpha=0.3)
        
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
            axes[1, 1].bar(features, counts, color='#C73E1D', alpha=0.7)
            axes[1, 1].set_title('Content Features Distribution', fontweight='bold')
            axes[1, 1].set_xlabel('Feature Type')
            axes[1, 1].set_ylabel('Total Count')
            axes[1, 1].tick_params(axis='x', rotation=45)
            axes[1, 1].grid(True, alpha=0.3)
        
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
        
        # 3. Author influence analysis
        if 'author_followers_count' in self.df.columns and 'author_posts_count' in self.df.columns:
            # Scatter plot of followers vs posts
            axes[1, 0].scatter(self.df['author_posts_count'], self.df['author_followers_count'], 
                              alpha=0.6, color='#F18F01', s=20)
            axes[1, 0].set_title('Author Followers vs Total Posts', fontweight='bold')
            axes[1, 0].set_xlabel('Total Posts by Author')
            axes[1, 0].set_ylabel('Follower Count')
            axes[1, 0].set_yscale('log')
            axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Author verification status
        if 'author_verified' in self.df.columns:
            verified_counts = self.df['author_verified'].value_counts()
            labels = ['Verified' if x else 'Not Verified' for x in verified_counts.index]
            colors = ['#2E86AB' if x else '#C73E1D' for x in verified_counts.index]
            axes[1, 1].pie(verified_counts.values, labels=labels, 
                          autopct='%1.1f%%', colors=colors, startangle=90)
            axes[1, 1].set_title('Author Verification Status', fontweight='bold')
        
        plt.tight_layout()
        return self._fig_to_html(fig)
    
    def create_engagement_analysis(self):
        """Create engagement analysis visualizations"""
        if self.df.empty:
            return ""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('📊 Engagement Analysis of Social Justice Posts', fontsize=16, fontweight='bold')
        
        # 1. Like count distribution
        if 'like_count' in self.df.columns:
            axes[0, 0].hist(self.df['like_count'], bins=50, color='#2E86AB', alpha=0.7, edgecolor='black')
            axes[0, 0].set_title('Distribution of Like Counts', fontweight='bold')
            axes[0, 0].set_xlabel('Like Count')
            axes[0, 0].set_ylabel('Frequency')
            axes[0, 0].set_yscale('log')
            axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Repost count distribution
        if 'repost_count' in self.df.columns:
            axes[0, 1].hist(self.df['repost_count'], bins=50, color='#A23B72', alpha=0.7, edgecolor='black')
            axes[0, 1].set_title('Distribution of Repost Counts', fontweight='bold')
            axes[0, 1].set_xlabel('Repost Count')
            axes[0, 1].set_ylabel('Frequency')
            axes[0, 1].set_yscale('log')
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Engagement correlation
        if 'like_count' in self.df.columns and 'repost_count' in self.df.columns:
            # Calculate correlation
            correlation = self.df['like_count'].corr(self.df['repost_count'])
            axes[1, 0].scatter(self.df['like_count'], self.df['repost_count'], 
                              alpha=0.6, color='#F18F01', s=20)
            axes[1, 0].set_title(f'Likes vs Reposts (r={correlation:.2f})', fontweight='bold')
            axes[1, 0].set_xlabel('Like Count')
            axes[1, 0].set_ylabel('Repost Count')
            axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Top performing posts
        if 'like_count' in self.df.columns:
            top_posts = self.df.nlargest(10, 'like_count')
            axes[1, 1].barh(range(len(top_posts)), top_posts['like_count'], color='#C73E1D', alpha=0.7)
            axes[1, 1].set_yticks(range(len(top_posts)))
            axes[1, 1].set_yticklabels([f"Post {i+1}" for i in range(len(top_posts))])
            axes[1, 1].set_title('Top 10 Posts by Likes', fontweight='bold')
            axes[1, 1].set_xlabel('Like Count')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._fig_to_html(fig)
    
    def create_wordcloud(self):
        """Create word cloud"""
        if self.df.empty or 'text' not in self.df.columns:
            return ""
        
        all_text = ' '.join(self.df['text'].dropna().astype(str))
        if not all_text:
            return ""
        
        wordcloud = WordCloud(width=800, height=400, background_color='white', 
                            colormap='viridis', max_words=100,
                            stopwords={'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}).generate(all_text)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Content Word Cloud', fontsize=16, fontweight='bold', pad=20)
        
        return self._fig_to_html(fig)
    
    def create_hashtag_analysis(self):
        """Create hashtag analysis"""
        if self.df.empty or 'hashtags' not in self.df.columns:
            return ""
        
        # Extract hashtags
        all_hashtags = []
        for hashtags in self.df['hashtags'].dropna():
            if isinstance(hashtags, str):
                try:
                    import ast
                    hashtag_list = ast.literal_eval(hashtags)
                    all_hashtags.extend(hashtag_list)
                except:
                    all_hashtags.extend(hashtags.split(','))
            elif isinstance(hashtags, list):
                all_hashtags.extend(hashtags)
        
        if not all_hashtags:
            return ""
        
        hashtag_counts = Counter(all_hashtags)
        top_hashtags = dict(hashtag_counts.most_common(20))
        
        fig, ax = plt.subplots(figsize=(12, 8))
        hashtags = list(top_hashtags.keys())
        counts = list(top_hashtags.values())
        
        bars = ax.barh(range(len(hashtags)), counts, color='#2E86AB', alpha=0.7)
        ax.set_yticks(range(len(hashtags)))
        ax.set_yticklabels(hashtags)
        ax.set_title('Top 20 Hashtags', fontsize=16, fontweight='bold')
        ax.set_xlabel('Frequency')
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'{counts[i]}', ha='left', va='center')
        
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
        content_html = self.create_content_analysis()
        author_html = self.create_author_analysis()
        engagement_html = self.create_engagement_analysis()
        wordcloud_html = self.create_wordcloud()
        hashtag_html = self.create_hashtag_analysis()
        
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
                        <div class="stat-number">{stats.get('posts_with_hashtags', 0):,}</div>
                        <div class="stat-label">Posts with Hashtags</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('posts_with_mentions', 0):,}</div>
                        <div class="stat-label">Posts with Mentions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('avg_text_length', 0):.0f}</div>
                        <div class="stat-label">Avg Text Length</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('avg_likes', 0):.1f}</div>
                        <div class="stat-label">Avg Likes per Post</div>
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
                    <h2>📊 Engagement Analysis</h2>
                    <div class="chart-container">
                        {engagement_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>☁️ Content Word Cloud</h2>
                    <div class="chart-container">
                        {wordcloud_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>#️⃣ Hashtag Analysis</h2>
                    <div class="chart-container">
                        {hashtag_html}
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
        with open('simple_eda_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ HTML report generated: simple_eda_report.html")
        return html_content

def main():
    """Main execution function"""
    print("🚀 Starting FAANG-Level EDA Analysis...")
    
    # Initialize analyzer
    analyzer = SimpleEDAAnalyzer()
    
    if analyzer.df.empty:
        print("❌ No data found. Please check the data path.")
        return
    
    # Generate comprehensive report
    analyzer.generate_html_report()
    
    print("🎉 Analysis complete! Open 'simple_eda_report.html' in your browser.")

if __name__ == "__main__":
    main()
