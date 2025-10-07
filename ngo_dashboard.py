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
        color: #e5e7eb;
        margin: 0;
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
        background-color: #fffbeb;
        border-left: 5px solid #f59e0b;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 0 12px 12px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .warning-box strong {
        color: #92400e;
        font-size: 1.1rem;
    }
    
    .warning-box {
        color: #374151;
        line-height: 1.6;
    }
    
    .success-box {
        background-color: #f0fdf4;
        border-left: 5px solid #10b981;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 0 12px 12px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .success-box strong {
        color: #065f46;
        font-size: 1.1rem;
    }
    
    .success-box {
        color: #374151;
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
        self.master_scraper_path = self.project_root / "master_scraper.py"
        self.output_dir = self.project_root / "data" / "master_output"
        
    def run_master_scraper(self, duration=120):
        """Run the master scraper with specified duration"""
        try:
            # Run master scraper as subprocess
            cmd = [sys.executable, str(self.master_scraper_path), "--duration", str(duration)]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            return process
        except Exception as e:
            st.error(f"Failed to start master scraper: {e}")
            return None
    
    def get_latest_session_dir(self):
        """Get the most recent session directory"""
        if not self.output_dir.exists():
            return None
            
        session_dirs = [d for d in self.output_dir.iterdir() if d.is_dir() and d.name.startswith('session_')]
        if not session_dirs:
            return None
            
        # Sort by creation time and return the latest
        latest_dir = max(session_dirs, key=lambda x: x.stat().st_mtime)
        return latest_dir
    
    def get_visualizations(self, session_dir):
        """Get all visualization files from a session"""
        if not session_dir or not session_dir.exists():
            return []
            
        viz_extensions = ['.png', '.html', '.jpg', '.jpeg']
        viz_files = []
        
        for file in session_dir.iterdir():
            if file.suffix.lower() in viz_extensions:
                viz_files.append(file)
                
        return sorted(viz_files, key=lambda x: x.stat().st_mtime, reverse=True)

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
        
        self.mock_data = self._generate_mock_data()
        self.data_manager = DataCollectionManager()
        
    def _generate_mock_data(self) -> Dict:
        """Generate realistic mock data for homelessness analysis"""
        
        # Generate time series data for the past 12 months
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        
        # Reddit discussion trends
        reddit_data = {
            'date': dates,
            'mentions': np.random.poisson(50, len(dates)) + 
                       np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 20 + 
                       np.random.normal(0, 10, len(dates)),
            'sentiment': np.random.normal(0.2, 0.3, len(dates)),
            'engagement': np.random.poisson(100, len(dates))
        }
        
        # Google Trends data (normalized 0-100)
        google_trends = {
            'date': dates,
            'search_volume': np.random.uniform(20, 80, len(dates)) + 
                           np.sin(np.arange(len(dates)) * 2 * np.pi / 365 + np.pi/4) * 15 +
                           np.random.normal(0, 5, len(dates))
        }
        
        # News coverage sentiment
        news_data = {
            'date': dates,
            'article_count': np.random.poisson(15, len(dates)),
            'sentiment': np.random.normal(-0.1, 0.4, len(dates)),
            'political_mentions': np.random.poisson(8, len(dates))
        }
        
        # Bluesky/Social media sentiment
        social_data = {
            'date': dates,
            'posts': np.random.poisson(25, len(dates)),
            'sentiment': np.random.normal(0.1, 0.3, len(dates)),
            'hashtag_usage': np.random.poisson(40, len(dates))
        }
        
        # Geographic data (mock for different zipcodes)
        zipcode_data = {
            '90210': {'city': 'Beverly Hills, CA', 'homeless_pop': 450, 'shelter_capacity': 120, 'funding': 2.3},
            '10001': {'city': 'New York, NY', 'homeless_pop': 7800, 'shelter_capacity': 3400, 'funding': 8.7},
            '60601': {'city': 'Chicago, IL', 'homeless_pop': 3200, 'shelter_capacity': 1500, 'funding': 4.2},
            '33101': {'city': 'Miami, FL', 'homeless_pop': 2100, 'shelter_capacity': 800, 'funding': 3.1},
            '94102': {'city': 'San Francisco, CA', 'homeless_pop': 6800, 'shelter_capacity': 2100, 'funding': 12.5}
        }
        
        # Key themes and messaging insights
        themes = {
            'top_themes': [
                {'theme': 'Housing Affordability Crisis', 'mentions': 1250, 'sentiment': -0.3, 'growth': 15.2},
                {'theme': 'Mental Health Support', 'mentions': 890, 'sentiment': 0.1, 'growth': 8.7},
                {'theme': 'Economic Inequality', 'mentions': 760, 'sentiment': -0.2, 'growth': 12.1},
                {'theme': 'Homeless Services Funding', 'mentions': 650, 'sentiment': -0.1, 'growth': 6.3},
                {'theme': 'Policy Solutions', 'mentions': 580, 'sentiment': 0.2, 'growth': 9.8}
            ],
            'effective_messaging': [
                'Focus on individual stories and human impact',
                'Emphasize economic benefits of housing-first approaches',
                'Highlight successful programs and measurable outcomes',
                'Connect homelessness to broader community health',
                'Use data-driven arguments for policy change'
            ],
            'timing_insights': [
                'Peak engagement occurs during winter months (Dec-Feb)',
                'Policy discussions spike during budget season (Mar-May)',
                'Community events generate 40% more engagement',
                'Weekend posts receive 25% higher interaction rates'
            ]
        }
        
        return {
            'reddit': reddit_data,
            'google_trends': google_trends,
            'news': news_data,
            'social': social_data,
            'zipcode_data': zipcode_data,
            'themes': themes
        }
    
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
            
            # Analyze button
            if st.button("🔍 Analyze Region", key="analyze_btn"):
                if zipcode and len(zipcode) == 5 and zipcode.isdigit():
                    st.session_state.zipcode = zipcode
                    st.session_state.current_page = 'loading'
                    
                    # Reset data collection status
                    st.session_state.data_sources_status = {
                        'reddit': {'status': 'pending', 'progress': 0},
                        'google_trends': {'status': 'pending', 'progress': 0},
                        'news_api': {'status': 'pending', 'progress': 0},
                        'bluesky': {'status': 'pending', 'progress': 0}
                    }
                    st.session_state.all_data_collected = False
                    
                    # TODO: Trigger backend data collection for all sources
                    print(f"🚀 BACKEND DATA COLLECTION TRIGGERED FOR ZIP CODE: {zipcode}")
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
    
    def render_loading_screen(self):
        """Render the data collection loading screen"""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #1d4ed8 100%); min-height: 100vh; padding: 2rem 0;">
            <div style="max-width: 800px; margin: 0 auto; padding: 2rem;">
                <h1 style="color: #ffffff; text-align: center; font-size: 3rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                    🔍 Collecting Data
                </h1>
                <p style="color: #ffffff; text-align: center; font-size: 1.2rem; margin-bottom: 3rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
                    Gathering insights from multiple sources for ZIP code {st.session_state.zipcode}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Data sources checklist
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.95); padding: 2rem; border-radius: 20px; margin: 2rem auto; max-width: 600px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <h2 style="color: #1f2937; text-align: center; margin-bottom: 2rem;">Data Sources Status</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Create checklist for each data source
        data_sources = [
            {'name': 'Reddit Discussions', 'key': 'reddit', 'description': 'Collecting homelessness-related posts and comments'},
            {'name': 'Google Trends', 'key': 'google_trends', 'description': 'Analyzing search volume patterns and trends'},
            {'name': 'News API', 'key': 'news_api', 'description': 'Gathering media coverage and sentiment analysis'},
            {'name': 'Bluesky Social', 'key': 'bluesky', 'description': 'Collecting social media posts and engagement'}
        ]
        
        for source in data_sources:
            status = st.session_state.data_sources_status[source['key']]
            
            if status['status'] == 'completed':
                icon = "✅"
                color = "#10b981"
                progress_text = "Completed"
            elif status['status'] == 'collecting':
                icon = "⏳"
                color = "#f59e0b"
                progress_text = f"Collecting... {status['progress']}%"
            else:
                icon = "⏸️"
                color = "#6b7280"
                progress_text = "Pending"
            
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 2rem;">{icon}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="padding: 1rem 0;">
                    <h3 style="color: #1f2937; margin: 0 0 0.5rem 0; font-size: 1.2rem;">{source['name']}</h3>
                    <p style="color: #6b7280; margin: 0 0 0.5rem 0; font-size: 0.9rem;">{source['description']}</p>
                    <div style="background: #f3f4f6; border-radius: 10px; height: 8px; margin: 0.5rem 0;">
                        <div style="background: {color}; height: 100%; border-radius: 10px; width: {status['progress']}%; transition: width 0.3s ease;"></div>
                    </div>
                    <p style="color: {color}; margin: 0; font-size: 0.8rem; font-weight: 600;">{progress_text}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
        
        # Overall progress
        total_progress = sum(status['progress'] for status in st.session_state.data_sources_status.values()) / len(st.session_state.data_sources_status)
        completed_sources = sum(1 for status in st.session_state.data_sources_status.values() if status['status'] == 'completed')
        total_sources = len(st.session_state.data_sources_status)
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.95); padding: 2rem; border-radius: 20px; margin: 2rem auto; max-width: 600px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center;">
            <h3 style="color: #1f2937; margin-bottom: 1rem;">Overall Progress</h3>
            <div style="background: #f3f4f6; border-radius: 15px; height: 20px; margin: 1rem 0;">
                <div style="background: linear-gradient(90deg, #10b981, #3b82f6); height: 100%; border-radius: 15px; width: {total_progress:.1f}%; transition: width 0.5s ease;"></div>
            </div>
            <p style="color: #1f2937; margin: 0; font-size: 1.1rem;">
                {completed_sources}/{total_sources} sources completed ({total_progress:.1f}%)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Status message
        if completed_sources == total_sources:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #10b981, #059669); color: #ffffff; padding: 1.5rem; border-radius: 15px; margin: 2rem auto; max-width: 600px; text-align: center; box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);">
                <h3 style="margin: 0 0 1rem 0; font-size: 1.5rem;">🎉 Data Collection Complete!</h3>
                <p style="margin: 0; font-size: 1.1rem;">All sources have been successfully collected. Loading dashboard...</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: #ffffff; padding: 1.5rem; border-radius: 15px; margin: 2rem auto; max-width: 600px; text-align: center; box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);">
                <h3 style="margin: 0 0 1rem 0; font-size: 1.5rem;">📊 Collecting Data Sources</h3>
                <p style="margin: 0; font-size: 1.1rem;">Please wait while we gather comprehensive insights from all sources...</p>
            </div>
            """, unsafe_allow_html=True)
    
    def start_real_data_collection(self):
        """Start real data collection using master scraper"""
        if st.session_state.scraper_process is None:
            # Start the master scraper process
            st.session_state.scraper_process = self.data_manager.run_master_scraper(duration=120)
            st.session_state.collection_start_time = time.time()
            
            # Initialize all sources as collecting
            for source in st.session_state.data_sources_status:
                st.session_state.data_sources_status[source]['status'] = 'collecting'
                st.session_state.data_sources_status[source]['progress'] = 0
    
    def update_data_collection_progress(self):
        """Update progress based on real master scraper execution"""
        if st.session_state.scraper_process is None:
            return
            
        # Check if process is still running
        if st.session_state.scraper_process.poll() is None:
            # Process is still running, update progress based on elapsed time
            elapsed_time = time.time() - st.session_state.collection_start_time
            total_estimated_time = 120  # 2 minutes estimated total time
            
            # Estimate progress based on time (this is approximate)
            overall_progress = min(95, (elapsed_time / total_estimated_time) * 100)
            
            # Distribute progress across sources based on estimated timing
            # Google Trends: 15%, News API: 30%, Reddit: 25%, Bluesky: 30%
            source_timing = {
                'google_trends': (0, 0.15),
                'news_api': (0.15, 0.45), 
                'reddit': (0.45, 0.70),
                'bluesky': (0.70, 1.0)
            }
            
            for source, (start_ratio, end_ratio) in source_timing.items():
                if overall_progress >= end_ratio * 100:
                    st.session_state.data_sources_status[source]['status'] = 'completed'
                    st.session_state.data_sources_status[source]['progress'] = 100
                elif overall_progress >= start_ratio * 100:
                    st.session_state.data_sources_status[source]['status'] = 'collecting'
                    source_progress = ((overall_progress - start_ratio * 100) / ((end_ratio - start_ratio) * 100)) * 100
                    st.session_state.data_sources_status[source]['progress'] = min(95, source_progress)
                else:
                    st.session_state.data_sources_status[source]['status'] = 'pending'
                    st.session_state.data_sources_status[source]['progress'] = 0
        else:
            # Process has completed
            st.session_state.scraper_process = None
            
            # Mark all sources as completed
            for source in st.session_state.data_sources_status:
                st.session_state.data_sources_status[source]['status'] = 'completed'
                st.session_state.data_sources_status[source]['progress'] = 100
            
            # Mark all data as collected
            st.session_state.all_data_collected = True
    
    def render_dashboard_header(self):
        """Render the dashboard page header"""
        st.markdown("""
        <div style="background: #ffffff; padding: 1rem 0 0 0;">
            <h1 style="font-size: 2.5rem; font-weight: 700; color: #1f2937; text-align: center; margin-bottom: 1rem;">
                🏠 NGO Intelligence Dashboard
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Location info
        if st.session_state.zipcode:
            zipcode_data = self.mock_data['zipcode_data'].get(st.session_state.zipcode)
            if zipcode_data:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #10b981, #059669); color: #ffffff; padding: 1rem; border-radius: 10px; margin: 1rem 0; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);">
                    <strong style="color: #ffffff; font-size: 1.1rem;">📍 Analyzing: {zipcode_data['city']} ({st.session_state.zipcode})</strong><br>
                    <span style="color: #f0fdf4;">Homeless Population: {zipcode_data['homeless_pop']:,} • 
                    Shelter Capacity: {zipcode_data['shelter_capacity']:,} • 
                    Annual Funding: ${zipcode_data['funding']:.1f}M</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #10b981, #059669); color: #ffffff; padding: 1rem; border-radius: 10px; margin: 1rem 0; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);">
                    <strong style="color: #ffffff; font-size: 1.1rem;">📍 Analyzing ZIP Code: {st.session_state.zipcode}</strong><br>
                    <span style="color: #f0fdf4;">Using sample data for demonstration purposes</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Back button
        col1, col2, col3 = st.columns([1, 8, 1])
        with col1:
            if st.button("← Back to Search", key="back_btn"):
                st.session_state.current_page = 'landing'
                st.session_state.zipcode = None
                st.rerun()
    
    def render_zipcode_trends(self):
        """Section 1: What are the trends in your zipcode?"""
        st.markdown('<h2 class="section-header">📊 What are the trends in your zipcode?</h2>', unsafe_allow_html=True)
        
        # Sample stats for the zipcode
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📈 Monthly Search Volume",
                value="4,230",
                delta="12.3%",
                help="Google search interest for homelessness-related terms"
            )
        
        with col2:
            st.metric(
                label="💬 Social Mentions",
                value="1,847",
                delta="8.7%",
                help="Total mentions across social platforms this month"
            )
        
        with col3:
            st.metric(
                label="📰 News Articles",
                value="156",
                delta="-3.2%",
                help="Number of news articles mentioning homelessness"
            )
        
        # TODO: Replace with actual Google Trends visualization
        st.markdown("""
        <div class="insight-box">
            <strong>🔍 TODO: Google Trends Visualization</strong><br>
            <em>Once data sources are ready, this will show:</em><br>
            • Time series of search volume for homelessness-related terms in this ZIP code<br>
            • Comparison with national average<br>
            • Seasonal patterns and spikes in interest<br>
            • Related search terms and queries
        </div>
        """, unsafe_allow_html=True)
        
        # Mock chart placeholder
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            y=[100, 120, 110, 140, 160, 150],
            mode='lines+markers',
            name='Your ZIP Code',
            line=dict(color='#3b82f6', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            y=[80, 85, 90, 95, 100, 105],
            mode='lines+markers',
            name='National Average',
            line=dict(color='#ef4444', width=3)
        ))
        fig.update_layout(
            title="Search Volume Trends (Sample Data)",
            xaxis_title="Month",
            yaxis_title="Search Interest (Normalized)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def render_constituent_impact(self):
        """Section 2: How is homelessness affecting your constituents?"""
        st.markdown('<h2 class="section-header">👥 How is homelessness affecting your constituents?</h2>', unsafe_allow_html=True)
        
        # TODO: Replace with actual Google Trends visualizations
        st.markdown("""
        <div class="insight-box">
            <strong>🔍 TODO: 3 Google Trends Visualizations (National vs Local)</strong><br>
            <em>Once data sources are ready, this will show:</em><br>
            • <strong>Visualization 1:</strong> Housing affordability searches (local vs national)<br>
            • <strong>Visualization 2:</strong> Homeless services searches (local vs national)<br>
            • <strong>Visualization 3:</strong> Emergency shelter searches (local vs national)
        </div>
        """, unsafe_allow_html=True)
        
        # Mock visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(
                x=['Housing Affordability', 'Shelter Services', 'Emergency Help'],
                y=[85, 92, 78],
                name='Your ZIP Code',
                marker_color='#3b82f6'
            ))
            fig1.add_trace(go.Bar(
                x=['Housing Affordability', 'Shelter Services', 'Emergency Help'],
                y=[65, 70, 60],
                name='National Average',
                marker_color='#ef4444'
            ))
            fig1.update_layout(
                title="Search Interest: Local vs National (Sample)",
                xaxis_title="Search Categories",
                yaxis_title="Search Volume (Normalized)",
                height=400
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Mock heatmap showing interest patterns
            fig2 = go.Figure(data=go.Heatmap(
                z=[[85, 92, 78, 65],
                   [70, 88, 82, 58],
                   [90, 85, 75, 72]],
                x=['Q1', 'Q2', 'Q3', 'Q4'],
                y=['Housing', 'Services', 'Emergency'],
                colorscale='Blues',
                showscale=True
            ))
            fig2.update_layout(
                title="Quarterly Search Patterns (Sample)",
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    def render_search_trends(self):
        """Section 3: What are people searching for?"""
        st.markdown('<h2 class="section-header">🔍 What are people searching for?</h2>', unsafe_allow_html=True)
        
        # TODO: Replace with actual Google Trends data
        st.markdown("""
        <div class="insight-box">
            <strong>🔍 TODO: Google Trends Search Analysis</strong><br>
            <em>Once data sources are ready, this will show:</em><br>
            • Top search terms related to homelessness in your area<br>
            • Rising search queries (trending upward)<br>
            • Geographic comparison of search patterns<br>
            • Related queries and search suggestions
        </div>
        """, unsafe_allow_html=True)
        
        # Mock search trends
        search_terms = [
            "homeless shelters near me",
            "housing assistance programs",
            "emergency shelter",
            "homeless help",
            "affordable housing",
            "homeless services",
            "shelter beds available",
            "homeless outreach"
        ]
        
        search_volumes = [95, 88, 82, 76, 71, 68, 65, 60]
        
        fig = go.Figure(go.Bar(
            x=search_volumes,
            y=search_terms,
            orientation='h',
            marker_color='#10b981'
        ))
        fig.update_layout(
            title="Top Search Terms (Sample Data)",
            xaxis_title="Search Volume",
            yaxis_title="Search Terms",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def render_reddit_analysis(self):
        """Section 4: What are the top problems faced by the homeless community nationwide?"""
        st.markdown('<h2 class="section-header">💬 What are the top problems faced by the homeless community nationwide?</h2>', unsafe_allow_html=True)
        
        # TODO: Replace with actual Reddit visualizations
        st.markdown("""
        <div class="insight-box">
            <strong>🔍 TODO: Reddit Visualizations</strong><br>
            <em>Once data sources are ready, this will show:</em><br>
            • Sentiment analysis of homelessness discussions<br>
            • Most mentioned problems and challenges<br>
            • Community sentiment trends over time<br>
            • Geographic distribution of discussions<br>
            • Top subreddits discussing homelessness issues
        </div>
        """, unsafe_allow_html=True)
        
        # Mock Reddit analysis
        problems = [
            "Housing Affordability",
            "Mental Health Support",
            "Job Opportunities",
            "Healthcare Access",
            "Substance Abuse",
            "Family Separation",
            "Legal Issues",
            "Weather Exposure"
        ]
        
        mentions = [1250, 890, 760, 650, 580, 520, 480, 420]
        sentiment = [0.2, -0.3, 0.1, -0.1, -0.4, -0.2, -0.3, -0.1]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=mentions,
            y=problems,
            mode='markers',
            marker=dict(
                size=15,
                color=sentiment,
                colorscale='RdYlBu',
                showscale=True,
                colorbar=dict(title="Sentiment Score")
            ),
            text=[f"Mentions: {m}<br>Sentiment: {s:.2f}" for m, s in zip(mentions, sentiment)],
            hovertemplate="%{y}<br>%{text}<extra></extra>"
        ))
        fig.update_layout(
            title="Homelessness Problems Discussion (Sample Reddit Data)",
            xaxis_title="Number of Mentions",
            yaxis_title="Problems Discussed",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def render_media_analysis(self):
        """Section 5: How is the media talking about it?"""
        st.markdown('<h2 class="section-header">📰 How is the media talking about it?</h2>', unsafe_allow_html=True)
        
        # TODO: Replace with actual news/media visualizations
        st.markdown("""
        <div class="insight-box">
            <strong>🔍 TODO: NewsAPI, NPR and Bluesky Visualizations</strong><br>
            <em>Once data sources are ready, this will show:</em><br>
            • <strong>NewsAPI:</strong> Media coverage volume and sentiment by outlet<br>
            • <strong>NPR:</strong> Public radio coverage analysis and story themes<br>
            • <strong>Bluesky:</strong> Social media sentiment and trending topics<br>
            • News channel traction analysis and framing approaches
        </div>
        """, unsafe_allow_html=True)
        
        # Mock media analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # News outlets analysis
            outlets = ['CNN', 'Fox News', 'NPR', 'BBC', 'Local News', 'AP', 'Reuters']
            coverage = [45, 38, 52, 41, 28, 35, 33]
            sentiment = [0.1, -0.2, 0.3, 0.2, 0.0, 0.1, 0.2]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=outlets,
                y=coverage,
                marker_color=['#ef4444' if s < 0 else '#10b981' for s in sentiment],
                text=[f"{s:.1f}" for s in sentiment],
                textposition='auto'
            ))
            fig.update_layout(
                title="News Coverage by Outlet (Sample)",
                xaxis_title="News Outlets",
                yaxis_title="Number of Articles",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Bluesky sentiment analysis
            fig = go.Figure(data=go.Pie(
                labels=['Positive', 'Neutral', 'Negative'],
                values=[35, 45, 20],
                marker_colors=['#10b981', '#f59e0b', '#ef4444']
            ))
            fig.update_layout(
                title="Bluesky Social Media Sentiment (Sample)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_geographic_comparison(self):
        """Section 6: Zoom it and compare to surrounding states"""
        st.markdown('<h2 class="section-header">🗺️ Zoom it and compare to surrounding states</h2>', unsafe_allow_html=True)
        
        # TODO: Replace with actual Google Trends map visualization
        st.markdown("""
        <div class="insight-box">
            <strong>🔍 TODO: Google Trends Map Visualization</strong><br>
            <em>Once data sources are ready, this will show:</em><br>
            • Interactive map showing search interest by state/region<br>
            • Identification of areas with high need but low help<br>
            • Comparison of your state with surrounding states<br>
            • Resource gap analysis and partnership opportunities
        </div>
        """, unsafe_allow_html=True)
        
        # Mock geographic comparison
        states = ['Your State', 'Neighbor 1', 'Neighbor 2', 'Neighbor 3', 'Neighbor 4']
        search_interest = [85, 65, 78, 45, 72]
        resources = [60, 80, 55, 90, 65]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=states,
            y=search_interest,
            name='Search Interest',
            marker_color='#3b82f6'
        ))
        fig.add_trace(go.Bar(
            x=states,
            y=resources,
            name='Available Resources',
            marker_color='#10b981'
        ))
        fig.update_layout(
            title="Search Interest vs Available Resources (Sample)",
            xaxis_title="States",
            yaxis_title="Score (Normalized)",
            barmode='group',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Partnership opportunities
        st.markdown("""
        <div class="success-box">
            <strong>🤝 Partnership Opportunities Identified</strong><br>
            <em>Based on the analysis above:</em><br>
            • <strong>Neighbor 1:</strong> High resources, moderate interest - potential resource sharing<br>
            • <strong>Neighbor 3:</strong> Very high resources, low interest - outreach opportunity<br>
            • <strong>Your State:</strong> High interest, moderate resources - advocacy focus needed<br>
            • <strong>Neighbor 2:</strong> Similar profile - collaboration potential
        </div>
        """, unsafe_allow_html=True)
    
    def render_generated_visualizations(self):
        """Section 7: Display generated visualizations from master scraper"""
        st.markdown('<h2 class="section-header">📊 Generated Visualizations</h2>', unsafe_allow_html=True)
        
        # Get the latest session directory
        latest_session = self.data_manager.get_latest_session_dir()
        
        if latest_session:
            st.markdown(f"""
            <div class="success-box">
                <strong>🎉 Data Collection Complete!</strong><br>
                Session: {latest_session.name}<br>
                Generated on: {datetime.fromtimestamp(latest_session.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
            </div>
            """, unsafe_allow_html=True)
            
            # Get all visualization files
            viz_files = self.data_manager.get_visualizations(latest_session)
            
            if viz_files:
                st.markdown("### 📈 Interactive Visualizations")
                
                # Group visualizations by type
                google_trends_viz = [f for f in viz_files if 'googletrends' in f.name.lower() or 'national_seasonal' in f.name.lower() or 'state_seasonal' in f.name.lower()]
                news_viz = [f for f in viz_files if 'news_' in f.name.lower()]
                reddit_viz = [f for f in viz_files if 'reddit' in f.name.lower()]
                bluesky_viz = [f for f in viz_files if 'bluesky' in f.name.lower()]
                
                # Display Google Trends visualizations
                if google_trends_viz:
                    st.markdown("#### 🔍 Google Trends Analysis")
                    cols = st.columns(min(3, len(google_trends_viz)))
                    for i, viz_file in enumerate(google_trends_viz[:6]):  # Show up to 6
                        with cols[i % 3]:
                            if viz_file.suffix.lower() == '.png':
                                st.image(str(viz_file), caption=viz_file.stem, use_column_width=True)
                            elif viz_file.suffix.lower() == '.html':
                                with open(viz_file, 'r') as f:
                                    html_content = f.read()
                                components.html(html_content, height=400)
                
                # Display News visualizations
                if news_viz:
                    st.markdown("#### 📰 News Analysis")
                    cols = st.columns(min(3, len(news_viz)))
                    for i, viz_file in enumerate(news_viz[:6]):
                        with cols[i % 3]:
                            if viz_file.suffix.lower() == '.png':
                                st.image(str(viz_file), caption=viz_file.stem, use_column_width=True)
                
                # Display Bluesky visualizations
                if bluesky_viz:
                    st.markdown("#### 🐦 Bluesky Social Analysis")
                    cols = st.columns(min(3, len(bluesky_viz)))
                    for i, viz_file in enumerate(bluesky_viz[:6]):
                        with cols[i % 3]:
                            if viz_file.suffix.lower() == '.png':
                                st.image(str(viz_file), caption=viz_file.stem, use_column_width=True)
                
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
                <strong>⚠️ No Recent Data Found</strong><br>
                No recent data collection session was found. The visualizations will appear here once the master scraper completes successfully.
            </div>
            """, unsafe_allow_html=True)
    
    # Old methods removed - using new guided workflow instead
    
    def run(self):
        """Main dashboard execution with page navigation"""
        if st.session_state.current_page == 'landing':
            self.render_landing_page()
        elif st.session_state.current_page == 'loading':
            self.render_loading_screen()
            
            # Auto-advance to dashboard after data collection
            if st.session_state.all_data_collected:
                st.session_state.current_page = 'dashboard'
                st.rerun()
            else:
                # Start real data collection on first load
                if all(status['status'] == 'pending' for status in st.session_state.data_sources_status.values()):
                    # Start real data collection
                    self.start_real_data_collection()
                    st.rerun()
                else:
                    # Update progress for ongoing collection
                    self.update_data_collection_progress()
                    # Use auto-refresh with a placeholder for better UX
                    placeholder = st.empty()
                    placeholder.info("🔄 Updating progress... Please wait while data is being collected.")
                    st.rerun()
        elif st.session_state.current_page == 'dashboard':
            self.render_dashboard_header()
            
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
            
            # Section 7: Generated Visualizations
            self.render_generated_visualizations()

def main():
    """Main application entry point"""
    dashboard = NGODashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
