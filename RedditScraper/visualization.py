import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from wordcloud import WordCloud
from matplotlib.colors import LinearSegmentedColormap
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from scipy.interpolate import make_interp_spline
from scipy.ndimage import gaussian_filter1d


def _time_bin(df: pd.DataFrame) -> pd.Series:
    # Use weekly binning by finding the start of each week (Monday)
    return df['created_utc'].dt.to_period('W').dt.start_time


def _create_smooth_density_plot(ax, time_bins, values, color, alpha=0.3, label='', line_color=None):
    """Create smooth, hill-like density plots using interpolation and smoothing."""
    if len(time_bins) < 2:
        return
    
    # Convert time bins to numeric for interpolation
    time_numeric = np.array([tb.toordinal() for tb in time_bins])
    values_array = np.array(values)
    
    # Create smooth interpolation
    if len(time_numeric) >= 3:
        # Use cubic spline interpolation for smooth curves
        try:
            # Create more points for smoother curves
            time_smooth = np.linspace(time_numeric.min(), time_numeric.max(), 200)
            spl = make_interp_spline(time_numeric, values_array, k=min(3, len(time_numeric)-1))
            values_smooth = spl(time_smooth)
        except:
            # Fallback to linear interpolation if spline fails
            time_smooth = np.linspace(time_numeric.min(), time_numeric.max(), 200)
            values_smooth = np.interp(time_smooth, time_numeric, values_array)
    else:
        # For very few points, use simple interpolation
        time_smooth = np.linspace(time_numeric.min(), time_numeric.max(), 200)
        values_smooth = np.interp(time_smooth, time_numeric, values_array)
    
    # Apply Gaussian smoothing for hill-like structure
    values_smooth = gaussian_filter1d(values_smooth, sigma=2)
    
    # Convert back to datetime for plotting
    time_smooth_dt = [pd.Timestamp.fromordinal(int(t)) for t in time_smooth]
    
    # Create the smooth density plot
    ax.fill_between(time_smooth_dt, values_smooth, alpha=alpha, color=color, label=label)
    
    # Add smooth line overlay
    line_color = line_color or color
    ax.plot(time_smooth_dt, values_smooth, color=line_color, linewidth=2, alpha=0.8)
    
    return time_smooth_dt, values_smooth


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
    fig.set_size_inches(16, 18)  # Increased height for better spacing
    gs = fig.add_gridspec(3, 1, hspace=0.6, wspace=0.3, height_ratios=[2.5, 1.5, 1.5])

    # Import the new analysis functions
    from .analysis import get_top_topic_keywords_by_frequency, aggregate_topic_keyword_sentiments
    
    # Get top keywords with their sentiment data
    top_keywords = get_top_topic_keywords_by_frequency(df, topic='housing_crisis', top_n=30)
    
    # 1) Housing Crisis Engagement Trends (Main Analysis)
    ax1 = fig.add_subplot(gs[0, 0])
    
    if df.empty:
        ax1.text(0.5, 0.5, 'No data for engagement analysis', ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Housing Crisis Engagement Trends', fontsize=14, fontweight='bold')
        ax1.axis('off')
        
        # Show empty word cloud
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.text(0.5, 0.5, 'No keywords found for word cloud', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Housing Crisis Keywords Word Cloud', fontsize=12, fontweight='bold')
        ax2.axis('off')
        
        # Show empty featured posts
        ax3 = fig.add_subplot(gs[2, 0])
        ax3.text(0.5, 0.5, 'No posts available for featured section', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Featured Posts - Highest Engagement', fontsize=12, fontweight='bold')
        ax3.axis('off')
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
        
        # Plot smooth density plots for both post count and engagement
        ax1_twin = ax1.twinx()
        
        # Post count smooth density (hill-like structure)
        _create_smooth_density_plot(ax1, time_bins, post_counts, color='#2E8B57', alpha=0.3, label='Post Count Density')

        # Engagement smooth density (hill-like structure)
        _create_smooth_density_plot(ax1_twin, time_bins, engagement_densities, color='#FF6347', alpha=0.3, label='Total Engagement Density')
        
        # Add individual data points for visibility
        for i, (tb, count, engagement) in enumerate(zip(time_bins, post_counts, engagement_densities)):
            # Color intensity based on engagement density
            intensity = min(1.0, engagement / max(engagement_densities) if max(engagement_densities) > 0 else 0)
            color = plt.cm.Reds(intensity)
            
            # Plot individual points
            ax1.scatter(tb, count, c=[color], s=100, alpha=0.7, edgecolors='black', linewidth=1)
            ax1_twin.scatter(tb, engagement, c=[color], s=100, alpha=0.7, edgecolors='black', linewidth=1)
        
        ax1.set_title('Housing Crisis Engagement Trends - Weekly Analysis', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Time (Weekly Bins)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Post Count (Weekly Aggregation)', color='#2E8B57', fontsize=11, fontweight='bold')
        ax1_twin.set_ylabel('Total Engagement Density (Upvotes + Comments)', color='#FF6347', fontsize=11, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Add comprehensive legend with explanations
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9, framealpha=0.9)
        
        # Add detailed explanation text box outside the plot area
        explanation_text = (
            "📊 DATA EXPLANATION:\n"
            "• Green Hills = Post Count Density (number of posts per week)\n"
            "• Red Hills = Engagement Density (total upvotes + comments per week)\n"
            "• Point Colors = Engagement intensity (darker red = higher engagement)\n"
            "• Smooth curves created using cubic spline interpolation + Gaussian smoothing\n"
            "• Weekly binning shows natural trends over time periods"
        )
        # Position explanation below the plot
        ax1.text(0.5, -0.15, explanation_text, transform=ax1.transAxes, fontsize=9,
                horizontalalignment='center', verticalalignment='top', 
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))

    # 2) Word cloud with sentiment-based red coloration
    ax2 = fig.add_subplot(gs[1, 0])
    
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

        ax2.imshow(wc.recolor(color_func=color_func), interpolation='bilinear')
        ax2.set_title('Housing Crisis Keywords Heatmap (Light Red=Positive, Dark Red=Negative)', fontsize=12, fontweight='bold')
        ax2.axis('off')
        
        # Add color bar explanation
        ax2.text(0.02, 0.02, 'Heatmap Spectrum: Light Red = Positive Sentiment\nDark Red = Negative Sentiment', 
                transform=ax2.transAxes, fontsize=8, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    else:
        ax2.text(0.5, 0.5, 'No keywords found for word cloud', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Housing Crisis Keywords Word Cloud', fontsize=12, fontweight='bold')
        ax2.axis('off')

    # 3) Featured posts section - top 3 highest engagement posts
    ax3 = fig.add_subplot(gs[2, 0])
    
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
        ax3.axis('off')
        ax3.set_title('Featured Posts - Top 3 Highest Engagement (Personal Stories)', fontsize=14, fontweight='bold')
        
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
            
            ax3.text(0.02, y_pos, post_text, transform=ax3.transAxes, fontsize=10, 
                    verticalalignment='top', color=color, weight='bold' if engagement > 500 else 'normal',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9, edgecolor=color, linewidth=2))
    else:
        ax3.text(0.5, 0.5, 'No posts available for featured section', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Featured Posts - Highest Engagement', fontsize=12, fontweight='bold')
        ax3.axis('off')