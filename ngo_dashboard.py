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
        self.master_scraper_path = self.project_root / "master_scraper_data.py"
        self.output_dir = self.project_root / "data" / "master_output"
        self.backup_data_dir = self.project_root / "data" / "BACKUP_RAWDATA"
        
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
                    st.warning(f"⚠️ Session visualization failed: {e}")
                    using_backup = True
            
            # If session failed or no session, use backup data
            if using_backup or not session_dir:
                st.warning("⚠️ Using backup data for visualizations (live data collection failed or incomplete)")
                
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
                    st.error("❌ No backup data files found")
                    return {'status': 'failed', 'error': 'No backup data available'}
            
        except Exception as e:
            st.error(f"Error creating visualizations: {e}")
            return {'status': 'failed', 'error': str(e)}

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
            elif status['status'] == 'failed':
                icon = "❌"
                color = "#ef4444"
                progress_text = "Failed"
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
        failed_sources = sum(1 for status in st.session_state.data_sources_status.values() if status['status'] == 'failed')
        
        if completed_sources == total_sources:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #10b981, #059669); color: #ffffff; padding: 1.5rem; border-radius: 15px; margin: 2rem auto; max-width: 600px; text-align: center; box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);">
                <h3 style="margin: 0 0 1rem 0; font-size: 1.5rem;">🎉 Data Collection Complete!</h3>
                <p style="margin: 0; font-size: 1.1rem;">All sources have been successfully collected. Loading dashboard...</p>
            </div>
            """, unsafe_allow_html=True)
        elif failed_sources > 0:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #ef4444, #dc2626); color: #ffffff; padding: 1.5rem; border-radius: 15px; margin: 2rem auto; max-width: 600px; text-align: center; box-shadow: 0 10px 30px rgba(239, 68, 68, 0.3);">
                <h3 style="margin: 0 0 1rem 0; font-size: 1.5rem;">⚠️ Partial Data Collection</h3>
                <p style="margin: 0; font-size: 1.1rem;">Some data sources failed to collect. Dashboard will show available data.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: #ffffff; padding: 1.5rem; border-radius: 15px; margin: 2rem auto; max-width: 600px; text-align: center; box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);">
                <h3 style="margin: 0 0 1rem 0; font-size: 1.5rem;">📊 Collecting Data Sources</h3>
                <p style="margin: 0; font-size: 1.1rem;">Please wait while we gather comprehensive insights from all sources...</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Add manual proceed button if data collection is taking too long
        elapsed_time = time.time() - st.session_state.collection_start_time if st.session_state.collection_start_time else 0
        if elapsed_time > 120:  # After 2 minutes, show manual proceed option
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.95); padding: 2rem; border-radius: 20px; margin: 2rem auto; max-width: 600px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center;">
                <h3 style="color: #1f2937; margin-bottom: 1rem;">Data Collection Taking Longer Than Expected</h3>
                <p style="color: #6b7280; margin-bottom: 1.5rem;">You can proceed to the dashboard with available data or continue waiting.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Proceed to Dashboard with Available Data", key="proceed_btn", type="primary"):
                    st.session_state.current_page = 'dashboard'
                    st.rerun()
    
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
        """Update progress based on real master scraper execution and actual data files"""
        if st.session_state.scraper_process is None:
            return
            
        # Check if process is still running
        if st.session_state.scraper_process.poll() is None:
            # Process is still running, update progress based on elapsed time
            elapsed_time = time.time() - st.session_state.collection_start_time
            total_estimated_time = 180  # 3 minutes estimated total time (increased for safety)
            
            # Estimate progress based on time (this is approximate)
            overall_progress = min(90, (elapsed_time / total_estimated_time) * 100)
            
            # Distribute progress across sources based on estimated timing
            # Google Trends: 20%, News API: 25%, Reddit: 30%, Bluesky: 25%
            source_timing = {
                'google_trends': (0, 0.20),
                'news_api': (0.20, 0.45), 
                'reddit': (0.45, 0.75),
                'bluesky': (0.75, 1.0)
            }
            
            for source, (start_ratio, end_ratio) in source_timing.items():
                if overall_progress >= end_ratio * 100:
                    st.session_state.data_sources_status[source]['status'] = 'collecting'
                    st.session_state.data_sources_status[source]['progress'] = 90  # Don't mark as complete yet
                elif overall_progress >= start_ratio * 100:
                    st.session_state.data_sources_status[source]['status'] = 'collecting'
                    source_progress = ((overall_progress - start_ratio * 100) / ((end_ratio - start_ratio) * 100)) * 90
                    st.session_state.data_sources_status[source]['progress'] = min(90, source_progress)
                else:
                    st.session_state.data_sources_status[source]['status'] = 'pending'
                    st.session_state.data_sources_status[source]['progress'] = 0
        else:
            # Process has completed - now check for actual data files
            st.session_state.scraper_process = None
            
            # Get the latest session directory
            latest_session = self.data_manager.get_latest_session_dir()
            
            if latest_session:
                # Check for actual data files from each source in raw_data/ directory
                raw_data_dir = latest_session / "raw_data"
                data_sources = {
                    'google_trends': ['googletrends', 'google_trends'],
                    'news_api': ['news', 'articles'],
                    'reddit': ['reddit', 'reddit_posts'],
                    'bluesky': ['bluesky', 'social']
                }
                
                all_sources_complete = True
                
                for source, keywords in data_sources.items():
                    source_complete = False
                    
                    # Check for CSV files with relevant keywords in raw_data/
                    if raw_data_dir.exists():
                        for file in raw_data_dir.glob("*.csv"):
                            if any(keyword in file.name.lower() for keyword in keywords):
                                source_complete = True
                                break
                        
                        # Check for JSON/JSONL files with relevant keywords
                        if not source_complete:
                            for file in raw_data_dir.glob("*.json*"):
                                if any(keyword in file.name.lower() for keyword in keywords):
                                    source_complete = True
                                    break
                        
                        # Check for Excel files (Google Trends)
                        if not source_complete and source == 'google_trends':
                            for file in raw_data_dir.glob("*.xlsx"):
                                if any(keyword in file.name.lower() for keyword in keywords):
                                    source_complete = True
                                    break
                    
                    if source_complete:
                        st.session_state.data_sources_status[source]['status'] = 'completed'
                        st.session_state.data_sources_status[source]['progress'] = 100
                    else:
                        st.session_state.data_sources_status[source]['status'] = 'failed'
                        st.session_state.data_sources_status[source]['progress'] = 0
                        all_sources_complete = False
                
                # Use backup mode if ANY source failed (new logic)
                failed_sources = [source for source, status in st.session_state.data_sources_status.items() 
                                if status['status'] == 'failed']
                completed_sources = [source for source, status in st.session_state.data_sources_status.items() 
                                   if status['status'] == 'completed']
                
                if len(failed_sources) > 0:
                    # ANY failure triggers backup mode
                    st.warning(f"⚠️ Data collection incomplete. Failed sources: {', '.join(failed_sources)}")
                    st.info("🔄 Using backup data mode due to data collection failures.")
                    st.session_state.all_data_collected = True  # Allow dashboard to proceed with backup data
                elif all_sources_complete:
                    # All sources completed successfully
                    st.session_state.all_data_collected = True
                else:
                    # No data collected at all, use backup data only
                    st.info("🔄 No live data collected. Dashboard will use backup data.")
                    st.session_state.all_data_collected = True  # Allow dashboard to proceed
            else:
                # No session directory found - mark all as failed and use backup data
                for source in st.session_state.data_sources_status:
                    st.session_state.data_sources_status[source]['status'] = 'failed'
                    st.session_state.data_sources_status[source]['progress'] = 0
                
                st.warning("⚠️ No session directory found. Using backup data for dashboard.")
                st.session_state.all_data_collected = True  # Allow dashboard to proceed with backup data
    
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
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #10b981, #059669); color: #ffffff; padding: 1rem; border-radius: 10px; margin: 1rem 0; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);">
                <strong style="color: #ffffff; font-size: 1.1rem;">📍 Analyzing ZIP Code: {st.session_state.zipcode}</strong><br>
                <span style="color: #f0fdf4;">Real-time data analysis from multiple sources</span>
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
        
        # Check if we have real data available
        latest_session = self.data_manager.get_latest_session_dir()
        backup_viz_dir = self.data_manager.output_dir / "backup_visualizations"
        has_real_data = (latest_session and latest_session.exists()) or (backup_viz_dir.exists() and len(list(backup_viz_dir.glob("*.png"))) > 0)
        
        if has_real_data:
            st.markdown("""
            <div class="success-box">
                <strong>✅ Real Data Analysis Available</strong><br>
                The visualizations below are generated from actual data collected from Google Trends, News APIs, Reddit, and Bluesky. 
                Scroll down to the "Generated Visualizations" section to view the comprehensive analysis.
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
        
        # Check if we have real data available
        latest_session = self.data_manager.get_latest_session_dir()
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
        
        # Check if we have real data available
        latest_session = self.data_manager.get_latest_session_dir()
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
        
        # Check if we have real data available
        latest_session = self.data_manager.get_latest_session_dir()
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
        
        # Check if we have real data available
        latest_session = self.data_manager.get_latest_session_dir()
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
        """Section 6: Zoom it and compare to surrounding states"""
        st.markdown('<h2 class="section-header">🗺️ Zoom it and compare to surrounding states</h2>', unsafe_allow_html=True)
        
        # Check if we have real data available
        latest_session = self.data_manager.get_latest_session_dir()
        backup_viz_dir = self.data_manager.output_dir / "backup_visualizations"
        has_real_data = (latest_session and latest_session.exists()) or (backup_viz_dir.exists() and len(list(backup_viz_dir.glob("*.png"))) > 0)
        
        if has_real_data:
            st.markdown("""
            <div class="success-box">
                <strong>✅ Real Geographic Analysis</strong><br>
                The Google Trends map visualizations below show actual search interest patterns across different states and regions. 
                This helps identify areas with high need but low resources, and potential partnership opportunities with neighboring regions.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ Data Collection Required</strong><br>
                Geographic comparison requires Google Trends data collection for multiple states and regions. 
                This will show real search interest patterns to identify resource gaps and partnership opportunities.
            </div>
            """, unsafe_allow_html=True)
    
    def render_generated_visualizations(self):
        """Section 7: Display generated visualizations from master scraper with fallback to backup data"""
        st.markdown('<h2 class="section-header">📊 Generated Visualizations</h2>', unsafe_allow_html=True)
        
        # Get the latest session directory
        latest_session = self.data_manager.get_latest_session_dir()
        
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
                
                # Display Reddit visualizations
                if reddit_viz:
                    st.markdown("#### 💬 Reddit Analysis")
                    cols = st.columns(min(3, len(reddit_viz)))
                    for i, viz_file in enumerate(reddit_viz[:6]):
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
            
            # Auto-advance to dashboard after data collection (even if partial)
            if st.session_state.all_data_collected or any(status['status'] in ['completed', 'failed'] for status in st.session_state.data_sources_status.values()):
                # Check if we have at least some data or if enough time has passed
                elapsed_time = time.time() - st.session_state.collection_start_time if st.session_state.collection_start_time else 0
                
                # If we have completed sources or enough time has passed (3+ minutes), proceed to dashboard
                if st.session_state.all_data_collected or elapsed_time > 180:
                    st.session_state.current_page = 'dashboard'
                    st.rerun()
                else:
                    # Update progress for ongoing collection
                    self.update_data_collection_progress()
                    # Auto-refresh every 2 seconds to show progress
                    time.sleep(2)
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
                    # Auto-refresh every 2 seconds to show progress
                    time.sleep(2)
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
            
            # Section 7: Generated Visualizations
            self.render_generated_visualizations()

def main():
    """Main application entry point"""
    dashboard = NGODashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
