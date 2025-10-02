#!/usr/bin/env python3
"""
Visualization module for Bluesky GUI
Matches the narrative structure of interactive_eda_report.html
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from collections import Counter
from wordcloud import WordCloud
import warnings
warnings.filterwarnings('ignore')


def create_narrative_visualizations(df):
    """
    Create visualizations with clear data journalism narrative flow

    Structure (Top to Bottom):
    1. Keywords Searched - What we're tracking
    2. Period Data Pulled - When data was collected
    3. Content Word Cloud - What people are saying
    4. Geographic Distribution - Where conversations happen
    5. Political Analysis Section:
       - Polarization Gauge (center, spanning full width)
       - Left-leaning Word Cloud | Right-leaning Word Cloud (side by side below gauge)
    6. Content Metrics - Post length distribution
    7. Engagement Analysis - Likes, replies, reposts, hourly patterns
    8. Author Analysis - Top contributors
    9. Top Posts - Most engaging content
    10. Engagement Correlation - Post length vs likes
    11. Collection Summary - Overall metrics
    """

    # Create figure with GridSpec for data journalism layout
    fig = Figure(figsize=(16, 50), dpi=100, facecolor='#f8f8f8')
    gs = fig.add_gridspec(18, 2, hspace=1.0, wspace=0.4,
                          left=0.06, right=0.94, top=0.98, bottom=0.02)

    # Style settings - NYT minimal with card style
    text_color = '#121212'  # Near black
    bg_color = 'white'  # Card background
    page_bg = '#f8f8f8'  # Page background
    grid_color = '#e5e5e5'  # Light gray
    accent_color = '#4a4a4a'  # Dark grey (default for non-political viz)
    border_color = '#d0d0d0'  # Card border
    # Political colors
    left_color = '#4a90e2'  # Blue for left
    right_color = '#e24a4a'  # Red for right

    # 1. KEYWORDS SEARCHED
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor(bg_color)
    ax1.axis('off')
    # Add card border
    for spine in ax1.spines.values():
        spine.set_edgecolor(border_color)
        spine.set_linewidth(1)
        spine.set_visible(True)

    # Extract keywords from data
    all_keywords = []
    if 'keyword_matches' in df.columns:
        for keywords in df['keyword_matches'].dropna().head(100):
            try:
                if isinstance(keywords, str):
                    kw_list = eval(keywords)
                    all_keywords.extend(kw_list)
            except:
                pass

    unique_keywords = list(set(all_keywords))[:20] if all_keywords else ['homelessness', 'housing', 'shelter']

    keywords_text = "Keywords Searched\n" + "─" * 60 + "\n\n"
    keywords_text += "   ".join([f"{kw}" for kw in unique_keywords[:10]]) + "\n"
    if len(unique_keywords) > 10:
        keywords_text += "   ".join([f"{kw}" for kw in unique_keywords[10:20]])

    ax1.text(0.5, 0.9, "Keywords Searched", fontsize=16, color=text_color,
             ha='center', va='top', family='serif', weight='normal')
    ax1.text(0.5, 0.5, "   ".join(unique_keywords[:15]), fontsize=10, color='#666666',
             ha='center', va='center', family='sans-serif', wrap=True)

    # 2. PERIOD DATA PULLED (Timeline)
    ax2 = fig.add_subplot(gs[1, :])
    ax2.set_facecolor(bg_color)
    ax2.patch.set_edgecolor(border_color)
    ax2.patch.set_linewidth(1)

    if 'created_at' in df.columns:
        df['created_at_parsed'] = pd.to_datetime(df['created_at'], errors='coerce', utc=True)
        if df['created_at_parsed'].notna().any():
            df['date'] = df['created_at_parsed'].dt.date
            posts_per_day = df.groupby('date').size().sort_index()

            ax2.plot(posts_per_day.index, posts_per_day.values,
                    color=accent_color, linewidth=2.5, marker='o', markersize=5)
            ax2.fill_between(posts_per_day.index, posts_per_day.values, alpha=0.1, color=accent_color)

            ax2.set_title('Period Data Pulled', fontsize=16, color=text_color,
                         weight='normal', pad=20, family='serif', loc='left')
            ax2.set_xlabel('Date', fontsize=11, color='#666666', family='sans-serif')
            ax2.set_ylabel('Posts', fontsize=11, color='#666666', family='sans-serif')
            ax2.grid(True, alpha=0.3, color=grid_color, linestyle='-', linewidth=0.5)
            ax2.tick_params(colors='#666666', labelsize=9)
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.spines['bottom'].set_color(grid_color)
            ax2.spines['left'].set_color(grid_color)

    # 3. CONTENT WORD CLOUD
    ax3 = fig.add_subplot(gs[2, :])
    ax3.set_facecolor(bg_color)
    ax3.axis('off')
    # Add card border
    for spine in ax3.spines.values():
        spine.set_edgecolor(border_color)
        spine.set_linewidth(1)
        spine.set_visible(True)

    if 'text' in df.columns:
        text_data = ' '.join(df['text'].dropna().astype(str).head(1000))
        if text_data.strip():
            try:
                wc = WordCloud(width=1400, height=400, background_color='white',
                             color_func=lambda *args, **kwargs: accent_color,  # Dark grey
                             max_words=80, relative_scaling=0.4).generate(text_data)
                ax3.imshow(wc, interpolation='bilinear')
                ax3.set_title('Content Word Cloud (All Posts)', fontsize=16, color=text_color,
                            weight='normal', pad=15, family='serif', loc='left')
            except:
                ax3.text(0.5, 0.5, 'No word cloud data', ha='center', va='center',
                        color='#999999', family='sans-serif')

    # 4. GEOGRAPHIC DISTRIBUTION
    ax4 = fig.add_subplot(gs[3, :])
    ax4.set_facecolor(bg_color)
    ax4.patch.set_edgecolor(border_color)
    ax4.patch.set_linewidth(1)

    if 'detected_location' in df.columns:
        location_counts = df['detected_location'].value_counts().head(10)
        if len(location_counts) > 0:
            bars = ax4.barh(range(len(location_counts)), location_counts.values,
                          color=accent_color, height=0.7)
            ax4.set_yticks(range(len(location_counts)))
            ax4.set_yticklabels(location_counts.index, fontsize=10, family='sans-serif')
            ax4.invert_yaxis()
            ax4.set_title('Geographic Distribution', fontsize=16,
                         color=text_color, weight='normal', pad=20, family='serif', loc='left')
            ax4.set_xlabel('Number of Posts', fontsize=11, color='#666666', family='sans-serif')
            ax4.tick_params(colors='#666666', labelsize=9)
            ax4.spines['top'].set_visible(False)
            ax4.spines['right'].set_visible(False)
            ax4.spines['bottom'].set_color(grid_color)
            ax4.spines['left'].set_color(grid_color)
            ax4.grid(True, alpha=0.3, axis='x', color=grid_color, linestyle='-', linewidth=0.5)

    # 5. POLITICAL ANALYSIS SECTION
    # 5a. Political Polarization Gauge (spans full width at top of section)
    ax5a = fig.add_subplot(gs[4, :])
    ax5a.set_facecolor(bg_color)
    ax5a.patch.set_edgecolor(border_color)
    ax5a.patch.set_linewidth(1)

    # Analyze political leaning from text
    left_keywords = ['progressive', 'liberal', 'democrat', 'social justice', 'equity',
                     'climate action', 'healthcare for all', 'lgbtq', 'immigrant rights',
                     'gun control', 'abortion rights', 'blm', 'defund', 'taxing the rich']
    right_keywords = ['conservative', 'republican', 'traditional', 'freedom', 'liberty',
                      'border security', 'pro-life', 'second amendment', 'small government',
                      'law and order', 'patriot', 'maga', 'god', 'family values']

    # Initialize lists for word clouds
    left_texts = []
    right_texts = []

    if 'text' in df.columns:
        left_count = 0
        right_count = 0

        for text in df['text'].dropna().astype(str):
            text_lower = text.lower()
            # Count keyword matches
            left_matches = sum(1 for kw in left_keywords if kw in text_lower)
            right_matches = sum(1 for kw in right_keywords if kw in text_lower)

            if left_matches > right_matches and left_matches > 0:
                left_count += 1
                left_texts.append(text)
            elif right_matches > left_matches and right_matches > 0:
                right_count += 1
                right_texts.append(text)

        # Create half donut gauge chart
        total_polar = left_count + right_count
        if total_polar > 0:
            left_pct = (left_count / total_polar) * 100
            right_pct = (right_count / total_polar) * 100

            # Half donut data
            sizes = [left_pct, right_pct]
            colors = [left_color, right_color]  # Blue for left, red for right
            labels = [f'Left-leaning\n{left_count} posts\n({left_pct:.1f}%)',
                     f'Right-leaning\n{right_count} posts\n({right_pct:.1f}%)']

            # Create wedge pie (half donut)
            wedges, texts, autotexts = ax5a.pie(sizes, labels=labels, colors=colors,
                                               autopct='', startangle=180,
                                               wedgeprops={'width': 0.4, 'linewidth': 1, 'edgecolor': 'white'})

            # Only show bottom half (gauge style)
            ax5a.set_ylim(-1, 0.2)

            for text in texts:
                text.set_fontsize(10)
                text.set_family('sans-serif')

            ax5a.set_title('Political Polarization Analysis',
                         fontsize=18, color=text_color, weight='normal', pad=20,
                         family='serif', loc='center')

            # Add center text showing total
            ax5a.text(0, -0.5, f'{total_polar}\npolarized posts',
                    ha='center', va='center', fontsize=12, color='#666666',
                    family='sans-serif', weight='bold')
        else:
            ax5a.text(0.5, 0.5, 'Insufficient political data', ha='center', va='center',
                    color='#999999', family='sans-serif', fontsize=11)
            ax5a.set_title('Political Polarization Analysis', fontsize=18, color=text_color,
                         weight='normal', pad=20, family='serif', loc='center')

    # 5b. LEFT-LEANING WORD CLOUD (below gauge, left side)
    ax5b = fig.add_subplot(gs[5, 0])
    ax5b.set_facecolor(bg_color)
    ax5b.axis('off')
    for spine in ax5b.spines.values():
        spine.set_edgecolor(border_color)
        spine.set_linewidth(1)
        spine.set_visible(True)

    if len(left_texts) > 0:
        left_text_data = ' '.join(left_texts)
        if left_text_data.strip():
            try:
                wc_left = WordCloud(width=700, height=450, background_color='white',
                                   color_func=lambda *args, **kwargs: left_color,
                                   max_words=60, relative_scaling=0.4).generate(left_text_data)
                ax5b.imshow(wc_left, interpolation='bilinear')
                ax5b.set_title(f'Left-Leaning Content\n{len(left_texts)} posts',
                              fontsize=14, color=left_color, weight='normal', pad=15,
                              family='serif', loc='center')
            except:
                ax5b.text(0.5, 0.5, 'No left-leaning data', ha='center', va='center',
                         color='#999999', family='sans-serif')
    else:
        ax5b.text(0.5, 0.5, 'No left-leaning posts', ha='center', va='center',
                 color='#999999', family='sans-serif', fontsize=10)

    # 5c. RIGHT-LEANING WORD CLOUD (below gauge, right side)
    ax5c = fig.add_subplot(gs[5, 1])
    ax5c.set_facecolor(bg_color)
    ax5c.axis('off')
    for spine in ax5c.spines.values():
        spine.set_edgecolor(border_color)
        spine.set_linewidth(1)
        spine.set_visible(True)

    if len(right_texts) > 0:
        right_text_data = ' '.join(right_texts)
        if right_text_data.strip():
            try:
                wc_right = WordCloud(width=700, height=450, background_color='white',
                                    color_func=lambda *args, **kwargs: right_color,
                                    max_words=60, relative_scaling=0.4).generate(right_text_data)
                ax5c.imshow(wc_right, interpolation='bilinear')
                ax5c.set_title(f'Right-Leaning Content\n{len(right_texts)} posts',
                              fontsize=14, color=right_color, weight='normal', pad=15,
                              family='serif', loc='center')
            except:
                ax5c.text(0.5, 0.5, 'No right-leaning data', ha='center', va='center',
                         color='#999999', family='sans-serif')
    else:
        ax5c.text(0.5, 0.5, 'No right-leaning posts', ha='center', va='center',
                 color='#999999', family='sans-serif', fontsize=10)

    # 6. CONTENT METRICS - Post Length Distribution
    ax6 = fig.add_subplot(gs[6, :])
    ax6.set_facecolor(bg_color)
    ax6.patch.set_edgecolor(border_color)
    ax6.patch.set_linewidth(1)

    if 'text' in df.columns:
        df['text_length'] = df['text'].str.len()
        lengths = df['text_length'].dropna()
        if len(lengths) > 0:
            ax6.hist(lengths, bins=50, color=accent_color, alpha=0.6, edgecolor='white')
            ax6.axvline(lengths.median(), color='#d84a4a', linestyle='--', linewidth=2,
                       label=f'Median: {lengths.median():.0f}')
            ax6.set_title('Content Metrics: Post Length Distribution', fontsize=16, color=text_color,
                         weight='normal', pad=20, family='serif', loc='left')
            ax6.set_xlabel('Characters', fontsize=11, color='#666666', family='sans-serif')
            ax6.set_ylabel('Frequency', fontsize=11, color='#666666', family='sans-serif')
            ax6.tick_params(colors='#666666', labelsize=9)
            ax6.legend(facecolor='white', edgecolor=grid_color, framealpha=1)
            ax6.spines['top'].set_visible(False)
            ax6.spines['right'].set_visible(False)
            ax6.spines['bottom'].set_color(grid_color)
            ax6.spines['left'].set_color(grid_color)
            ax6.grid(True, alpha=0.3, axis='y', color=grid_color, linestyle='-', linewidth=0.5)

    # Skip original keyword categories
    if False and 'keyword_categories' in df.columns:
        all_categories = []
        for cats in df['keyword_categories'].dropna().head(500):
            try:
                if isinstance(cats, str):
                    cat_list = eval(cats)
                    all_categories.extend(cat_list)
            except:
                pass

        if all_categories:
            category_counts = Counter(all_categories)
            cats, counts = zip(*category_counts.most_common(6))
            colors = [accent_color, '#5a9bc4', '#8bb8d6', '#aacce6', '#c9e0f3', '#e8f4fa'][:len(cats)]
            ax6.pie(counts, labels=cats, autopct='%1.1f%%', startangle=90, colors=colors,
                   textprops={'fontsize': 9, 'family': 'sans-serif'},
                   wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
            ax6.set_title('Keyword Categories', fontsize=14, color=text_color,
                         weight='normal', pad=15, family='serif')

    # 7. ENGAGEMENT ANALYSIS - Total Engagement
    ax7 = fig.add_subplot(gs[7, 0])
    ax7.set_facecolor(bg_color)
    ax7.patch.set_edgecolor(border_color)
    ax7.patch.set_linewidth(1)

    engagement_data = []
    labels = []
    if 'like_count' in df.columns:
        engagement_data.append(df['like_count'].sum())
        labels.append('Likes')
    if 'reply_count' in df.columns:
        engagement_data.append(df['reply_count'].sum())
        labels.append('Replies')
    if 'repost_count' in df.columns:
        engagement_data.append(df['repost_count'].sum())
        labels.append('Reposts')

    if engagement_data:
        bars = ax7.bar(labels, engagement_data,
                      color=[accent_color, '#5a9bc4', '#8bb8d6'][:len(labels)], width=0.6)
        ax7.set_title('Engagement: Total Counts', fontsize=14, color=text_color,
                     weight='normal', pad=20, family='serif', loc='left')
        ax7.set_ylabel('Count', fontsize=10, color='#666666', family='sans-serif')
        ax7.tick_params(colors='#666666', labelsize=9)
        for i, v in enumerate(engagement_data):
            ax7.text(i, v, f'{int(v):,}', ha='center', va='bottom',
                    color='#666666', fontsize=9, family='sans-serif')
        ax7.spines['top'].set_visible(False)
        ax7.spines['right'].set_visible(False)
        ax7.spines['bottom'].set_color(grid_color)
        ax7.spines['left'].set_color(grid_color)
        ax7.grid(True, alpha=0.3, axis='y', color=grid_color, linestyle='-', linewidth=0.5)

    # 8. ENGAGEMENT ANALYSIS - Hourly Pattern
    ax8 = fig.add_subplot(gs[7, 1])
    ax8.set_facecolor(bg_color)
    ax8.patch.set_edgecolor(border_color)
    ax8.patch.set_linewidth(1)

    if 'created_at_parsed' in df.columns and df['created_at_parsed'].notna().any():
        df['hour'] = df['created_at_parsed'].dt.hour
        hourly_counts = df.groupby('hour').size()
        ax8.bar(hourly_counts.index, hourly_counts.values, color=accent_color, alpha=0.7, width=0.8)
        ax8.set_title('Engagement: Hourly Posting Pattern', fontsize=14, color=text_color,
                     weight='normal', pad=20, family='serif', loc='left')
        ax8.set_xlabel('Hour (UTC)', fontsize=10, color='#666666', family='sans-serif')
        ax8.set_ylabel('Posts', fontsize=10, color='#666666', family='sans-serif')
        ax8.tick_params(colors='#666666', labelsize=9)
        ax8.set_xticks(range(0, 24, 3))
        ax8.spines['top'].set_visible(False)
        ax8.spines['right'].set_visible(False)
        ax8.spines['bottom'].set_color(grid_color)
        ax8.spines['left'].set_color(grid_color)
        ax8.grid(True, alpha=0.3, axis='y', color=grid_color, linestyle='-', linewidth=0.5)

    # 9. AUTHOR ANALYSIS - Top Authors
    ax9 = fig.add_subplot(gs[8, :])
    ax9.set_facecolor(bg_color)
    ax9.patch.set_edgecolor(border_color)
    ax9.patch.set_linewidth(1)

    if 'author_handle' in df.columns:
        author_counts = df['author_handle'].value_counts().head(15)
        bars = ax9.barh(range(len(author_counts)), author_counts.values,
                       color=accent_color, height=0.7)
        ax9.set_yticks(range(len(author_counts)))
        ax9.set_yticklabels([f'@{handle}' for handle in author_counts.index],
                           fontsize=9, family='sans-serif')
        ax9.invert_yaxis()
        ax9.set_title('Author Analysis: Top 15 Contributors', fontsize=16, color=text_color,
                     weight='normal', pad=20, family='serif', loc='left')
        ax9.set_xlabel('Number of Posts', fontsize=11, color='#666666', family='sans-serif')
        ax9.tick_params(colors='#666666', labelsize=9)
        ax9.spines['top'].set_visible(False)
        ax9.spines['right'].set_visible(False)
        ax9.spines['bottom'].set_color(grid_color)
        ax9.spines['left'].set_color(grid_color)
        ax9.grid(True, alpha=0.3, axis='x', color=grid_color, linestyle='-', linewidth=0.5)

    # 10. TOP POSTS BY LIKES
    ax10 = fig.add_subplot(gs[9:12, :])
    ax10.set_facecolor(bg_color)
    ax10.axis('off')
    # Add card border
    for spine in ax10.spines.values():
        spine.set_edgecolor(border_color)
        spine.set_linewidth(1)
        spine.set_visible(True)

    if 'like_count' in df.columns and 'text' in df.columns:
        top_posts = df.nlargest(5, 'like_count')[['author_handle', 'text', 'like_count', 'reply_count']]

        # Title
        ax10.text(0.05, 0.97, "Most Engaging Posts", fontsize=18, color=text_color,
                 ha='left', va='top', family='serif', weight='normal')

        # Posts
        y_pos = 0.87
        for idx, (_, row) in enumerate(top_posts.iterrows(), 1):
            author = row.get('author_handle', 'unknown')
            text = str(row.get('text', ''))[:180] + ('...' if len(str(row.get('text', ''))) > 180 else '')
            likes = int(row.get('like_count', 0))
            replies = int(row.get('reply_count', 0))

            # Author and metrics
            ax10.text(0.05, y_pos, f"@{author}", fontsize=10, color=accent_color,
                     ha='left', va='top', family='sans-serif', weight='bold')
            ax10.text(0.95, y_pos, f"{likes:,} likes  •  {replies:,} replies",
                     fontsize=9, color='#999999', ha='right', va='top', family='sans-serif')

            # Post text
            ax10.text(0.05, y_pos - 0.03, text, fontsize=9, color='#333333',
                     ha='left', va='top', family='sans-serif', wrap=True)

            # Separator line
            if idx < 5:
                ax10.plot([0.05, 0.95], [y_pos - 0.11, y_pos - 0.11],
                         color=grid_color, linewidth=0.5)

            y_pos -= 0.16

    # 11. ENGAGEMENT CORRELATION
    ax11 = fig.add_subplot(gs[12, 0])
    ax11.set_facecolor(bg_color)
    ax11.patch.set_edgecolor(border_color)
    ax11.patch.set_linewidth(1)

    if 'like_count' in df.columns and 'text_length' in df.columns:
        sample = df.sample(min(1000, len(df)))
        ax11.scatter(sample['text_length'], sample['like_count'],
                    alpha=0.4, color=accent_color, s=30, edgecolors='white', linewidth=0.5)
        ax11.set_title('Correlation: Post Length vs Engagement', fontsize=14, color=text_color,
                      weight='normal', pad=20, family='serif', loc='left')
        ax11.set_xlabel('Post Length (characters)', fontsize=10, color='#666666', family='sans-serif')
        ax11.set_ylabel('Likes', fontsize=10, color='#666666', family='sans-serif')
        ax11.tick_params(colors='#666666', labelsize=9)
        ax11.spines['top'].set_visible(False)
        ax11.spines['right'].set_visible(False)
        ax11.spines['bottom'].set_color(grid_color)
        ax11.spines['left'].set_color(grid_color)
        ax11.grid(True, alpha=0.3, color=grid_color, linestyle='-', linewidth=0.5)

    # 12. COLLECTION SUMMARY
    ax12 = fig.add_subplot(gs[12:, 1])
    ax12.set_facecolor(bg_color)
    ax12.axis('off')
    # Add card border
    for spine in ax12.spines.values():
        spine.set_edgecolor(border_color)
        spine.set_linewidth(1)
        spine.set_visible(True)

    # Build summary
    date_range_text = "N/A"
    if 'created_at_parsed' in df.columns and df['created_at_parsed'].notna().any():
        min_date = df['created_at_parsed'].min()
        max_date = df['created_at_parsed'].max()
        if pd.notna(min_date) and pd.notna(max_date):
            date_range_text = f"{min_date.date()} to {max_date.date()}"

    # Title
    ax12.text(0.1, 0.95, "Collection Summary", fontsize=16, color=text_color,
             ha='left', va='top', family='serif', weight='normal')

    y = 0.85
    line_height = 0.08

    # Basic metrics
    ax12.text(0.1, y, f"Total Posts", fontsize=11, color='#666666', ha='left', va='top', family='sans-serif')
    ax12.text(0.9, y, f"{len(df):,}", fontsize=11, color=text_color, ha='right', va='top',
             family='sans-serif', weight='bold')
    y -= line_height

    ax12.text(0.1, y, f"Date Range", fontsize=11, color='#666666', ha='left', va='top', family='sans-serif')
    ax12.text(0.9, y, date_range_text, fontsize=9, color=text_color, ha='right', va='top', family='sans-serif')
    y -= line_height * 1.5

    # Engagement section
    ax12.text(0.1, y, "Engagement", fontsize=13, color=text_color, ha='left', va='top',
             family='serif', style='italic')
    y -= line_height * 0.8

    ax12.text(0.15, y, f"Total Likes", fontsize=10, color='#666666', ha='left', va='top', family='sans-serif')
    ax12.text(0.9, y, f"{df['like_count'].sum() if 'like_count' in df.columns else 0:,}",
             fontsize=10, color=text_color, ha='right', va='top', family='sans-serif')
    y -= line_height * 0.7

    ax12.text(0.15, y, f"Total Replies", fontsize=10, color='#666666', ha='left', va='top', family='sans-serif')
    ax12.text(0.9, y, f"{df['reply_count'].sum() if 'reply_count' in df.columns else 0:,}",
             fontsize=10, color=text_color, ha='right', va='top', family='sans-serif')
    y -= line_height * 0.7

    ax12.text(0.15, y, f"Avg Likes per Post", fontsize=10, color='#666666', ha='left', va='top', family='sans-serif')
    ax12.text(0.9, y, f"{df['like_count'].mean() if 'like_count' in df.columns else 0:.1f}",
             fontsize=10, color=text_color, ha='right', va='top', family='sans-serif')
    y -= line_height * 1.3

    # Content section
    ax12.text(0.1, y, "Content", fontsize=13, color=text_color, ha='left', va='top',
             family='serif', style='italic')
    y -= line_height * 0.8

    ax12.text(0.15, y, f"Avg Length", fontsize=10, color='#666666', ha='left', va='top', family='sans-serif')
    ax12.text(0.9, y, f"{df['text_length'].mean() if 'text_length' in df.columns else 0:.0f} chars",
             fontsize=10, color=text_color, ha='right', va='top', family='sans-serif')
    y -= line_height * 0.7

    ax12.text(0.15, y, f"Unique Locations", fontsize=10, color='#666666', ha='left', va='top', family='sans-serif')
    ax12.text(0.9, y, f"{df['detected_location'].nunique() if 'detected_location' in df.columns else 0}",
             fontsize=10, color=text_color, ha='right', va='top', family='sans-serif')
    y -= line_height * 1.3

    # Author section
    ax12.text(0.1, y, "Authors", fontsize=13, color=text_color, ha='left', va='top',
             family='serif', style='italic')
    y -= line_height * 0.8

    ax12.text(0.15, y, f"Unique Authors", fontsize=10, color='#666666', ha='left', va='top', family='sans-serif')
    ax12.text(0.9, y, f"{df['author_handle'].nunique() if 'author_handle' in df.columns else 0:,}",
             fontsize=10, color=text_color, ha='right', va='top', family='sans-serif')
    y -= line_height * 0.7

    ax12.text(0.15, y, f"Avg Posts per Author", fontsize=10, color='#666666', ha='left', va='top', family='sans-serif')
    ax12.text(0.9, y, f"{len(df)/df['author_handle'].nunique() if 'author_handle' in df.columns and df['author_handle'].nunique() > 0 else 0:.1f}",
             fontsize=10, color=text_color, ha='right', va='top', family='sans-serif')

    return fig
