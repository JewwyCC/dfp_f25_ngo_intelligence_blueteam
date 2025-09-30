import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from wordcloud import WordCloud
from matplotlib.colors import LinearSegmentedColormap
from collections import defaultdict, Counter
from datetime import datetime, timedelta


def _time_bin(df: pd.DataFrame) -> pd.Series:
    return df['created_utc'].dt.floor('D')


def _fit_linear_trend(x_ord: np.ndarray, y: np.ndarray):
    if len(x_ord) < 2:
        return None, None
    z = np.polyfit(x_ord, y, 1)
    p = np.poly1d(z)
    return z, p


def _fit_curve_trend(x_ord: np.ndarray, y: np.ndarray, degree: int = 2):
    """Fit a polynomial curve to the data."""
    if len(x_ord) < degree + 1:
        return None, None
    try:
        z = np.polyfit(x_ord, y, degree)
        p = np.poly1d(z)
        return z, p
    except:
        return None, None


def _classify_post_topic(text: str) -> str:
    """Classify posts into specific homelessness topics."""
    text_lower = text.lower()
    
    # Topic keywords
    topics = {
        'eviction': ['eviction', 'evicted', 'evict', 'evicting', 'notice', 'termination', 'lease', 'landlord'],
        'affordable_housing': ['affordable', 'housing', 'rent', 'rental', 'cost', 'price', 'expensive', 'cheap'],
        'homeless_services': ['shelter', 'homeless', 'homelessness', 'services', 'support', 'assistance', 'help'],
        'tenant_rights': ['rights', 'legal', 'law', 'protection', 'harassment', 'discrimination', 'violation'],
        'housing_policy': ['policy', 'government', 'funding', 'subsidy', 'voucher', 'program', 'initiative']
    }
    
    # Count matches for each topic
    topic_scores = {}
    for topic, keywords in topics.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        topic_scores[topic] = score
    
    # Return the topic with highest score, or 'general' if no matches
    if max(topic_scores.values()) > 0:
        return max(topic_scores, key=topic_scores.get)
    else:
        return 'general'


def _remove_outliers_iqr(data, column):
    """Remove outliers using IQR method."""
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]


def _remove_outliers_zscore(data, column, threshold=3):
    """Remove outliers using Z-score method."""
    z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
    return data[z_scores < threshold]


def _sentiment_colormap():
    # Heatmap-style red spectrum: lightest to darkest representing sentiment intensity
    colors = ['#FFF5F5', '#FFE5E5', '#FFD5D5', '#FFC5C5', '#FFB5B5', '#FFA5A5', '#FF9595', '#FF8585', '#FF7575', '#FF6565', '#FF5555', '#FF4545', '#FF3535', '#FF2525', '#FF1515', '#FF0505', '#F50000', '#E50000', '#D50000', '#C50000', '#B50000', '#A50000', '#950000', '#850000', '#750000', '#650000', '#550000', '#450000', '#350000', '#250000', '#150000', '#050000']
    return LinearSegmentedColormap.from_list('sentiment_heatmap', colors, N=256)


def build_dashboard(fig, df: pd.DataFrame, keyword_sentiments: dict = None, time_filter: str = 'month'):
    """
    Four visualizations with more space:
    1) Housing Crisis Engagement Trends (with outliers) - dual-axis post count and engagement density
    2) Engagement (upvotes + comments) over time by topic classification with curve fitting
    3) Word cloud of most frequent keywords with sentiment-based red coloration
    4) Featured posts section showing top 3 highest engagement posts
    """
    fig.clear()
    # Create a larger figure with more space for each visualization
    fig.set_size_inches(16, 20)  # Increased height for better spacing
    gs = fig.add_gridspec(4, 1, hspace=0.4, wspace=0.3, height_ratios=[2, 2, 1.5, 1.5])

    # Import the new analysis functions
    from .analysis import get_top_topic_keywords_by_frequency, aggregate_topic_keyword_sentiments
    
    # Get top keywords with their sentiment data
    top_keywords = get_top_topic_keywords_by_frequency(df, topic='housing_crisis', top_n=30)
    
    # 1) Housing Crisis Engagement Trends WITH outliers
    ax1 = fig.add_subplot(gs[0, 0])
    
    if df.empty:
        ax1.text(0.5, 0.5, 'No data for engagement analysis', ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Housing Crisis Engagement Trends (With Outliers)', fontsize=12, fontweight='bold')
        ax1.axis('off')
        
        # Show empty engagement plot
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.text(0.5, 0.5, 'No data for engagement analysis', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Engagement Over Time by Topic', fontsize=12, fontweight='bold')
        ax2.axis('off')
        
        # Show empty word cloud
        ax3 = fig.add_subplot(gs[2, 0])
        ax3.text(0.5, 0.5, 'No keywords found for word cloud', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Housing Crisis Keywords Word Cloud', fontsize=12, fontweight='bold')
        ax3.axis('off')
        
        # Show empty featured posts
        ax4 = fig.add_subplot(gs[3, 0])
        ax4.text(0.5, 0.5, 'No posts available for featured section', ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Featured Posts - Highest Engagement', fontsize=12, fontweight='bold')
        ax4.axis('off')
        return
    else:
        # Create time bins
        df_sorted = df.sort_values('created_utc')
        df_sorted['time_bin'] = _time_bin(df_sorted)
        
        # Calculate engagement (upvotes + comments) - KEEP ALL OUTLIERS
        df_sorted['engagement'] = df_sorted['score'] + df_sorted['num_comments']
        
        # Calculate overall trends WITH outliers
        time_bins = sorted(df_sorted['time_bin'].unique())
        post_counts = []
        avg_engagements = []
        engagement_densities = []
        
        for tb in time_bins:
            tb_data = df_sorted[df_sorted['time_bin'] == tb]
            post_counts.append(len(tb_data))
            avg_engagements.append(tb_data['engagement'].mean() if len(tb_data) > 0 else 0)
            engagement_densities.append(tb_data['engagement'].sum())  # Total engagement density
        
        # Plot overall post count trend
        ax1_twin = ax1.twinx()
        
        # Post count line (density)
        ax1.plot(time_bins, post_counts, 'o-', color='#2E8B57', linewidth=3, markersize=8, 
                 alpha=0.8, label='Post Count Trend', markeredgecolor='black', markeredgewidth=1)
        
        # Engagement density line
        ax1_twin.plot(time_bins, engagement_densities, 's-', color='#FF6347', linewidth=3, markersize=8,
                      alpha=0.8, label='Total Engagement Density', markeredgecolor='black', markeredgewidth=1)
        
        # Add individual data points for visibility
        for i, (tb, count, engagement) in enumerate(zip(time_bins, post_counts, engagement_densities)):
            # Color intensity based on engagement density
            intensity = min(1.0, engagement / max(engagement_densities) if max(engagement_densities) > 0 else 0)
            color = plt.cm.Reds(intensity)
            
            # Plot individual points
            ax1.scatter(tb, count, c=[color], s=100, alpha=0.7, edgecolors='black', linewidth=1)
            ax1_twin.scatter(tb, engagement, c=[color], s=100, alpha=0.7, edgecolors='black', linewidth=1)
        
        # Fit overall trend curves
        if len(time_bins) > 2:
            x_ord = np.array([tb.toordinal() for tb in time_bins])
            
            # Post count trend
            y_posts = np.array(post_counts)
            z_posts, p_posts = _fit_curve_trend(x_ord, y_posts, degree=2)
            if p_posts is not None:
                x_line = np.linspace(x_ord.min(), x_ord.max(), 100)
                y_line = p_posts(x_line)
                x_dates = [pd.Timestamp.fromordinal(int(x)) for x in x_line]
                ax1.plot(x_dates, y_line, color='#2E8B57', linewidth=4, alpha=0.9, linestyle='--')
            
            # Engagement density trend
            y_engagement = np.array(engagement_densities)
            z_engagement, p_engagement = _fit_curve_trend(x_ord, y_engagement, degree=2)
            if p_engagement is not None:
                x_line = np.linspace(x_ord.min(), x_ord.max(), 100)
                y_line = p_engagement(x_line)
                x_dates = [pd.Timestamp.fromordinal(int(x)) for x in x_line]
                ax1_twin.plot(x_dates, y_line, color='#FF6347', linewidth=4, alpha=0.9, linestyle='--')
        
        ax1.set_title('Housing Crisis Engagement Trends (With Outliers)', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Post Count', color='#2E8B57')
        ax1_twin.set_ylabel('Total Engagement Density', color='#FF6347')
        ax1.grid(True, alpha=0.3)
        
        # Add legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)

    # 2) Engagement over time with EDA and overall trend
    ax2 = fig.add_subplot(gs[1, 0])
    
    # Classify posts by topic
    df_sorted = df.sort_values('created_utc')
    df_sorted['time_bin'] = _time_bin(df_sorted)
    df_sorted['topic'] = df_sorted.apply(lambda row: _classify_post_topic(f"{row.get('title', '')} {row.get('selftext', '')}"), axis=1)
    
    # Calculate engagement (upvotes + comments)
    df_sorted['engagement'] = df_sorted['score'] + df_sorted['num_comments']
    
    # EDA: Remove outliers from engagement data
    df_clean = _remove_outliers_iqr(df_sorted, 'engagement')
    if len(df_clean) < len(df_sorted) * 0.5:  # If too many outliers removed, use z-score method
        df_clean = _remove_outliers_zscore(df_sorted, 'engagement', threshold=2.5)
    
    # Calculate overall trends
    time_bins = sorted(df_clean['time_bin'].unique())
    post_counts = []
    avg_engagements = []
    engagement_densities = []
    
    for tb in time_bins:
        tb_data = df_clean[df_clean['time_bin'] == tb]
        post_counts.append(len(tb_data))
        avg_engagements.append(tb_data['engagement'].mean() if len(tb_data) > 0 else 0)
        engagement_densities.append(tb_data['engagement'].sum())  # Total engagement density
    
    # Plot overall post count trend
    ax2_twin = ax2.twinx()
    
    # Post count line (density)
    ax2.plot(time_bins, post_counts, 'o-', color='#2E8B57', linewidth=3, markersize=8, 
             alpha=0.8, label='Post Count Trend', markeredgecolor='black', markeredgewidth=1)
    
    # Engagement density line
    ax2_twin.plot(time_bins, engagement_densities, 's-', color='#FF6347', linewidth=3, markersize=8,
                  alpha=0.8, label='Total Engagement Density', markeredgecolor='black', markeredgewidth=1)
    
    # Add individual data points for visibility
    for i, (tb, count, engagement) in enumerate(zip(time_bins, post_counts, engagement_densities)):
        # Color intensity based on engagement density
        intensity = min(1.0, engagement / max(engagement_densities) if max(engagement_densities) > 0 else 0)
        color = plt.cm.Reds(intensity)
        
        # Plot individual points
        ax2.scatter(tb, count, c=[color], s=100, alpha=0.7, edgecolors='black', linewidth=1)
        ax2_twin.scatter(tb, engagement, c=[color], s=100, alpha=0.7, edgecolors='black', linewidth=1)
    
    # Fit overall trend curves
    if len(time_bins) > 2:
        x_ord = np.array([tb.toordinal() for tb in time_bins])
        
        # Post count trend
        y_posts = np.array(post_counts)
        z_posts, p_posts = _fit_curve_trend(x_ord, y_posts, degree=2)
        if p_posts is not None:
            x_line = np.linspace(x_ord.min(), x_ord.max(), 100)
            y_line = p_posts(x_line)
            x_dates = [pd.Timestamp.fromordinal(int(x)) for x in x_line]
            ax2.plot(x_dates, y_line, color='#2E8B57', linewidth=4, alpha=0.9, linestyle='--')
        
        # Engagement density trend
        y_engagement = np.array(engagement_densities)
        z_engagement, p_engagement = _fit_curve_trend(x_ord, y_engagement, degree=2)
        if p_engagement is not None:
            x_line = np.linspace(x_ord.min(), x_ord.max(), 100)
            y_line = p_engagement(x_line)
            x_dates = [pd.Timestamp.fromordinal(int(x)) for x in x_line]
            ax2_twin.plot(x_dates, y_line, color='#FF6347', linewidth=4, alpha=0.9, linestyle='--')
    
    ax2.set_title('Housing Crisis Engagement Trends (EDA - Outliers Removed)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Post Count', color='#2E8B57')
    ax2_twin.set_ylabel('Total Engagement Density', color='#FF6347')
    ax2.grid(True, alpha=0.3)
    
    # Add legend
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)

    # 3) Word cloud with sentiment-based red coloration
    ax3 = fig.add_subplot(gs[2, 0])
    
    # Prepare word cloud data
    word_frequencies = {}
    word_sentiments = {}
    
    for keyword, frequency, sentiment_sum in top_keywords:
        word_frequencies[keyword] = frequency
        word_sentiments[keyword] = sentiment_sum
    
    if word_frequencies:
        wc = WordCloud(width=800, height=400, background_color='white', max_words=50)
        wc.generate_from_frequencies(word_frequencies)
        
        # Create sentiment spectrum colormap
        cmap = _sentiment_colormap()

        def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
            sentiment = word_sentiments.get(word.lower(), 0.0)
            # Map sentiment to color intensity (0-1)
            # Negative sentiment = bright dark red, positive sentiment = very light red
            intensity = (sentiment + 1) / 2.0  # Map from [-1,1] to [0,1]
            intensity = 1 - intensity  # Invert so negative = bright dark red
            rgba = cmap(intensity)
            r, g, b = [int(255 * v) for v in rgba[:3]]
            return f"rgb({r}, {g}, {b})"

        ax3.imshow(wc.recolor(color_func=color_func), interpolation='bilinear')
        ax3.set_title('Housing Crisis Keywords Heatmap (Light Red=Positive, Dark Red=Negative)', fontsize=12, fontweight='bold')
        ax3.axis('off')
        
        # Add color bar explanation
        ax3.text(0.02, 0.02, 'Heatmap Spectrum: Light Red = Positive Sentiment\nDark Red = Negative Sentiment', 
                transform=ax3.transAxes, fontsize=8, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    else:
        ax3.text(0.5, 0.5, 'No keywords found for word cloud', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Housing Crisis Keywords Word Cloud', fontsize=12, fontweight='bold')
        ax3.axis('off')

    # 4) Featured posts section - top 3 highest engagement posts
    ax4 = fig.add_subplot(gs[3, 0])
    
    if not df.empty:
        # Calculate engagement and apply EDA outlier removal
        df['engagement'] = df['score'] + df['num_comments']
        
        # EDA: Remove outliers from engagement data for featured posts
        df_clean_posts = _remove_outliers_iqr(df, 'engagement')
        if len(df_clean_posts) < len(df) * 0.3:  # If too many outliers removed, use z-score method
            df_clean_posts = _remove_outliers_zscore(df, 'engagement', threshold=2.0)
        
        # Get top 3 posts from cleaned data
        top_posts = df_clean_posts.nlargest(3, 'engagement')
        
        # Create featured posts display
        ax4.axis('off')
        ax4.set_title('Featured Posts - Top 3 Highest Engagement (Personal Stories)', fontsize=14, fontweight='bold')
        
        # Display each featured post with better spacing
        y_positions = [0.85, 0.5, 0.15]  # Better spacing for 3 posts
        
        for i, (_, post) in enumerate(top_posts.iterrows()):
            if i >= 3:
                break
                
            y_pos = y_positions[i]
            
            # Post title (truncated if too long)
            title = post['title'][:100] + "..." if len(post['title']) > 100 else post['title']
            
            # Post details
            engagement = post['engagement']
            score = post['score']
            comments = post['num_comments']
            subreddit = post['subreddit']
            created_date = post['created_utc'].strftime('%Y-%m-%d')
            
            # Display post information with better formatting
            post_text = f"#{i+1} r/{subreddit} | {created_date}\n"
            post_text += f"Title: {title}\n"
            post_text += f"Engagement: {engagement} (↑{score} | 💬{comments})\n"
            
            # Add a snippet of the post content if available
            if pd.notna(post['selftext']) and post['selftext'].strip():
                content_snippet = post['selftext'][:200] + "..." if len(post['selftext']) > 200 else post['selftext']
                post_text += f"Content: {content_snippet}\n"
            
            # Color based on engagement level
            if engagement > 1000:
                color = '#FF0000'  # High engagement - red
            elif engagement > 500:
                color = '#FF8000'  # Medium-high engagement - orange
            else:
                color = '#000000'  # Lower engagement - black
            
            ax4.text(0.02, y_pos, post_text, transform=ax4.transAxes, fontsize=10, 
                    verticalalignment='top', color=color, weight='bold' if engagement > 500 else 'normal',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9, edgecolor=color, linewidth=2))
    else:
        ax4.text(0.5, 0.5, 'No posts available for featured section', ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Featured Posts - Highest Engagement', fontsize=12, fontweight='bold')
        ax4.axis('off')