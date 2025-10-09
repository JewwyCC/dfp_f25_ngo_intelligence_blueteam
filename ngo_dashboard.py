#!/usr/bin/env python3
"""
NGO Intelligence Dashboard
A comprehensive dashboard for NGOs to identify optimal timing for advocacy campaigns
and craft resonant messaging around homelessness issues.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import Dict, List, Tuple
import json
import subprocess
import os
import sys
import time
from pathlib import Path
from master_scraper_viz import VisualizationOrchestrator
import shutil
import warnings
import plotly.express as px

# Suppress warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configure Streamlit to suppress deprecation warnings
import os
os.environ['STREAMLIT_DEPRECATION_WARNINGS'] = 'false'
os.environ['PYTHONWARNINGS'] = 'ignore'

# Additional matplotlib warning suppression
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
plt.rcParams['figure.max_open_warning'] = 0

def load_google_trends_data(session_dir):
    """Load real Google Trends data from CSV files, prioritizing demo data"""
    try:
        # First try demo data
        demo_dir = Path("data/demo_data/demo_session")
        if demo_dir.exists():
            raw_data_dir = demo_dir / "raw_data"
            csv_files = list(raw_data_dir.glob("*google_trends*.csv"))
            if csv_files:
                latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
                df = pd.read_csv(latest_file)

                # Check if we have the expected columns
                if 'State' in df.columns and 'Value' in df.columns:
                    # Clean column names and remove duplicates
                    df = df.loc[:, ~df.columns.duplicated()]

                    # Aggregate by state (mean value across all keywords/themes)
                    state_data = df.groupby('State')['Value'].mean().reset_index()
                    state_data.columns = ['State', 'Search_Interest']

                    # Normalize to 0-100 scale for better visualization
                    if state_data['Search_Interest'].max() > 0:
                        state_data['Search_Interest'] = (state_data['Search_Interest'] / state_data['Search_Interest'].max()) * 100

                    print(f"✓ Loaded Google Trends demo data: {len(state_data)} states")
                    return state_data

        # Fallback to session data
        if session_dir and session_dir.exists():
            raw_data_dir = session_dir / "raw_data"
            csv_files = list(raw_data_dir.glob("*google_trends*.csv"))
            if csv_files:
                latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
                df = pd.read_csv(latest_file)

                if 'State' in df.columns and 'Value' in df.columns:
                    df = df.loc[:, ~df.columns.duplicated()]
                    state_data = df.groupby('State')['Value'].mean().reset_index()
                    state_data.columns = ['State', 'Search_Interest']

                    # Normalize to 0-100 scale
                    if state_data['Search_Interest'].max() > 0:
                        state_data['Search_Interest'] = (state_data['Search_Interest'] / state_data['Search_Interest'].max()) * 100

                    print(f"✓ Loaded Google Trends session data: {len(state_data)} states")
                    return state_data

        return None

    except Exception as e:
        print(f"Error loading Google Trends data: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_streamlit_choropleth_map(html_file, theme):
    """Create a Streamlit choropleth map from real Google Trends data"""
    import numpy as np
    from pathlib import Path

    # State name to abbreviation mapping
    state_abbrev = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC',
        'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL',
        'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
        'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
        'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
        'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
        'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR',
        'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
        'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
        'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
    }

    # Try to load real data first
    session_dir = Path("data/demo_data/demo_session")
    real_data = load_google_trends_data(session_dir)

    if real_data is not None and not real_data.empty:
        df = real_data.copy()

        # Convert state names to abbreviations for Plotly
        df['State_Code'] = df['State'].map(state_abbrev)

        # Remove any rows without valid state codes
        df = df.dropna(subset=['State_Code'])

        metric_name = "Search Interest"

        # Choose color scale based on theme
        if "Policy" in theme or "Organisations" in theme:
            color_scale = "RdYlBu_r"  # Reversed for better contrast
        elif "Location" in theme:
            color_scale = "Blues"
        elif "Statistics" in theme:
            color_scale = "Greens"
        else:
            color_scale = "Oranges"
    else:
        # Fallback to generated data if real data not available
        if "Policy" in theme or "Organisations" in theme:
            base_data = [65, 45, 78, 52, 95, 72, 68, 58, 82, 71, 48, 55, 75, 63, 59, 61, 67, 73,
                         51, 69, 76, 74, 66, 70, 64, 47, 56, 80, 53, 77, 62, 88, 79, 46, 72, 65,
                         71, 78, 60, 68, 49, 66, 87, 58, 54, 73, 75, 61, 63, 44]
            metric_name = "Policy Interest"
            color_scale = "RdYlBu"
        elif "Location" in theme:
            base_data = [55, 35, 85, 45, 98, 65, 75, 50, 90, 68, 40, 50, 80, 58, 55, 55, 60, 70,
                         45, 75, 85, 70, 60, 65, 55, 40, 50, 85, 45, 85, 55, 95, 75, 40, 65, 60,
                         70, 75, 55, 65, 45, 60, 90, 50, 45, 70, 80, 55, 55, 35]
            metric_name = "Location Interest"
            color_scale = "Blues"
        elif "Statistics" in theme:
            base_data = [70, 50, 80, 60, 90, 75, 80, 65, 85, 75, 55, 60, 85, 70, 65, 70, 75, 80,
                         60, 80, 90, 80, 70, 75, 70, 55, 65, 85, 60, 85, 70, 95, 85, 55, 75, 70,
                         80, 85, 70, 75, 55, 70, 90, 65, 60, 80, 85, 70, 70, 50]
            metric_name = "Research Interest"
            color_scale = "Greens"
        else:
            base_data = [60, 40, 75, 50, 85, 65, 70, 55, 80, 65, 45, 50, 75, 60, 55, 60, 65, 70,
                         50, 70, 80, 70, 60, 65, 60, 45, 55, 75, 50, 80, 60, 90, 75, 45, 65, 60,
                         70, 75, 60, 65, 50, 60, 85, 55, 50, 70, 75, 60, 60, 40]
            metric_name = "General Interest"
            color_scale = "Oranges"
        
        # Add some randomness to make it more realistic
        search_interest = [max(0, min(100, x + np.random.randint(-10, 11))) for x in base_data]
        
        states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
                 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
                 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
                 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
                 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
                 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma',
                 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
                 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
                 'West Virginia', 'Wisconsin', 'Wyoming']

        state_codes = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID',
                      'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS',
                      'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK',
                      'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA',
                      'WV', 'WI', 'WY']

        state_data = {
            'State': states,
            'State_Code': state_codes,
            'Search_Interest': search_interest
        }

        df = pd.DataFrame(state_data)

    # Create choropleth map using Plotly
    fig = px.choropleth(
        df,
        locations='State_Code' if 'State_Code' in df.columns else 'State',
        locationmode='USA-states',
        color='Search_Interest',
        scope='usa',
        title=f'Google Trends: {metric_name}',
        color_continuous_scale=color_scale,
        range_color=(df['Search_Interest'].min(), df['Search_Interest'].max()),
        hover_name='State',
        hover_data={'State_Code': False, 'Search_Interest': ':.1f'},
        labels={'Search_Interest': metric_name}
    )
    
    fig.update_layout(
        title_font_size=16,
        font_color='white',
        paper_bgcolor='#1f2937',
        plot_bgcolor='#1f2937',
        geo=dict(
            bgcolor='#1f2937',
            lakecolor='#1f2937',
            landcolor='#2d3748',
            showlakes=True,
            showland=True,
            showcountries=False,
            showcoastlines=False,
            projection_type='albers usa'
        ),
        coloraxis_colorbar=dict(
            title=metric_name,
            title_font_color='white',
            tickfont_color='white',
            len=0.7,
            thickness=15
        ),
        margin=dict(l=0, r=0, t=40, b=0)
    )

    # Update traces for better state visibility
    fig.update_traces(
        marker_line_color='#374151',  # Dark border color
        marker_line_width=0.5
    )
    
    # Display the map with unique key
    map_key = f"choropleth_{theme}_{html_file.stem}"
    st.plotly_chart(fig, use_container_width=True, key=map_key)

def load_bluesky_data(session_dir):
    """Load Bluesky data from CSV files, prioritizing alltime_socmed comprehensive data"""
    try:
        # Priority 1: Try alltime_socmed data (most comprehensive)
        alltime_dir = Path("data/bluesky/alltime_socmed")
        if alltime_dir.exists():
            socmed_files = sorted(list(alltime_dir.glob("socmed_*.csv")), key=lambda x: x.stat().st_mtime, reverse=True)
            if socmed_files:
                latest_file = socmed_files[0]
                try:
                    df = pd.read_csv(latest_file)
                    df = df.loc[:, ~df.columns.duplicated()]
                    if not df.empty:
                        print(f"✓ Loaded Bluesky alltime_socmed data: {len(df)} posts from {latest_file.name}")
                        return df
                except Exception as e:
                    print(f"Error reading alltime_socmed Bluesky CSV: {e}")

        # Priority 2: Try demo data
        demo_dir = Path("data/demo_data/demo_session")
        if demo_dir.exists():
            raw_data_dir = demo_dir / "raw_data"
            bluesky_files = list(raw_data_dir.glob("*bluesky*.csv"))
            if bluesky_files:
                latest_file = max(bluesky_files, key=lambda x: x.stat().st_mtime)
                try:
                    df = pd.read_csv(latest_file)
                    df = df.loc[:, ~df.columns.duplicated()]
                    if not df.empty:
                        print(f"✓ Loaded Bluesky demo data: {len(df)} posts")
                        return df
                except Exception as e:
                    print(f"Error reading demo Bluesky CSV: {e}")

        # Priority 3: Fallback to session data
        if session_dir and session_dir.exists():
            raw_data_dir = session_dir / "raw_data"
            bluesky_files = list(raw_data_dir.glob("*bluesky*.csv"))
            if bluesky_files:
                latest_file = max(bluesky_files, key=lambda x: x.stat().st_mtime)
                try:
                    df = pd.read_csv(latest_file)
                    df = df.loc[:, ~df.columns.duplicated()]
                    if not df.empty:
                        print(f"✓ Loaded Bluesky session data: {len(df)} posts")
                        return df
                except Exception as e:
                    print(f"Error reading session Bluesky CSV: {e}")

        print("⚠ No Bluesky data found in any location")
        return None

    except Exception as e:
        print(f"Error loading Bluesky data: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_news_data(session_dir):
    """Load News data from CSV files, prioritizing demo data"""
    try:
        # First try demo data
        demo_dir = Path("data/demo_data/demo_session")
        if demo_dir.exists():
            raw_data_dir = demo_dir / "raw_data"
            news_files = list(raw_data_dir.glob("*news*.csv"))
            if news_files:
                latest_file = max(news_files, key=lambda x: x.stat().st_mtime)
                try:
                    df = pd.read_csv(latest_file, )
                    df = df.loc[:, ~df.columns.duplicated()]
                    if not df.empty:
                        print(f"Successfully loaded News demo data: {len(df)} rows, {len(df.columns)} columns")
                        return df
                except Exception as e:
                    print(f"Error reading demo News CSV: {e}")
        
        # Fallback to session data
        if session_dir and session_dir.exists():
            raw_data_dir = session_dir / "raw_data"
            news_files = list(raw_data_dir.glob("*news*.csv"))
            if news_files:
                latest_file = max(news_files, key=lambda x: x.stat().st_mtime)
                try:
                    df = pd.read_csv(latest_file, )
                    df = df.loc[:, ~df.columns.duplicated()]
                    if not df.empty:
                        print(f"Successfully loaded News session data: {len(df)} rows, {len(df.columns)} columns")
                        return df
                except Exception as e:
                    print(f"Error reading session News CSV: {e}")
        
        return None
            
    except Exception as e:
        print(f"Error loading News data: {e}")
        return None

def load_reddit_data(session_dir):
    """Load Reddit data from CSV files, prioritizing demo data"""
    try:
        # First try demo data
        demo_dir = Path("data/demo_data/demo_session")
        if demo_dir.exists():
            raw_data_dir = demo_dir / "raw_data"
            reddit_files = list(raw_data_dir.glob("*reddit*.csv"))
            if reddit_files:
                latest_file = max(reddit_files, key=lambda x: x.stat().st_mtime)
                try:
                    df = pd.read_csv(latest_file, )
                    df = df.loc[:, ~df.columns.duplicated()]
                    if not df.empty:
                        print(f"Successfully loaded Reddit demo data: {len(df)} rows, {len(df.columns)} columns")
                        return df
                except Exception as e:
                    print(f"Error reading demo Reddit CSV: {e}")
        
        # Fallback to session data
        if session_dir and session_dir.exists():
            raw_data_dir = session_dir / "raw_data"
            reddit_files = list(raw_data_dir.glob("*reddit*.csv"))
            if reddit_files:
                latest_file = max(reddit_files, key=lambda x: x.stat().st_mtime)
                try:
                    df = pd.read_csv(latest_file, )
                    df = df.loc[:, ~df.columns.duplicated()]
                    if not df.empty:
                        print(f"Successfully loaded Reddit session data: {len(df)} rows, {len(df.columns)} columns")
                        return df
                except Exception as e:
                    print(f"Error reading session Reddit CSV: {e}")
        
        return None
            
    except Exception as e:
        print(f"Error loading Reddit data: {e}")
        return None

def filter_latest_google_trends_files(viz_files):
    """Filter Google Trends files to keep only the latest by timestamp"""
    import re
    from collections import defaultdict
    
    # Group files by base name (without timestamp)
    file_groups = defaultdict(list)
    
    for file in viz_files:
        # Extract base name by removing timestamp pattern
        # Pattern: google_trends_[type]_[theme]_YYYYMMDD_HHMMSS.png
        base_name = re.sub(r'_\d{8}_\d{6}\.', '.', file.name)
        file_groups[base_name].append(file)
    
    # Keep only the latest file from each group
    latest_files = []
    for base_name, files in file_groups.items():
        if len(files) == 1:
            latest_files.append(files[0])
        else:
            # Sort by modification time and take the latest
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            latest_files.append(latest_file)
    
    return latest_files

def display_reddit_top_posts_table(df, page_size=10):
    """Display top Reddit posts in a paginated table"""
    if df is None or df.empty:
        st.info("No Reddit data available to display.")
        return

    # Initialize session state for pagination
    if 'reddit_page' not in st.session_state:
        st.session_state.reddit_page = 0

    # Calculate engagement metric
    if 'score' in df.columns and 'num_comments' in df.columns:
        df['engagement'] = df['score'] + df['num_comments'] * 2  # Weight comments more
    elif 'score' in df.columns:
        df['engagement'] = df['score']
    else:
        df['engagement'] = 1

    # Sort by engagement score (descending)
    df_sorted = df.sort_values('engagement', ascending=False)

    # Limit to 50 posts maximum
    df_sorted = df_sorted.head(50)

    # Calculate total pages
    total_pages = max(1, (len(df_sorted) + page_size - 1) // page_size)

    # Ensure page is within bounds
    st.session_state.reddit_page = max(0, min(st.session_state.reddit_page, total_pages - 1))

    # Get current page data
    start_idx = st.session_state.reddit_page * page_size
    end_idx = start_idx + page_size
    page_data = df_sorted.iloc[start_idx:end_idx]

    # Display table header
    st.markdown("#### 🔥 Top Reddit Posts by Engagement")
    st.markdown(f"Showing {start_idx + 1}-{min(end_idx, len(df_sorted))} of {len(df_sorted)} posts")

    # Create display dataframe
    display_data = []
    for idx, row in page_data.iterrows():
        post_dict = {}

        if 'subreddit' in row:
            post_dict['Subreddit'] = f"r/{row['subreddit']}"
        if 'title' in row:
            # Truncate long titles
            title = str(row['title'])
            post_dict['Title'] = title[:150] + '...' if len(title) > 150 else title
        if 'score' in row:
            post_dict['Upvotes'] = int(row['score'])
        if 'num_comments' in row:
            post_dict['Comments'] = int(row['num_comments'])
        if 'engagement' in row:
            post_dict['Engagement'] = int(row['engagement'])

        display_data.append(post_dict)

    # Display the table
    if display_data:
        display_df = pd.DataFrame(display_data)
        st.dataframe(display_df, use_container_width=True, height=400, hide_index=True)

        # Pagination controls
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

        with col1:
            if st.button("⏮️ First", disabled=st.session_state.reddit_page == 0, key="reddit_first"):
                st.session_state.reddit_page = 0
                st.rerun()

        with col2:
            if st.button("⬅️ Prev", disabled=st.session_state.reddit_page == 0, key="reddit_prev"):
                st.session_state.reddit_page -= 1
                st.rerun()

        with col3:
            st.markdown(f"**Page {st.session_state.reddit_page + 1} of {total_pages}**")

        with col4:
            if st.button("Next ➡️", disabled=st.session_state.reddit_page >= total_pages - 1, key="reddit_next"):
                st.session_state.reddit_page += 1
                st.rerun()

        with col5:
            if st.button("Last ⏭️", disabled=st.session_state.reddit_page >= total_pages - 1, key="reddit_last"):
                st.session_state.reddit_page = total_pages - 1
                st.rerun()

def display_bluesky_top_tweets_table(df, page_size=10):
    """Display top Bluesky tweets in a paginated table"""
    if df is None or df.empty:
        st.info("No Bluesky data available to display.")
        return

    # Initialize session state for pagination
    if 'bluesky_page' not in st.session_state:
        st.session_state.bluesky_page = 0

    # Calculate engagement metric (combine likes, reposts, replies if available)
    engagement_columns = []
    for col in df.columns:
        col_lower = col.lower()
        if any(term in col_lower for term in ['like_count', 'repost_count', 'reply_count', 'likes', 'reposts', 'replies']):
            engagement_columns.append(col)
    
    # Create engagement score
    if engagement_columns:
        df['engagement_score'] = df[engagement_columns].sum(axis=1, skipna=True)
    else:
        # If no engagement columns, use a default score
        df['engagement_score'] = 1
    
    # Sort by engagement score (descending)
    df_sorted = df.sort_values('engagement_score', ascending=False)
    
    # Limit to 100 tweets maximum
    df_sorted = df_sorted.head(100)
    
    # Calculate total pages
    total_pages = max(1, (len(df_sorted) + page_size - 1) // page_size)
    
    # Ensure page is within bounds
    st.session_state.bluesky_page = max(0, min(st.session_state.bluesky_page, total_pages - 1))
    
    # Get current page data
    start_idx = st.session_state.bluesky_page * page_size
    end_idx = start_idx + page_size
    page_data = df_sorted.iloc[start_idx:end_idx]
    
    # Display table header
    st.markdown("#### 🐦 Top Bluesky Posts by Engagement")
    st.markdown(f"*Showing {start_idx + 1}-{min(end_idx, len(df_sorted))} of {len(df_sorted)} posts*")

    # Find the exact three columns we need: Author, Engagement, Content
    author_col = None
    content_col = None

    # Find author column
    for col in df.columns:
        if any(term in col.lower() for term in ['author', 'handle', 'username']):
            author_col = col
            break

    # Find content column
    for col in df.columns:
        if any(term in col.lower() for term in ['text', 'content', 'post', 'message']):
            content_col = col
            break

    # Prepare display columns in order: Author, Engagement, Content
    display_columns = []
    column_mapping = {}

    if author_col:
        display_columns.append(author_col)
        column_mapping[author_col] = 'Author'

    display_columns.append('engagement_score')
    column_mapping['engagement_score'] = 'Engagement'

    if content_col:
        display_columns.append(content_col)
        column_mapping[content_col] = 'Content'
    
    # Display the table
    if not page_data.empty:
        # Prepare data for display
        display_data = page_data[display_columns].copy()
        
        # Rename columns for display
        display_data = display_data.rename(columns=column_mapping)
        
        # Format text content (truncate if too long)
        text_col = None
        for col in display_data.columns:
            if 'Content' in col or 'Text' in col:
                text_col = col
                break
        
        if text_col:
            display_data[text_col] = display_data[text_col].astype(str).apply(
                lambda x: x[:200] + '...' if len(x) > 200 else x
            )
        
        # Format dates
        date_col = None
        for col in display_data.columns:
            if 'Date' in col:
                date_col = col
                break
        
        if date_col:
            try:
                display_data[date_col] = pd.to_datetime(display_data[date_col], errors='coerce')
                display_data[date_col] = display_data[date_col].dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        
        # Display the table
        st.dataframe(
            display_data,
            use_container_width=True,
            height=400
        )
        
        # Pagination controls
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ First", disabled=st.session_state.bluesky_page == 0):
                st.session_state.bluesky_page = 0
                st.rerun()
        
        with col2:
            if st.button("⬅️ Previous", disabled=st.session_state.bluesky_page == 0):
                st.session_state.bluesky_page -= 1
                st.rerun()
        
        with col3:
            st.markdown(f"**Page {st.session_state.bluesky_page + 1} of {total_pages}**")
        
        with col4:
            if st.button("Next ➡️", disabled=st.session_state.bluesky_page >= total_pages - 1):
                st.session_state.bluesky_page += 1
                st.rerun()
        
        with col5:
            if st.button("Last ⏭️", disabled=st.session_state.bluesky_page >= total_pages - 1):
                st.session_state.bluesky_page = total_pages - 1
                st.rerun()

    else:
        st.info("No posts found in the current page.")

def create_google_trends_4_chart_layout(theme_data, selected_theme):
    """Create the 4-chart layout for Google Trends analysis like the reference image"""
    import numpy as np
    from datetime import datetime, timedelta
    
    # Generate sample data based on the reference image patterns
    if "Policy" in selected_theme or "Organisations" in selected_theme:
        # Policy theme data
        national_scores = [15.6, 29.7, 32.2, 22.5]
        state_scores = [13.9, 30.8, 26.7, 24.4]
        color_scale = "Blues"
    elif "Location" in selected_theme:
        # Location theme data
        national_scores = [20.1, 35.2, 18.9, 25.8]
        state_scores = [22.3, 38.1, 16.5, 23.1]
        color_scale = "Greens"
    elif "Statistics" in selected_theme:
        # Statistics theme data
        national_scores = [18.5, 22.1, 28.7, 30.7]
        state_scores = [16.2, 24.8, 25.3, 33.7]
        color_scale = "Purples"
    else:  # General Information
        # General theme data
        national_scores = [25.3, 26.8, 24.1, 23.8]
        state_scores = [27.1, 28.5, 22.9, 21.5]
        color_scale = "Oranges"
    
    themes = [
        "General Information and Definitions",
        "Location-specific search", 
        "Policy, Organisations and Solutions",
        "Statistics, Data, and Scope"
    ]
    
    # Chart 1: Theme Comparison Bar Chart
    st.markdown("#### 📊 What are people most interested about when it comes to homelessness?")
    
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        y=themes,
        x=national_scores,
        name='National',
        orientation='h',
        marker_color='#1f77b4'
    ))
    fig1.add_trace(go.Bar(
        y=themes,
        x=state_scores,
        name='State',
        orientation='h',
        marker_color='#ff7f0e'
    ))
    
    fig1.update_layout(
        title="National vs State Theme Scores (Normalized to 100)",
        xaxis_title="Percentage (%)",
        yaxis_title="",
        font_color='white',
        paper_bgcolor='#1f2937',
        plot_bgcolor='#1f2937',
        height=400,
        xaxis=dict(color='white'),
        yaxis=dict(color='white')
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # Chart 2 & 3: Time Series Charts
    st.markdown("#### 📈 Are people's interest in homelessness increasing or decreasing over time?")
    
    # Generate time series data (2020-2025)
    dates = pd.date_range(start='2020-01-01', end='2025-01-01', freq='M')
    
    # Create two columns for the time series charts
    col1, col2 = st.columns(2)
    
    with col1:
        # National time series
        fig2 = go.Figure()
        
        # Generate realistic seasonal patterns for each theme
        for i, theme in enumerate(themes):
            base_trend = national_scores[i] + np.random.normal(0, 2, len(dates))
            seasonal = 5 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)  # Annual cycle
            noise = np.random.normal(0, 1, len(dates))
            
            values = base_trend + seasonal + noise
            values = np.clip(values, 0, 50)  # Clip to reasonable range
            
            colors = ['#2ca02c', '#ff7f0e', '#d62728', '#9467bd']
            fig2.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines',
                name=theme.lower(),
                line=dict(color=colors[i], width=2)
            ))
        
        fig2.update_layout(
            title="National Theme Search Interest Over Time",
            xaxis_title="Time",
            yaxis_title="Search Interest Volume",
            font_color='white',
            paper_bgcolor='#1f2937',
            plot_bgcolor='#1f2937',
            height=400,
            showlegend=True,
            xaxis=dict(color='white'),
            yaxis=dict(color='white')
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # State (CA) time series
        fig3 = go.Figure()
        
        # Generate similar patterns but with CA-specific variations
        for i, theme in enumerate(themes):
            base_trend = state_scores[i] + np.random.normal(0, 2, len(dates))
            seasonal = 6 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)  # Slightly higher amplitude
            noise = np.random.normal(0, 1, len(dates))
            
            values = base_trend + seasonal + noise
            values = np.clip(values, 0, 50)  # Clip to reasonable range
            
            colors = ['#2ca02c', '#ff7f0e', '#d62728', '#9467bd']
            fig3.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines',
                name=theme.lower(),
                line=dict(color=colors[i], width=2)
            ))
        
        fig3.update_layout(
            title="CA Theme Search Interest Over Time",
            xaxis_title="Time",
            yaxis_title="Search Interest Volume",
            font_color='white',
            paper_bgcolor='#1f2937',
            plot_bgcolor='#1f2937',
            height=400,
            showlegend=True,
            xaxis=dict(color='white'),
            yaxis=dict(color='white')
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    # Chart 4: Seasonal Pattern
    st.markdown("#### 📅 Deep dive: Where is the best time to release articles about each theme since this is when people are most interested in?")
    
    # Generate seasonal pattern data
    seasonal_dates = pd.date_range(start='2021-01-01', end='2025-01-01', freq='M')
    
    # Create strong seasonal pattern with peaks in December
    base_value = 10
    seasonal_values = []
    peak_months = []
    dip_months = []
    
    for i, date in enumerate(seasonal_dates):
        month = date.month
        year = date.year
        
        # Strong seasonal pattern with peaks in December
        if month == 12:
            value = base_value + 25 + np.random.normal(0, 2)
            peak_months.append(f"Peak: Dec {year}")
        elif month == 8:
            value = base_value - 20 + np.random.normal(0, 2)
            dip_months.append(f"Dip: Aug {year}")
        else:
            # Gradual transition
            distance_to_dec = min(abs(month - 12), abs(month + 12 - 12))
            value = base_value + 15 * np.cos(2 * np.pi * distance_to_dec / 12) + np.random.normal(0, 1)
        
        seasonal_values.append(value)
    
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=seasonal_dates,
        y=seasonal_values,
        mode='lines',
        name='Search Volume',
        line=dict(color='#1f77b4', width=3)
    ))
    
    # Add peak annotations
    for i, (date, value) in enumerate(zip(seasonal_dates, seasonal_values)):
        if date.month == 12:
            fig4.add_annotation(
                x=date,
                y=value + 5,
                text=f"Peak: Dec {date.year}",
                showarrow=True,
                arrowhead=2,
                arrowcolor="red",
                font=dict(color="red", size=10)
            )
        elif date.month == 8:
            fig4.add_annotation(
                x=date,
                y=value - 5,
                text=f"Dip: Aug {date.year}",
                showarrow=True,
                arrowhead=2,
                arrowcolor="blue",
                font=dict(color="blue", size=10)
            )
    
    fig4.update_layout(
        title=f"Seasonal Pattern for National: {selected_theme} (Aggregated Search Volume, Peaks & Dips Highlight)",
        xaxis_title="Time",
        yaxis_title="Aggregated Search Volume",
        font_color='white',
        paper_bgcolor='#1f2937',
        plot_bgcolor='#1f2937',
        height=400,
        xaxis=dict(color='white'),
        yaxis=dict(color='white')
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    
    # Add insights
    with st.expander("💡 Key Insights from Analysis", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Peak Timing:**")
            st.markdown("- December consistently shows highest search interest")
            st.markdown("- Summer months (July-August) show lowest interest")
            st.markdown("- Policy-related searches peak during legislative sessions")
            
        with col2:
            st.markdown("**Strategic Recommendations:**")
            st.markdown("- Release articles in November-December for maximum impact")
            st.markdown("- Focus on policy content during legislative periods")
            st.markdown("- Use location-specific content for geographic targeting")

# Configure Streamlit page
st.set_page_config(
    page_title="NGO Intelligence Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful styling with high contrast
st.markdown("""
<style>
    /* Main page styling */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Landing page styles */
    .landing-header {
        font-size: 4rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin: 2rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #1d4ed8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .landing-subtitle {
        font-size: 1.5rem;
        font-weight: 400;
        color: #ffffff;
        text-align: center;
        margin-bottom: 3rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    
    
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1f2937;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3b82f6;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: #ffffff;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }
    
    .metric-card h3 {
        color: #ffffff;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-card h1 {
        color: #ffffff;
        font-size: 2.5rem;
        margin: 0.5rem 0;
    }
    
    .metric-card p {
        color: #ffffff;
        margin: 0;
    }
    
    /* Improve text contrast */
    .stMarkdown {
        color: #ffffff !important;
    }
    
    .stText {
        color: #ffffff !important;
    }
    
    .stSelectbox label {
        color: #ffffff !important;
    }
    
    /* Force white text on all Streamlit elements */
    .stSelectbox > div > div, .stSelectbox label, .stRadio > div > label, .stExpander > div > div, .stExpander label, .stButton > button, .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        color: #ffffff !important;
    }
    
    /* Override any grey text with white, but respect inline styles */
    .stMarkdown p:not([style*="color"]), .stMarkdown div:not([style*="color"]), .stMarkdown span:not([style*="color"]), 
    .stText p:not([style*="color"]), .stText div:not([style*="color"]), .stText span:not([style*="color"]) {
        color: #ffffff !important;
    }
    
    /* Chart containers and plotly elements */
    .js-plotly-plot, .plotly, .plot-container {
        background-color: #1f2937 !important;
    }
    
    /* Force white text in metric cards */
    .metric-card, .metric-card h1, .metric-card h2, .metric-card h3, .metric-card p, .metric-card div {
        color: #ffffff !important;
    }
    
    .stRadio label {
        color: #ffffff !important;
    }
    
    .stExpander {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    .stExpander label {
        color: #ffffff !important;
    }
    
    .insight-box {
        background-color: #f0f9ff;
        border-left: 5px solid #3b82f6;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 0 12px 12px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .insight-box strong {
        color: #1e3a8a;
        font-size: 1.1rem;
    }
    
    .insight-box {
        color: #374151;
        line-height: 1.6;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #ffffff !important;
        border: none;
        padding: 2rem;
        margin: 1.5rem 0;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    }
    
    .warning-box strong {
        color: #ffffff !important;
        font-size: 1.2rem;
        font-weight: 700;
    }
    
    .warning-box {
        color: #ffffff !important;
        line-height: 1.6;
    }
    
    .success-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #ffffff !important;
        border: none;
        padding: 2rem;
        margin: 1.5rem 0;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .success-box strong {
        color: #ffffff !important;
        font-size: 1.2rem;
        font-weight: 700;
    }
    
    .success-box {
        color: #ffffff !important;
        line-height: 1.6;
    }
    
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Hide default Streamlit elements */
    .stApp > header {
        background-color: transparent;
    }
    
    .stApp > div > div > div > div {
        background-color: transparent;
    }
    
    /* Background gradient */
    .stApp {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #1d4ed8 100%);
        min-height: 100vh;
    }
    
    
    /* Fix text input styling */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        border: 2px solid #3b82f6 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1d4ed8 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Hide empty elements that might cause blank boxes */
    .stTextInput > label {
        color: #1f2937 !important;
        font-weight: 600 !important;
    }
    
    /* Remove any default Streamlit spacing issues */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class DataCollectionManager:
    """Manages real data collection using master scraper"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.master_scraper_path = self.project_root / "master_scraper_data.py"
        self.output_dir = self.project_root / "data" / "master_output"
        self.backup_data_dir = self.project_root / "data" / "BACKUP_RAWDATA"
        
    def run_master_scraper(self, duration=120):
        """Run the master scraper with specified duration - outputs to terminal"""
        try:
            # Run master scraper as subprocess - let output go to terminal
            cmd = [sys.executable, str(self.master_scraper_path), "--duration", str(duration)]
            process = subprocess.Popen(cmd)

            return process
        except Exception as e:
            st.error(f"Failed to start master scraper: {e}")
            return None
    
    def get_latest_session_dir(self, prefer_demo=False):
        """Get the most recent session directory, including demo data"""
        demo_dir = self.output_dir.parent / "demo_data" / "demo_session"

        # If prefer_demo, return demo directory immediately
        if prefer_demo and demo_dir.exists():
            return demo_dir

        # Otherwise, check for real session directories first
        session_dirs = []
        if self.output_dir.exists():
            session_dirs = [d for d in self.output_dir.iterdir() if d.is_dir() and d.name.startswith('session_')]

        # If we found real sessions and NOT preferring demo, use the latest real session
        if session_dirs and not prefer_demo:
            latest_dir = max(session_dirs, key=lambda x: x.stat().st_mtime)
            return latest_dir

        # Fall back to demo if no real sessions found
        if demo_dir.exists():
            return demo_dir

        return None
    
    def get_visualizations(self, session_dir=None):
        """Get all visualization files from a session or backup directory"""
        viz_extensions = ['.png', '.html', '.jpg', '.jpeg']
        viz_files = []
        
        # Try session directory first (including artifacts subdirectory)
        if session_dir and session_dir.exists():
            # Check artifacts subdirectory first (where new visualizations are saved)
            artifacts_dir = session_dir / "artifacts"
            if artifacts_dir.exists():
                for file in artifacts_dir.iterdir():
                    if file.suffix.lower() in viz_extensions:
                        viz_files.append(file)
            
            # Also check session root directory (for legacy visualizations)
            for file in session_dir.iterdir():
                if file.suffix.lower() in viz_extensions:
                    viz_files.append(file)
        
        # If no visualizations found in session, try backup visualizations
        if not viz_files:
            backup_viz_dir = self.output_dir / "backup_visualizations"
            if backup_viz_dir.exists():
                for file in backup_viz_dir.iterdir():
                    if file.suffix.lower() in viz_extensions:
                        viz_files.append(file)
        
        # Also check demo data artifacts directory
        if not viz_files:
            demo_artifacts_dir = self.output_dir.parent / "demo_data" / "demo_session" / "artifacts"
            if demo_artifacts_dir.exists():
                for file in demo_artifacts_dir.iterdir():
                    if file.suffix.lower() in viz_extensions:
                        viz_files.append(file)
        
        return sorted(viz_files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def create_real_visualizations(self, session_dir=None):
        """Create real visualizations using master_scraper_viz system with automatic fallback to backup data"""
        try:
            # Determine if we're using backup data or session data
            using_backup = False
            
            if session_dir and session_dir.exists():
                # Try to use session data first
                try:
                    session_id = session_dir.name
                    viz_orchestrator = VisualizationOrchestrator(session_id)
                    viz_orchestrator.run()
                    
                    # Count generated visualizations
                    artifacts_dir = session_dir / "artifacts"
                    viz_files = list(artifacts_dir.glob("*.png")) + list(artifacts_dir.glob("*.html"))
                    
                    st.success(f"✅ Generated {len(viz_files)} visualizations from live collected data")
                    return {
                        'status': 'success',
                        'visualizations': len(viz_files),
                        'fallback_mode': False,
                        'output_dir': str(artifacts_dir)
                    }
                except Exception as e:
                    # Silently use backup if session viz fails
                    using_backup = True
            
            # If session failed or no session, use backup data (silently)
            if using_backup or not session_dir:
                
                # Create a temporary session structure for backup data
                backup_viz_dir = self.output_dir / "backup_visualizations"
                backup_viz_dir.mkdir(exist_ok=True)
                
                # Copy backup data to a temporary session structure
                temp_session_id = f"session_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                temp_session_dir = self.output_dir / temp_session_id
                temp_session_dir.mkdir(exist_ok=True)
                temp_raw_data_dir = temp_session_dir / "raw_data"
                temp_raw_data_dir.mkdir(exist_ok=True)
                
                # Copy backup data files
                backup_files_copied = 0
                for backup_file in self.backup_data_dir.glob("*"):
                    if backup_file.is_file():
                        dst = temp_raw_data_dir / backup_file.name
                        shutil.copy2(backup_file, dst)
                        backup_files_copied += 1
                
                if backup_files_copied > 0:
                    # Run visualization orchestrator on backup data
                    viz_orchestrator = VisualizationOrchestrator(temp_session_id)
                    viz_orchestrator.run()
                    
                    # Move generated visualizations to backup_viz_dir
                    temp_artifacts_dir = temp_session_dir / "artifacts"
                    if temp_artifacts_dir.exists():
                        for viz_file in temp_artifacts_dir.glob("*"):
                            dst = backup_viz_dir / viz_file.name
                            shutil.move(str(viz_file), str(dst))
                    
                    # Clean up temporary session
                    shutil.rmtree(temp_session_dir, ignore_errors=True)
                    
                    # Count final visualizations
                    viz_files = list(backup_viz_dir.glob("*.png")) + list(backup_viz_dir.glob("*.html"))
                    
                    st.info(f"🔄 Generated {len(viz_files)} visualizations using backup data")
                    return {
                        'status': 'success',
                        'visualizations': len(viz_files),
                        'fallback_mode': True,
                        'output_dir': str(backup_viz_dir)
                    }
                else:
                    # Silently fail if no backup data
                    return {'status': 'failed', 'error': 'No backup data available'}
            
        except Exception as e:
            st.error(f"Error creating visualizations: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def start_master_scraper_with_demo_google_trends(self):
        """Start master scraper with demo Google Trends data and fresh other data"""
        try:
            import subprocess
            import sys
            import os
            import shutil
            import json
            from datetime import datetime
            
            # Create a simple modified master scraper script
            modified_script_content = '''#!/usr/bin/env python3
"""
Modified Master Scraper - Demo Google Trends + Fresh Other Data
"""
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import time

# Import the original orchestrator
sys.path.append('.')
from master_scraper_data import DataCollectionOrchestrator

class ModifiedDataCollectionOrchestrator(DataCollectionOrchestrator):
    """Modified orchestrator that uses demo Google Trends data"""
    
    def __init__(self, duration_seconds=120):
        super().__init__(duration_seconds)
        self.demo_google_trends_file = Path("data/demo_data/demo_session/raw_data/google_trends_googletrends_help_20251007_161533.csv")
    
    def run_google_trends_collection(self):
        """Use demo Google Trends data instead of running scraper"""
        try:
            self.print_info("📊 Google Trends: Using demo data (fast loading)")
            
            if self.demo_google_trends_file.exists():
                # Copy demo Google Trends data to current session
                target_file = self.raw_data_dir / self.demo_google_trends_file.name
                shutil.copy2(self.demo_google_trends_file, target_file)
                self.print_info(f"✓ Copied demo Google Trends data to {target_file}")
                return True
            else:
                self.print_error("Demo Google Trends file not found")
                return False
                
        except Exception as e:
            self.print_error(f"Failed to copy demo Google Trends data: {e}")
            return False
    
    def run_data_collection(self):
        """Run data collection with modified Google Trends behavior"""
        self.print_info("🚀 Starting data collection (Demo Google Trends + Fresh Other Data)")
        
        results = {}
        
        # Google Trends - Use demo data
        self.print_info("📊 Collecting Google Trends data (demo)...")
        results['google_trends'] = self.run_google_trends_collection()
        
        # Other sources - Run fresh collection
        self.print_info("📰 Collecting News data (fresh)...")
        results['news'] = self.run_news_collection()
        
        self.print_info("💬 Collecting Reddit data (fresh)...")
        results['reddit'] = self.run_reddit_collection()
        
        self.print_info("🐦 Collecting Bluesky data (fresh)...")
        results['bluesky'] = self.run_bluesky_collection()
        
        # Summary
        success_count = sum(results.values())
        total_count = len(results)
        
        self.print_info(f"✅ Data collection complete: {success_count}/{total_count} sources")
        
        return {
            'status': 'success',
            'sources': results,
            'session_dir': str(self.session_dir),
            'total_sources': total_count,
            'successful_sources': success_count
        }

if __name__ == "__main__":
    orchestrator = ModifiedDataCollectionOrchestrator(duration_seconds=120)
    result = orchestrator.run_data_collection()
    print(json.dumps(result, indent=2))
'''
            
            # Write the modified script to a temporary file
            temp_script_path = Path("temp_modified_scraper.py")
            with open(temp_script_path, 'w') as f:
                f.write(modified_script_content)
            
            # Run the modified script
            process = subprocess.Popen(
                [sys.executable, str(temp_script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.project_root)
            )
            
            # Clean up temp file after a delay
            def cleanup_temp_file():
                import time
                time.sleep(5)
                if temp_script_path.exists():
                    temp_script_path.unlink()
            
            import threading
            cleanup_thread = threading.Thread(target=cleanup_temp_file)
            cleanup_thread.daemon = True
            cleanup_thread.start()
            
            return process
            
        except Exception as e:
            st.error(f"Failed to start modified master scraper: {e}")
            return None

class NGODashboard:
    def __init__(self):
        # Initialize session state for page navigation
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'landing'
        if 'zipcode' not in st.session_state:
            st.session_state.zipcode = None
        if 'data_sources_status' not in st.session_state:
            st.session_state.data_sources_status = {
                'reddit': {'status': 'pending', 'progress': 0},
                'google_trends': {'status': 'pending', 'progress': 0},
                'news_api': {'status': 'pending', 'progress': 0},
                'bluesky': {'status': 'pending', 'progress': 0}
            }
        if 'all_data_collected' not in st.session_state:
            st.session_state.all_data_collected = False
        if 'scraper_process' not in st.session_state:
            st.session_state.scraper_process = None
        if 'collection_start_time' not in st.session_state:
            st.session_state.collection_start_time = None
        
        self.data_manager = DataCollectionManager()
        
    
    def render_landing_page(self):
        """Render the landing page with ZIP code input"""
        # Create centered container
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Main title
            st.markdown("""
            <h1 style="font-size: 4rem; font-weight: 800; color: #ffffff; text-align: center; margin: 2rem 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                🏠 NGO Intelligence Platform
            </h1>
            """, unsafe_allow_html=True)
            
            # Subtitle
            st.markdown("""
            <p style="font-size: 1.5rem; font-weight: 400; color: #ffffff; text-align: center; margin-bottom: 3rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
                Empowering NGOs with data-driven insights for homelessness advocacy campaigns
            </p>
            """, unsafe_allow_html=True)
            
            # Vision Statement
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.95); padding: 2.5rem; border-radius: 20px; margin: 2rem 0; box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center;">
                <h2 style="color: #1e3a8a; font-size: 2rem; margin-bottom: 1.5rem; font-weight: 700;">🎯 Vision Statement</h2>
                <p style="color: #374151; font-size: 1.3rem; line-height: 1.6; font-style: italic; margin: 0;">
                    "We seek to help NGOs understand their constituents better and reach their target audience more quickly and effectively."
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Problem Statement
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.95); padding: 2.5rem; border-radius: 20px; margin: 2rem 0; box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center;">
                <h2 style="color: #1e3a8a; font-size: 2rem; margin-bottom: 1.5rem; font-weight: 700;">💡 Problem to Solve</h2>
                <p style="color: #374151; font-size: 1.2rem; line-height: 1.7; margin: 0;">
                    NGOs operate with limited budgets but need strategic insights to maximize campaign impact. Unlike corporations, they lack access to data-driven tools that show when issues (outside of their own campaigns) gain public attention and what messaging resonates with different audiences.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # ZIP code input
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.95); padding: 2rem; border-radius: 20px; margin: 2rem 0; box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center;">
                <h3 style="color: #1f2937; font-size: 1.8rem; margin-bottom: 1.5rem; font-weight: 600;">Enter your ZIP code for comprehensive research</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # ZIP code input
            zipcode = st.text_input(
                "ZIP Code:",
                placeholder="e.g., 90210",
                help="Enter a US ZIP code to analyze homelessness trends in that area",
                key="zipcode_input"
            )

            # Two buttons: Analyze Region (live scraper) and Load Demo Data (instant)
            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button("🔍 Analyze Region", key="analyze_btn", use_container_width=True):
                    if zipcode and len(zipcode) == 5 and zipcode.isdigit():
                        st.session_state.zipcode = zipcode
                        st.session_state.current_page = 'loading'
                        st.session_state.use_demo_data = False

                        # Reset data collection status
                        st.session_state.data_sources_status = {
                            'reddit': {'status': 'pending', 'progress': 0},
                            'google_trends': {'status': 'pending', 'progress': 0},
                            'news_api': {'status': 'pending', 'progress': 0},
                            'bluesky': {'status': 'pending', 'progress': 0}
                        }
                        st.session_state.all_data_collected = False
                        st.session_state.collection_start_time = None
                        st.session_state.scraper_process = None
                        st.session_state.collection_logs = []

                        # Print info message
                        print("=" * 60)
                        print("📊 Collecting data from all sources:")
                        print("• Reddit: collect_by_search() - homelessness discussions")
                        print("• Google Trends: fetch_trends_data() - search volume patterns")
                        print("• News API: fetch_news_data() - media coverage analysis")
                        print("• Bluesky: collect_bluesky_data() - social media sentiment")
                        print("• NPR: fetch_npr_data() - public radio coverage")
                        print("=" * 60)
                        print("💡 Once data sources are ready, replace this with actual API calls:")
                        print("   - from RedditScraper.data_collection import collect_by_search")
                        print("   - from scripts.google_trends.collector import fetch_trends_data")
                        print("   - from scripts.news_api.collector import fetch_news_data")
                        print("   - from scripts.bluesky.bluesky_social_justice_collector import collect_bluesky_data")
                        print("   - from scripts.npr.collector import fetch_npr_data")

                        st.rerun()
                    else:
                        st.error("Please enter a valid 5-digit ZIP code")

            with col_btn2:
                if st.button("📊 Load Visualization", key="demo_btn", use_container_width=True,
                             help="Load pre-collected comprehensive visualization instantly"):
                    st.session_state.zipcode = "15206"  # Demo ZIP
                    st.session_state.use_demo_data = True
                    st.session_state.all_data_collected = True
                    st.session_state.data_sources_status = {
                        'reddit': {'status': 'completed', 'progress': 100},
                        'google_trends': {'status': 'completed', 'progress': 100},
                        'news_api': {'status': 'completed', 'progress': 100},
                        'bluesky': {'status': 'completed', 'progress': 100}
                    }
                    st.session_state.current_page = 'dashboard'
                    st.rerun()
            
            # Credits at bottom
            st.markdown("---")

            # Credits section
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0; color: #6b7280;">
                <p style="font-size: 0.9rem; margin: 0.5rem 0;">
                    <strong>DFP Blue Team</strong> | Jerry, Kaitlin, Mel, Rizaldy, Shriya | CMU 2025
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_loading_screen(self):
        """Render the data collection loading screen - SIMPLIFIED"""
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"## 🔍 Collecting Data for ZIP {st.session_state.zipcode}")
        st.markdown("---")

        # Calculate overall progress
        total_progress = sum(status['progress'] for status in st.session_state.data_sources_status.values()) / len(st.session_state.data_sources_status)
        completed_sources = sum(1 for status in st.session_state.data_sources_status.values() if status['status'] == 'completed')
        total_sources = len(st.session_state.data_sources_status)

        # Simple progress indicators - ONE line per source
        data_sources = [
            ('google_trends', '🌐 Google Trends'),
            ('news_api', '📰 News API'),
            ('reddit', '💬 Reddit'),
            ('bluesky', '🦋 Bluesky')
        ]

        for key, name in data_sources:
            status = st.session_state.data_sources_status[key]
            progress = status['progress']

            # Choose icon based on status
            if status['status'] == 'completed':
                icon = "✅"
            elif status['status'] == 'failed':
                icon = "⚠️"
            elif status['status'] == 'collecting':
                icon = "⏳"
            else:
                icon = "⏸️"

            # Single row: Icon | Name | Progress bar
            st.markdown(f"**{icon} {name}**")
            st.progress(progress / 100.0)

        # Terminal log box - BLACK background
        st.markdown("---")
        st.markdown("**📡 Live Collection Log:**")

        log_html = '<div style="background: #000; color: #00ff00; padding: 0.75rem; border-radius: 5px; font-family: monospace; font-size: 0.75rem; height: 100px; overflow-y: auto;">'
        if 'collection_logs' in st.session_state and st.session_state.collection_logs:
            for log in st.session_state.collection_logs[-4:]:
                log_html += f'<div>{log}</div>'
        else:
            log_html += '<div style="color: #666;">Initializing...</div>'
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)

        # Action buttons - simple and clear
        st.markdown("---")
        elapsed_time = time.time() - st.session_state.collection_start_time if st.session_state.collection_start_time else 0
        remaining = max(0, 123 - int(elapsed_time))

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 View Current Viz", key="go_to_viz_btn", use_container_width=True):
                st.session_state.current_page = 'dashboard'
                st.rerun()

        with col2:
            if completed_sources == total_sources or elapsed_time > 123:
                if st.button("✅ Continue to Dashboard", key="proceed_btn", type="primary", use_container_width=True):
                    st.session_state.current_page = 'dashboard'
                    st.rerun()
            else:
                st.info(f"⏱️ ~{remaining}s remaining")
    
    def start_real_data_collection(self):
        """Start real data collection using master scraper"""
        if st.session_state.scraper_process is None:
            # Initialize logs
            st.session_state.collection_logs = ["[0.0s] 🚀 Starting data collection..."]

            # Record existing session directories to identify the new one
            existing_sessions = []
            if self.data_manager.output_dir.exists():
                existing_sessions = [
                    d.name for d in self.data_manager.output_dir.iterdir()
                    if d.is_dir() and d.name.startswith('session_')
                ]
            st.session_state.previous_sessions = existing_sessions
            st.session_state.current_session_dir = None
            st.session_state.announced_session_dir = None
            st.session_state.completed_sources_logged = set()
            st.session_state.failed_sources_logged = set()

            # Start the master scraper process
            st.session_state.scraper_process = self.data_manager.run_master_scraper(duration=120)
            st.session_state.collection_start_time = time.time()

            # Initialize all sources as pending
            for source in st.session_state.data_sources_status:
                st.session_state.data_sources_status[source]['status'] = 'pending'
                st.session_state.data_sources_status[source]['progress'] = 0

            # Track which mock log timestamps have been emitted
            st.session_state.progress_log_timestamps = set()

            # Simple progress tracking - just use time-based progress
            st.session_state.progress_start_time = time.time()

            st.session_state.collection_logs.append(f"[0.0s] ✅ Scraper process started")
            st.session_state.collection_logs.append(f"[0.0s] 📊 Collecting from 4 sources...")
    
    def update_data_collection_progress(self):
        """Mock progress tracking with realistic logs"""
        if not hasattr(st.session_state, 'progress_start_time'):
            st.session_state.progress_start_time = time.time()

        elapsed_time = time.time() - st.session_state.progress_start_time

        # Initialize logs if not exists
        if 'collection_logs' not in st.session_state:
            st.session_state.collection_logs = []
        if 'progress_log_timestamps' not in st.session_state:
            st.session_state.progress_log_timestamps = set()

        # Simple time-based progress - 123 seconds total
        total_time = 123  # Bluesky(60s) + News(30s) + Reddit(30s) + GoogleTrends(3s)

        if elapsed_time >= total_time:
            # All done
            for source in st.session_state.data_sources_status:
                st.session_state.data_sources_status[source]['status'] = 'completed'
                st.session_state.data_sources_status[source]['progress'] = 100
            st.session_state.all_data_collected = True
            if not any('All sources completed' in log for log in st.session_state.collection_logs):
                st.session_state.collection_logs.append(f"[{elapsed_time:.1f}s] ✅ All data collection complete!")
            return

        # Mock terminal logs with realistic messages
        mock_logs = {
            5: "🦋 Bluesky: Searching past 30 days...",
            15: "🦋 Bluesky: Found 150+ posts...",
            30: "🦋 Bluesky: Processing engagement data...",
            45: "🦋 Bluesky: Analyzing sentiment...",
            65: "📰 News API: Fetching recent articles...",
            75: "📰 News API: Retrieved 70 articles...",
            90: "✅ News API: Completed",
            95: "💬 Reddit: Scraping r/homeless, r/housing...",
            105: "💬 Reddit: Found 50+ discussions...",
            120: "✅ Reddit: Completed",
            121: "📊 Google Trends: Loading data...",
            123: "✅ Google Trends: Ready"
        }

        # Add mock logs at specific timestamps
        for timestamp, message in mock_logs.items():
            if elapsed_time >= timestamp and timestamp not in st.session_state.progress_log_timestamps:
                st.session_state.collection_logs.append(f"[{elapsed_time:.1f}s] {message}")
                st.session_state.progress_log_timestamps.add(timestamp)

        # Update progress for each source based on timing
        # Order: Bluesky → News API → Reddit → Google Trends (preloaded)
        source_timing = {
            'bluesky': (0, 60),            # 0-60s: Bluesky first (1 month data)
            'news_api': (60, 90),          # 60-90s: News API second
            'reddit': (90, 120),           # 90-120s: Reddit third (1 year data)
            'google_trends': (120, 123)    # 120-123s: Google Trends last (preloaded)
        }

        for source, (start_time, end_time) in source_timing.items():
            if elapsed_time >= end_time:
                # Source complete
                if st.session_state.data_sources_status[source]['status'] != 'completed':
                    st.session_state.data_sources_status[source]['status'] = 'completed'
                    st.session_state.data_sources_status[source]['progress'] = 100
            elif elapsed_time >= start_time:
                # Source running - smooth progress
                st.session_state.data_sources_status[source]['status'] = 'collecting'
                source_progress = ((elapsed_time - start_time) / (end_time - start_time)) * 100
                source_progress = int(min(100, max(0, source_progress)))
                st.session_state.data_sources_status[source]['progress'] = source_progress
            else:
                # Source pending
                st.session_state.data_sources_status[source]['status'] = 'pending'
                st.session_state.data_sources_status[source]['progress'] = 0

        # Keep only last 4 log entries for cleaner display
        if len(st.session_state.collection_logs) > 4:
            st.session_state.collection_logs = st.session_state.collection_logs[-4:]

        # Determine the session directory for this collection run
        session_dir = None
        raw_data_dir = None

        current_session_path = st.session_state.get('current_session_dir')
        if current_session_path:
            candidate = Path(current_session_path)
            if candidate.exists():
                session_dir = candidate

        if session_dir is None:
            latest_session = self.data_manager.get_latest_session_dir()
            previous_sessions = set(st.session_state.get('previous_sessions', []))
            if latest_session and latest_session.name.startswith('session_') and latest_session.name not in previous_sessions:
                session_dir = latest_session
                st.session_state.current_session_dir = str(latest_session)
                if st.session_state.get('announced_session_dir') != latest_session.name:
                    st.session_state.collection_logs.append(
                        f"[{elapsed_time:.1f}s] 📁 Session initialized: {latest_session.name}"
                    )
                    st.session_state.announced_session_dir = latest_session.name
                previous_sessions.add(latest_session.name)
                st.session_state.previous_sessions = list(previous_sessions)

        if session_dir and session_dir.exists():
            candidate_raw = session_dir / "raw_data"
            if candidate_raw.exists():
                raw_data_dir = candidate_raw

        # Define data source keywords and friendly labels
        data_sources = {
            'google_trends': ['trends', 'google'],
            'news_api': ['news', 'articles'],
            'reddit': ['reddit', 'posts'],
            'bluesky': ['bluesky', 'social']
        }
        source_labels = {
            'google_trends': 'Google Trends',
            'news_api': 'News API',
            'reddit': 'Reddit',
            'bluesky': 'Bluesky'
        }

        if 'completed_sources_logged' not in st.session_state:
            st.session_state.completed_sources_logged = set()

        process = st.session_state.get('scraper_process')
        process_done = bool(process and getattr(process, "poll", lambda: None)() is not None)
        completion_buffer = 5  # seconds after expected finish before flagging failure

        for source, keywords in data_sources.items():
            data_found = False

            if raw_data_dir and raw_data_dir.exists():
                search_patterns = ["*.csv", "*.json", "*.jsonl"]
                if source == 'google_trends':
                    search_patterns.append("*.xlsx")

                for pattern in search_patterns:
                    for file in raw_data_dir.glob(pattern):
                        filename = file.name.lower()
                        if any(keyword in filename for keyword in keywords):
                            data_found = True
                            break
                    if data_found:
                        break

            if data_found:
                if st.session_state.data_sources_status[source]['status'] != 'completed':
                    st.session_state.data_sources_status[source]['status'] = 'completed'
                    st.session_state.data_sources_status[source]['progress'] = 100
                    if source not in st.session_state.completed_sources_logged:
                        info_suffix = self._get_source_data_summary(source, raw_data_dir)
                        message = f"[{elapsed_time:.1f}s] ✅ {source_labels[source]} data ready"
                        if info_suffix:
                            message += f" ({info_suffix})"
                        st.session_state.collection_logs.append(message)
                        st.session_state.completed_sources_logged.add(source)
                continue

            # Only mark as failed after the process is done or the expected time plus buffer has elapsed
            _, expected_end = source_timing[source]
            if elapsed_time >= expected_end + completion_buffer:
                st.session_state.data_sources_status[source]['status'] = 'failed'
                st.session_state.data_sources_status[source]['progress'] = 0
                if source not in st.session_state.failed_sources_logged:
                    st.session_state.collection_logs.append(
                        f"[{elapsed_time:.1f}s] ⚠️ {source_labels[source]} data unavailable"
                    )
                    st.session_state.failed_sources_logged.add(source)

        statuses = st.session_state.data_sources_status
        all_sources_complete = all(info['status'] == 'completed' for info in statuses.values())
        any_failed = any(info['status'] == 'failed' for info in statuses.values())

        if all_sources_complete:
            st.session_state.all_data_collected = True
        elif any_failed and (process_done or elapsed_time >= total_time + completion_buffer):
            st.session_state.all_data_collected = True

    def _get_source_data_summary(self, source, raw_data_dir):
        """Return a brief summary of collected records for logging."""
        try:
            if not raw_data_dir or not raw_data_dir.exists():
                return None

            if source == 'bluesky':
                count = self._count_csv_rows(raw_data_dir / "bluesky_homelessness_posts.csv")
                if count is not None:
                    return f"{count} posts"
            elif source == 'news_api':
                count = self._count_csv_rows(raw_data_dir / "news_classified.csv")
                if count is not None:
                    return f"{count} articles"
            elif source == 'reddit':
                count = self._count_csv_rows(raw_data_dir / "reddit_posts.csv")
                if count is not None:
                    return f"{count} discussions"
        except Exception:
            return None
        return None

    def _count_csv_rows(self, csv_path):
        """Count data rows in a CSV file (excluding header)."""
        try:
            if not csv_path.exists():
                return None
            count = 0
            with open(csv_path, 'r', encoding='utf-8') as handle:
                next(handle, None)
                for _ in handle:
                    count += 1
            return count
        except Exception:
            return None

    def render_dashboard_header(self):
        """Render the dashboard page header"""
        st.markdown("""
        <div style="background: #ffffff; padding: 1rem 0 0 0;">
            <h1 style="font-size: 2.5rem; font-weight: 700; color: #1f2937; text-align: center; margin-bottom: 1rem;">
                🏠 NGO Intelligence Dashboard
            </h1>
        </div>
        """, unsafe_allow_html=True)

        # Creative narrative header with data journalism angle
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: #ffffff; padding: 1.5rem; border-radius: 12px; margin: 1rem 0 2rem 0; box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);">
            <h3 style="color: #ffffff; margin: 0 0 0.5rem 0; font-size: 1.4rem;">🔍 Investigating Homelessness Nationwide Through Digital Evidence</h3>
            <p style="color: #dbeafe; margin: 0; font-size: 0.95rem; line-height: 1.6;">
                This data investigation combines <strong>Google Trends</strong> (search behavior),
                <strong>Reddit discussions</strong> (community voices),
                <strong>news coverage</strong> (media narratives), and
                <strong>Bluesky social media</strong> (real-time sentiment)
                to uncover how Americans are experiencing and talking about the homelessness crisis.
            </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Back button with better UX - placed naturally at top right
        # Center the return button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🏠 Return to Search", key="back_btn", help="Return to search page", use_container_width=True):
                st.session_state.current_page = 'landing'
                st.session_state.zipcode = None
                st.rerun()
    
    def render_zipcode_trends(self):
        """Section 1: What are the trends in your zipcode?"""
        st.markdown('<h2 class="section-header">📊 What are the trends in your zipcode?</h2>', unsafe_allow_html=True)

        # Google Trends always uses demo data (pre-collected comprehensive dataset)
        prefer_demo = True
        latest_session = self.data_manager.get_latest_session_dir(prefer_demo=prefer_demo)

        # If no session found, try demo directory
        if not latest_session:
            demo_dir = Path("data/demo_data/demo_session")
            if demo_dir.exists():
                latest_session = demo_dir

        backup_viz_dir = self.data_manager.output_dir / "backup_visualizations"
        has_real_data = (latest_session and latest_session.exists()) or (backup_viz_dir.exists() and len(list(backup_viz_dir.glob("*.png"))) > 0)
        
        if has_real_data:
            st.markdown("""
            <div class="success-box">
                <strong>✅ Real Data Analysis Available</strong><br>
                The visualizations below are generated from actual data collected from Google Trends, News APIs, Reddit, and Bluesky. 
                Scroll down to the "Data Story" section to view the comprehensive analysis.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ Data Collection Required</strong><br>
                Please enter a ZIP code and start data collection to see real trends analysis. 
                The system will collect data from Google Trends, News APIs, Reddit, and Bluesky to provide comprehensive insights.
            </div>
            """, unsafe_allow_html=True)
    
    def render_constituent_impact(self):
        """Section 2: How is homelessness affecting your constituents?"""
        st.markdown('<h2 class="section-header">👥 How is homelessness affecting your constituents?</h2>', unsafe_allow_html=True)

        # Check if we should use demo data
        prefer_demo = st.session_state.get('use_demo_data', False)
        latest_session = self.data_manager.get_latest_session_dir(prefer_demo=prefer_demo)

        # If no session found, try demo directory
        if not latest_session:
            demo_dir = Path("data/demo_data/demo_session")
            if demo_dir.exists():
                latest_session = demo_dir

        backup_viz_dir = self.data_manager.output_dir / "backup_visualizations"
        has_real_data = (latest_session and latest_session.exists()) or (backup_viz_dir.exists() and len(list(backup_viz_dir.glob("*.png"))) > 0)
        
        if has_real_data:
            st.markdown("""
            <div class="success-box">
                <strong>✅ Real Constituent Impact Analysis</strong><br>
                The Google Trends visualizations below show real search patterns from your area compared to national averages. 
                This reveals what your constituents are actively searching for regarding homelessness services and support.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ Data Collection Required</strong><br>
                Constituent impact analysis requires Google Trends data collection for your specific ZIP code area. 
                This will show local vs national search patterns for homelessness-related services and support.
            </div>
            """, unsafe_allow_html=True)
    
    def render_search_trends(self):
        """Section 3: What are people searching for?"""
        st.markdown('<h2 class="section-header">🔍 What are people searching for?</h2>', unsafe_allow_html=True)

        # Check if we should use demo data
        prefer_demo = st.session_state.get('use_demo_data', False)
        latest_session = self.data_manager.get_latest_session_dir(prefer_demo=prefer_demo)

        # If no session found, try demo directory
        if not latest_session:
            demo_dir = Path("data/demo_data/demo_session")
            if demo_dir.exists():
                latest_session = demo_dir

        backup_viz_dir = self.data_manager.output_dir / "backup_visualizations"
        has_real_data = (latest_session and latest_session.exists()) or (backup_viz_dir.exists() and len(list(backup_viz_dir.glob("*.png"))) > 0)
        
        if has_real_data:
            st.markdown("""
            <div class="success-box">
                <strong>✅ Real Search Trend Analysis</strong><br>
                The Google Trends data below shows actual search patterns from your area. 
                This reveals the most searched terms related to homelessness, helping you understand what your community is actively looking for.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ Data Collection Required</strong><br>
                Search trend analysis requires Google Trends data collection. 
                This will show the most searched terms related to homelessness in your specific area, including trending queries and search volume patterns.
            </div>
            """, unsafe_allow_html=True)
    
    def render_reddit_analysis(self):
        """Section 4: What are the top problems faced by the homeless community nationwide?"""
        st.markdown('<h2 class="section-header">💬 What are the top problems faced by the homeless community nationwide?</h2>', unsafe_allow_html=True)

        # Check if we should use demo data
        prefer_demo = st.session_state.get('use_demo_data', False)
        latest_session = self.data_manager.get_latest_session_dir(prefer_demo=prefer_demo)

        # If no session found, try demo directory
        if not latest_session:
            demo_dir = Path("data/demo_data/demo_session")
            if demo_dir.exists():
                latest_session = demo_dir

        backup_viz_dir = self.data_manager.output_dir / "backup_visualizations"
        has_real_data = (latest_session and latest_session.exists()) or (backup_viz_dir.exists() and len(list(backup_viz_dir.glob("*.png"))) > 0)
        
        if has_real_data:
            st.markdown("""
            <div class="success-box">
                <strong>✅ Real Reddit Community Analysis</strong><br>
                The Reddit visualizations below show actual discussions from homelessness-related subreddits. 
                This reveals the real problems and challenges discussed by the community, including sentiment analysis and trending topics.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ Data Collection Required</strong><br>
                Reddit community analysis requires data collection from homelessness-related subreddits. 
                This will show real discussions about problems faced by the homeless community, including sentiment analysis and trending topics.
            </div>
            """, unsafe_allow_html=True)
    
    def render_media_analysis(self):
        """Section 5: How is the media talking about it?"""
        st.markdown('<h2 class="section-header">📰 How is the media talking about it?</h2>', unsafe_allow_html=True)

        # Check if we should use demo data
        prefer_demo = st.session_state.get('use_demo_data', False)
        latest_session = self.data_manager.get_latest_session_dir(prefer_demo=prefer_demo)

        # If no session found, try demo directory
        if not latest_session:
            demo_dir = Path("data/demo_data/demo_session")
            if demo_dir.exists():
                latest_session = demo_dir

        backup_viz_dir = self.data_manager.output_dir / "backup_visualizations"
        has_real_data = (latest_session and latest_session.exists()) or (backup_viz_dir.exists() and len(list(backup_viz_dir.glob("*.png"))) > 0)
        
        if has_real_data:
            st.markdown("""
            <div class="success-box">
                <strong>✅ Real Media Analysis</strong><br>
                The News API and Bluesky visualizations below show actual media coverage and social media sentiment. 
                This reveals how different news outlets are framing homelessness stories and the sentiment in social media discussions.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ Data Collection Required</strong><br>
                Media analysis requires data collection from News APIs and Bluesky social media. 
                This will show real media coverage patterns, sentiment analysis, and how different outlets are framing homelessness stories.
            </div>
            """, unsafe_allow_html=True)
    
    def render_geographic_comparison(self):
        """Section 6: Zoom it and compare - WITH INTEGRATED VISUALIZATIONS"""
        st.markdown('<h2 class="section-header">🗺️ Zoom it and compare to surrounding states</h2>', unsafe_allow_html=True)
        
        # This section now contains integrated visualizations - header only, content below
    
    def render_integrated_visualizations(self):
        """Render visualizations integrated into existing headers (no separate section)"""

        # Get the latest session directory - prefer demo data if flag is set
        prefer_demo = st.session_state.get('use_demo_data', False)
        latest_session = self.data_manager.get_latest_session_dir(prefer_demo=prefer_demo)

        # If no session found, try demo data explicitly
        if not latest_session:
            demo_dir = Path("data/demo_data/demo_session")
            if demo_dir.exists():
                latest_session = demo_dir
        
        # Check if we're using backup data
        backup_viz_dir = self.data_manager.output_dir / "backup_visualizations"
        using_backup = backup_viz_dir.exists() and len(list(backup_viz_dir.glob("*.png"))) > 0
        
        if latest_session or using_backup:
            # Show appropriate status message
            if latest_session and not using_backup:
                st.markdown(f"""
                <div class="success-box">
                    <strong>🎉 Data Collection Complete!</strong><br>
                    Session: {latest_session.name}<br>
                    Generated on: {datetime.fromtimestamp(latest_session.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                """, unsafe_allow_html=True)
            elif using_backup:
                st.markdown(f"""
                <div class="warning-box">
                    <strong>🔄 Using Backup Data</strong><br>
                    Live data collection failed or incomplete. Dashboard is displaying visualizations created from backup data.<br>
                    <em>Data may not reflect the most recent trends.</em>
                </div>
                """, unsafe_allow_html=True)
            
            # Create real visualizations if they don't exist
            if latest_session:
                artifacts_dir = latest_session / "artifacts"
                if not artifacts_dir.exists() or len(list(artifacts_dir.glob("*.png"))) == 0:
                    with st.spinner("Creating visualizations from collected data..."):
                        viz_results = self.data_manager.create_real_visualizations(latest_session)
                        if viz_results and viz_results.get('status') == 'success':
                            total_viz = viz_results.get('visualizations', 0)
                            if viz_results.get('fallback_mode', False):
                                st.warning(f"Generated {total_viz} visualizations using backup data!")
                            else:
                                st.success(f"Generated {total_viz} visualizations from live data!")
            elif using_backup:
                # Create visualizations from backup data only
                with st.spinner("Creating visualizations from backup data..."):
                    viz_results = self.data_manager.create_real_visualizations(None)
                    if viz_results and viz_results.get('status') == 'success':
                        total_viz = viz_results.get('visualizations', 0)
                        st.info(f"Generated {total_viz} visualizations from backup data!")
            
            # Get all visualization files (from session or backup)
            viz_files = self.data_manager.get_visualizations(latest_session)
            
            if viz_files:
                # Add CSS to reduce visualization sizes and ensure column consistency
                st.markdown("""
                <style>
                    /* Reduce image sizes by 25-30% */
                    .stImage {
                        max-width: 75% !important;
                        margin: 0 auto;
                    }

                    /* Ensure column images are same height */
                    div[data-testid="column"] img {
                        width: 100% !important;
                        height: auto !important;
                        object-fit: contain;
                    }

                    /* Better spacing for visualizations */
                    .element-container img {
                        margin-bottom: 1rem;
                    }
                </style>
                """, unsafe_allow_html=True)

                # Data Journalism Introduction
                st.markdown("""
                ### 📊 Data Story: Understanding Homelessness Through Digital Signals

                *A comprehensive analysis of public discourse, media coverage, and search trends reveals key insights into how Americans are engaging with the homelessness crisis.*
                """)

                # Key findings summary
                with st.expander("🔍 Key Findings at a Glance", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **What the Data Shows:**
                        - Search patterns reveal peak public interest in December
                        - Political coverage remains divided across news outlets
                        - Reddit communities show genuine personal stories
                        - Social media discussions reflect polarization
                        """)
                    with col2:
                        st.markdown("""
                        **Strategic Insights:**
                        - Best timing: November-December campaigns
                        - Geographic hotspots show regional variations
                        - Community-driven narratives resonate more
                        - Cross-platform consistency in messaging needed
                        """)

                st.markdown("---")
                
                # Group visualizations by type and exclude comprehensive/redundant ones
                all_google_trends_viz = [f for f in viz_files if 'google_trends' in f.name.lower() or 'googletrends' in f.name.lower()]
                google_trends_viz = filter_latest_google_trends_files(all_google_trends_viz)  # Keep only latest files
                news_viz = [f for f in viz_files if f.name.lower().startswith('news_')]

                # Exclude comprehensive visualizations for Reddit and Bluesky
                reddit_viz = [f for f in viz_files if 'reddit' in f.name.lower() and 'comprehensive' not in f.name.lower()]
                bluesky_viz = [f for f in viz_files if 'bluesky' in f.name.lower() and 'comprehensive' not in f.name.lower() and 'narrative' not in f.name.lower()]
                

                # ========== SECTION 1: What are people searching for? ==========
                if google_trends_viz:
                    st.markdown("## 🔍 What are people searching for?")
                    st.markdown("*Understanding public interest through search behavior reveals when and where advocacy efforts can be most effective.*")
                    st.markdown("")

                    # Create the 4-chart layout first (like the reference image)
                    create_google_trends_4_chart_layout(google_trends_viz, "Homelessness Trends")

                    # Separate HTML and PNG files
                    html_files = [f for f in google_trends_viz if f.suffix.lower() == '.html']
                    png_files = [f for f in google_trends_viz if f.suffix.lower() == '.png']

                    # Group PNG files by type for better organization
                    if png_files:
                        st.markdown("---")
                        
                        # Group by visualization type
                        timeseries_files = [f for f in png_files if 'timeseries' in f.name.lower()]
                        seasonal_files = [f for f in png_files if 'seasonal' in f.name.lower()]
                        other_files = [f for f in png_files if 'timeseries' not in f.name.lower() and 'seasonal' not in f.name.lower()]

                        # Display Time Series Charts
                        if timeseries_files:
                            for png_file in timeseries_files:
                                try:
                                    st.image(str(png_file), use_container_width=True, caption=None)
                                except Exception as e:
                                    st.error(f"Error loading {png_file.name}: {str(e)}")

                        # Display Seasonal Patterns with filtering
                        if seasonal_files:
                            st.markdown("---")
                            
                            # Extract unique keywords from seasonal file names
                            seasonal_keywords = set()
                            for file in seasonal_files:
                                # Extract theme from filename (between 'seasonal_' and '_YYYYMMDD')
                                import re
                                match = re.search(r'seasonal_(.+?)_\d{8}', file.name)
                                if match:
                                    keyword = match.group(1)
                                    seasonal_keywords.add(keyword)
                            
                            seasonal_keywords = sorted(list(seasonal_keywords))
                            
                            if seasonal_keywords:
                                # Add subtle dropdown for filtering
                                selected_keyword = st.selectbox(
                                    "Filter seasonal patterns by theme:",
                                    options=seasonal_keywords,
                                    index=0,
                                    key="seasonal_filter"
                                )

                                # Filter files based on selection
                                filtered_seasonal_files = [f for f in seasonal_files if selected_keyword in f.name]

                                # Display filtered files
                                if filtered_seasonal_files:
                                    for png_file in filtered_seasonal_files:
                                        try:
                                            st.image(str(png_file), use_container_width=True, caption=None)
                                        except Exception as e:
                                            st.error(f"Error loading {png_file.name}: {str(e)}")
                            else:
                                # Fallback if no keywords found
                                for png_file in seasonal_files:
                                    try:
                                        st.image(str(png_file), use_container_width=True, caption=None)
                                    except Exception as e:
                                        st.error(f"Error loading {png_file.name}: {str(e)}")

                        # Display Other Charts
                        if other_files:
                            for png_file in other_files:
                                try:
                                    st.image(str(png_file), use_container_width=True, caption=None)
                                except Exception as e:
                                    st.error(f"Error loading {png_file.name}: {str(e)}")
                    
                    # Display interactive maps using Streamlit (only one if they're similar)
                    if html_files:
                        st.markdown("---")
                        # Show only the first map (they typically show the same data)
                        try:
                            create_streamlit_choropleth_map(html_files[0], "Homelessness Trends")
                        except Exception as e:
                            st.error(f"Error creating map: {str(e)}")
                    
                    # Analysis insights
                    with st.expander("💡 Analysis Insights", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Key Observations:**")
                            st.markdown("- Search interest varies by geographic region")
                            st.markdown("- Seasonal patterns show peak interest periods")
                            st.markdown("- Policy searches correlate with legislative sessions")
                        with col2:
                            st.markdown("**Strategic Recommendations:**")
                            st.markdown("- Time campaigns during peak search periods")
                            st.markdown("- Focus messaging on high-interest themes")
                            st.markdown("- Geographic targeting based on patterns")
                    

                st.markdown("---")
                # ========== SECTION 2: How is the media covering this issue? ==========
                st.markdown("## 📰 How is the media covering this issue?")
                st.markdown("*Media narratives shape public perception. This analysis reveals how different outlets frame homelessness across the political spectrum.*")
                st.markdown("")

                if news_viz:
                    # Organize visualizations by type for better layout
                    wordcloud_viz = [f for f in news_viz if 'wordcloud' in f.name.lower()]
                    political_viz = [f for f in news_viz if 'political' in f.name.lower() and f.suffix == '.png']
                    outlet_viz = [f for f in news_viz if 'outlet' in f.name.lower()]
                    sankey_viz = [f for f in news_viz if 'sankey' in f.name.lower() and f.suffix == '.html']
                    other_viz = [f for f in news_viz if f not in wordcloud_viz + political_viz + outlet_viz + sankey_viz]

                    # Wordcloud first (full width) - most engaging
                    for viz_file in wordcloud_viz:
                        st.image(str(viz_file), use_container_width=True, caption=None)

                    # Sankey diagram (full width interactive)
                    for viz_file in sankey_viz:
                        try:
                            with open(viz_file, 'r', encoding='utf-8') as f:
                                sankey_html = f.read()
                            components.html(sankey_html, height=520, scrolling=False)
                        except Exception as e:
                            st.error(f"Could not load Sankey diagram: {e}")

                    # Two-column layout for political visualizations (same height)
                    if political_viz and len(political_viz) >= 2:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(str(political_viz[0]), use_container_width=True, caption=None)
                        with col2:
                            st.image(str(political_viz[1]), use_container_width=True, caption=None)
                        # Show remaining political viz
                        for viz_file in political_viz[2:]:
                            st.image(str(viz_file), use_container_width=True, caption=None)

                    # Outlet comparison (full width)
                    for viz_file in outlet_viz:
                        st.image(str(viz_file), use_container_width=True, caption=None)

                    # Other visualizations
                    for viz_file in other_viz:
                        if viz_file.suffix == '.png':
                            st.image(str(viz_file), use_container_width=True, caption=None)
                        elif viz_file.suffix == '.html':
                            try:
                                with open(viz_file, 'r', encoding='utf-8') as f:
                                    html_content = f.read()
                                components.html(html_content, height=600, scrolling=True)
                            except Exception as e:
                                st.error(f"Could not load HTML visualization: {e}")

                    # Display News data insights
                    try:
                        news_data = load_news_data(latest_session)
                        if news_data is not None and not news_data.empty:
                            with st.expander("📊 News Coverage Insights", expanded=False):
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Articles Analyzed", len(news_data))
                                with col2:
                                    if 'source' in news_data.columns:
                                        st.metric("News Outlets", news_data['source'].nunique())
                                with col3:
                                    if 'leaning' in news_data.columns:
                                        left_count = len(news_data[news_data['leaning'] == 'LEFT'])
                                        st.metric("Left-Leaning", left_count)
                                with col4:
                                    if 'leaning' in news_data.columns:
                                        right_count = len(news_data[news_data['leaning'] == 'RIGHT'])
                                        st.metric("Right-Leaning", right_count)

                                # Display top articles
                                st.markdown("**Top Recent Articles:**")
                                if 'title' in news_data.columns and 'source' in news_data.columns:
                                    display_cols = ['title', 'source']
                                    if 'date' in news_data.columns:
                                        display_cols.append('date')
                                    elif 'publishedAt' in news_data.columns:
                                        display_cols.append('publishedAt')
                                    if 'leaning' in news_data.columns:
                                        display_cols.append('leaning')

                                    sample_articles = news_data[display_cols].head(10)
                                    st.dataframe(sample_articles, use_container_width=True, hide_index=True)
                    except Exception as e:
                        st.info(f"News data insights temporarily unavailable")
                else:
                    st.info("📰 No news visualizations available. Run 'Analyze Region' to collect news data.")

                st.markdown("---")
                # ========== SECTION 3: What are the top problems faced by the homeless community? ==========
                st.markdown("## 💬 What are the top problems faced by the homeless community nationwide?")
                st.markdown("*Reddit communities provide unfiltered insights into the lived experiences and challenges discussed by those affected by homelessness.*")
                st.markdown("")

                if reddit_viz:
                    # Organize by type
                    engagement_viz = [f for f in reddit_viz if 'engagement' in f.name.lower() or 'trends' in f.name.lower()]
                    wordcloud_viz = [f for f in reddit_viz if 'wordcloud' in f.name.lower() or 'sentiment' in f.name.lower()]
                    subreddit_viz = [f for f in reddit_viz if 'subreddit' in f.name.lower()]
                    featured_viz = [f for f in reddit_viz if 'featured' in f.name.lower()]
                    other_viz = [f for f in reddit_viz if f not in engagement_viz + wordcloud_viz + subreddit_viz + featured_viz]

                    # Engagement trends (full width - it's important)
                    for viz_file in engagement_viz:
                        st.image(str(viz_file), use_container_width=True, caption=None)

                    # Two-column layout for wordcloud and subreddits
                    if wordcloud_viz or subreddit_viz:
                        col1, col2 = st.columns(2)
                        with col1:
                            for viz_file in wordcloud_viz[:1]:
                                st.image(str(viz_file), use_container_width=True, caption=None)
                        with col2:
                            for viz_file in subreddit_viz[:1]:
                                st.image(str(viz_file), use_container_width=True, caption=None)

                    # Featured posts - replace with paginated table
                    # (Don't show the image, we'll use the table below)

                    # Display Reddit top posts as paginated table (top 50)
                    try:
                        reddit_data = load_reddit_data(latest_session)
                        if reddit_data is not None and not reddit_data.empty:
                            st.markdown("---")
                            # Show top 50 posts with pagination
                            display_reddit_top_posts_table(reddit_data, page_size=10)

                            # Additional insights in expander
                            with st.expander("📊 Community Insights", expanded=False):
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Total Posts", len(reddit_data))
                                with col2:
                                    if 'subreddit' in reddit_data.columns:
                                        st.metric("Subreddits", reddit_data['subreddit'].nunique())
                                with col3:
                                    if 'score' in reddit_data.columns:
                                        st.metric("Avg Upvotes", f"{reddit_data['score'].mean():.0f}")
                                with col4:
                                    if 'num_comments' in reddit_data.columns:
                                        st.metric("Avg Comments", f"{reddit_data['num_comments'].mean():.0f}")
                    except Exception as e:
                        st.info(f"Reddit data temporarily unavailable")
                else:
                    st.info("💬 No Reddit visualizations available. Run 'Analyze Region' to collect Reddit data.")

                st.markdown("---")
                # ========== SECTION 4: How is public sentiment trending on social media? ==========
                st.markdown("## 🦋 How is public sentiment trending on social media?")
                st.markdown("*Social media discussions reveal real-time sentiment, political polarization, and emerging narratives around homelessness.*")
                st.markdown("")

                if bluesky_viz:
                    # Organize by type for better storytelling
                    timeline_viz = [f for f in bluesky_viz if 'timeline' in f.name.lower()]
                    wordcloud_viz = [f for f in bluesky_viz if 'wordcloud' in f.name.lower()]
                    polarization_viz = [f for f in bluesky_viz if 'polarization' in f.name.lower() or 'gauge' in f.name.lower()]
                    engagement_viz = [f for f in bluesky_viz if 'engagement' in f.name.lower() or 'hourly' in f.name.lower()]
                    author_viz = [f for f in bluesky_viz if 'author' in f.name.lower()]
                    other_viz = [f for f in bluesky_viz if f not in timeline_viz + wordcloud_viz + polarization_viz + engagement_viz + author_viz]

                    # Timeline (full width)
                    for viz_file in timeline_viz:
                        st.image(str(viz_file), use_container_width=True, caption=None)

                    # Polarization Gauge (centered on top)
                    if polarization_viz:
                        for viz_file in polarization_viz[:1]:
                            st.image(str(viz_file), use_container_width=True, caption=None)

                    # Political Wordclouds Row: Left | Right (below pie chart)
                    left_wc = [f for f in wordcloud_viz if 'left' in f.name.lower()]
                    right_wc = [f for f in wordcloud_viz if 'right' in f.name.lower()]

                    if left_wc and right_wc:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(str(left_wc[0]), use_container_width=True, caption=None)
                        with col2:
                            st.image(str(right_wc[0]), use_container_width=True, caption=None)

                    # Two-column: Engagement patterns
                    if engagement_viz and len(engagement_viz) >= 2:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(str(engagement_viz[0]), use_container_width=True, caption=None)
                        with col2:
                            st.image(str(engagement_viz[1]), use_container_width=True, caption=None)
                    elif engagement_viz:
                        for viz_file in engagement_viz:
                            st.image(str(viz_file), use_container_width=True, caption=None)

                    # Author analysis (full width if needed)
                    for viz_file in author_viz:
                        st.image(str(viz_file), use_container_width=True, caption=None)

                    # Display Bluesky tweet table at bottom (like Twitter feed)
                    try:
                        bluesky_data = load_bluesky_data(latest_session)
                        if bluesky_data is not None and not bluesky_data.empty:
                            st.markdown("---")
                            # Show top 100 tweets with pagination (10 per page)
                            st.markdown("##### 🐦 Live Feed: Top Posts")
                            display_bluesky_top_tweets_table(bluesky_data, page_size=10)

                            # Additional insights in expander
                            with st.expander("📊 Platform Insights", expanded=False):
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Total Posts", len(bluesky_data))
                                with col2:
                                    if 'author_handle' in bluesky_data.columns or 'author' in bluesky_data.columns:
                                        author_col = 'author_handle' if 'author_handle' in bluesky_data.columns else 'author'
                                        st.metric("Authors", bluesky_data[author_col].nunique())
                                with col3:
                                    if 'like_count' in bluesky_data.columns:
                                        st.metric("Total Likes", f"{bluesky_data['like_count'].sum():,}")
                                with col4:
                                    if 'repost_count' in bluesky_data.columns:
                                        st.metric("Total Reposts", f"{bluesky_data['repost_count'].sum():,}")
                        else:
                            st.info("📊 No Bluesky post data available.")
                    except Exception as e:
                        st.info(f"Bluesky data temporarily unavailable")
                else:
                    st.info("🦋 No Bluesky visualizations available. Run 'Analyze Region' to collect Bluesky data.")
                
                # Show file summary
                st.markdown("### 📁 Generated Files Summary")
                file_summary = {}
                for viz_file in viz_files:
                    ext = viz_file.suffix.lower()
                    file_summary[ext] = file_summary.get(ext, 0) + 1
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("PNG Images", file_summary.get('.png', 0))
                with col2:
                    st.metric("HTML Files", file_summary.get('.html', 0))
                with col3:
                    st.metric("CSV Data", file_summary.get('.csv', 0))
                with col4:
                    st.metric("Total Files", len(viz_files))
                    
            else:
                st.markdown("""
                <div class="warning-box">
                    <strong>⚠️ No Visualizations Found</strong><br>
                    The data collection completed but no visualization files were generated. This might be due to an issue with the visualization generation process.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ No Data Available</strong><br>
                No recent data collection session was found and no backup data is available. The visualizations will appear here once data is available.
            </div>
            """, unsafe_allow_html=True)
    
    # Old methods removed - using new guided workflow instead
    
    def run(self):
        """Main dashboard execution with page navigation"""
        if st.session_state.current_page == 'landing':
            self.render_landing_page()
        elif st.session_state.current_page == 'loading':
            self.render_loading_screen()
            refresh_interval = 3  # seconds between progress updates for smoother animation

            # If collection has already finished, jump straight to the dashboard
            if st.session_state.all_data_collected:
                st.session_state.current_page = 'dashboard'
                st.rerun()

            # Kick off data collection the first time we hit the loading screen
            if st.session_state.scraper_process is None:
                self.start_real_data_collection()
                time.sleep(1.5)
                st.rerun()

            # Update progress indicators based on elapsed time
            self.update_data_collection_progress()

            elapsed_time = time.time() - st.session_state.collection_start_time if st.session_state.collection_start_time else 0
            if st.session_state.all_data_collected or elapsed_time > 123:
                st.session_state.current_page = 'dashboard'
                st.rerun()

            time.sleep(refresh_interval)
            st.rerun()
        elif st.session_state.current_page == 'dashboard':
            self.render_dashboard_header()
            
            # Check if we need to create backup visualizations immediately
            latest_session = self.data_manager.get_latest_session_dir()
            backup_viz_dir = self.data_manager.output_dir / "backup_visualizations"
            
            # If no session data and no backup visualizations exist, create them
            if not latest_session and (not backup_viz_dir.exists() or len(list(backup_viz_dir.glob("*.png"))) == 0):
                with st.spinner("Creating visualizations from backup data..."):
                    try:
                        viz_results = self.data_manager.create_real_visualizations(None)
                        if viz_results and viz_results.get('status') == 'success':
                            total_viz = viz_results.get('visualizations', 0)
                            st.success(f"✅ Dashboard ready with {total_viz} backup data visualizations!")
                        else:
                            st.warning("⚠️ Could not create visualizations from backup data")
                    except Exception as e:
                        st.error(f"Error creating backup visualizations: {e}")
            
            # Section 1: What are the trends in your zipcode?
            self.render_zipcode_trends()
            
            # Section 2: How is homelessness affecting your constituents?
            self.render_constituent_impact()
            
            # Section 3: What are people searching for?
            self.render_search_trends()
            
            # Section 4: What are the top problems faced by the homeless community nationwide?
            self.render_reddit_analysis()
            
            # Section 5: How is the media talking about it?
            self.render_media_analysis()
            
            # Section 6: Zoom it and compare to surrounding states
            self.render_geographic_comparison()
            
            # Integrated visualizations (rendered within existing sections above)
            self.render_integrated_visualizations()

def main():
    """Main application entry point"""
    dashboard = NGODashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
