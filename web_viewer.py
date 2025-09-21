#!/usr/bin/env python3
"""
Bluesky Social Justice Data Web Viewer
DFP F25 Social Media Blue Team

Simple web interface for exploring collected social justice data.
Provides search, charts, and author analysis without modifying the collector.
"""

import json
import os
import pandas as pd
from datetime import datetime, timezone
from collections import defaultdict, Counter
from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64

app = Flask(__name__)

class DataViewer:
    def __init__(self):
        self.alltime_dir = "data/alltime"
        self.keywords = ["food_insecurity", "housing", "homeless", "unemployment", "gender_inequality"]
        self.keyword_labels = {
            "food_insecurity": "Food Insecurity",
            "housing": "Housing",
            "homeless": "Homelessness", 
            "unemployment": "Unemployment",
            "gender_inequality": "Gender Inequality"
        }
        self.data_cache = {}
        self.load_all_data()
    
    def load_all_data(self):
        """Load all alltime data into memory"""
        print("Loading alltime data...")
        all_posts = []
        
        for keyword in self.keywords:
            file_path = os.path.join(self.alltime_dir, f"{keyword}_alltime.jsonl")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                post = json.loads(line.strip())
                                post['keyword_label'] = self.keyword_labels[keyword]
                                all_posts.append(post)
                            except json.JSONDecodeError:
                                continue
                    print(f"Loaded {keyword}: {len([p for p in all_posts if p.get('keyword') == keyword])} posts")
                except Exception as e:
                    print(f"Error loading {keyword}: {e}")
        
        self.data_cache['all_posts'] = all_posts
        print(f"Total posts loaded: {len(all_posts)}")
    
    def search_posts(self, query="", page=1, per_page=20):
        """Search posts with wildcard matching"""
        all_posts = self.data_cache.get('all_posts', [])
        
        if query:
            # Wildcard search in text content
            filtered_posts = [
                post for post in all_posts 
                if query.lower() in post.get('text', '').lower()
            ]
        else:
            filtered_posts = all_posts
        
        # Sort by creation date (newest first)
        filtered_posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_posts = filtered_posts[start_idx:end_idx]
        
        return {
            'posts': page_posts,
            'total': len(filtered_posts),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(filtered_posts) + per_page - 1) // per_page
        }
    
    def get_keyword_stats(self):
        """Get keyword appearance statistics"""
        all_posts = self.data_cache.get('all_posts', [])
        keyword_counts = Counter()
        
        for post in all_posts:
            keyword = post.get('keyword', '')
            if keyword in self.keyword_labels:
                keyword_counts[keyword] += 1
        
        return {
            'labels': [self.keyword_labels[k] for k in self.keywords if k in keyword_counts],
            'data': [keyword_counts[k] for k in self.keywords if k in keyword_counts]
        }
    
    def get_daily_trends(self):
        """Get daily trends for all themes"""
        all_posts = self.data_cache.get('all_posts', [])
        daily_counts = defaultdict(lambda: defaultdict(int))
        
        for post in all_posts:
            keyword = post.get('keyword', '')
            if keyword in self.keyword_labels:
                try:
                    # Parse creation date
                    created_at = post.get('created_at', '')
                    if created_at:
                        # Handle different date formats
                        if 'T' in created_at:
                            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            date_obj = datetime.fromisoformat(created_at)
                        
                        date_str = date_obj.strftime('%Y-%m-%d')
                        daily_counts[date_str][keyword] += 1
                except Exception as e:
                    continue
        
        # Convert to chart data
        dates = sorted(daily_counts.keys())
        datasets = {}
        
        for keyword in self.keywords:
            datasets[keyword] = {
                'label': self.keyword_labels[keyword],
                'data': [daily_counts[date][keyword] for date in dates]
            }
        
        return {
            'dates': dates,
            'datasets': datasets
        }
    
    def get_top_authors(self, page=1, per_page=5):
        """Get top authors by follower count"""
        all_posts = self.data_cache.get('all_posts', [])
        
        # Group posts by author
        author_stats = defaultdict(lambda: {
            'handle': '',
            'display_name': '',
            'followers_count': 0,
            'posts': [],
            'themes': set(),
            'total_posts': 0
        })
        
        for post in all_posts:
            handle = post.get('author_handle', '')
            if handle:
                author_stats[handle]['handle'] = handle
                author_stats[handle]['display_name'] = post.get('author_display_name', handle)
                author_stats[handle]['followers_count'] = max(
                    author_stats[handle]['followers_count'],
                    post.get('author_followers_count', 0)
                )
                author_stats[handle]['posts'].append(post)
                author_stats[handle]['themes'].add(post.get('keyword_label', 'Unknown'))
                author_stats[handle]['total_posts'] += 1
        
        # Sort by follower count
        sorted_authors = sorted(
            author_stats.values(),
            key=lambda x: x['followers_count'],
            reverse=True
        )
        
        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_authors = sorted_authors[start_idx:end_idx]
        
        # Prepare response data
        for author in page_authors:
            author['themes'] = list(author['themes'])
            author['sample_tweet'] = author['posts'][0].get('text', '')[:100] + '...' if author['posts'] else ''
        
        return {
            'authors': page_authors,
            'total': len(sorted_authors),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(sorted_authors) + per_page - 1) // per_page
        }

# Initialize data viewer
viewer = DataViewer()

@app.route('/')
def index():
    """Main page with search and charts"""
    return render_template('index.html')

@app.route('/api/search')
def api_search():
    """API endpoint for post search"""
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    result = viewer.search_posts(query, page, per_page)
    return jsonify(result)

@app.route('/api/keyword-stats')
def api_keyword_stats():
    """API endpoint for keyword statistics"""
    stats = viewer.get_keyword_stats()
    return jsonify(stats)

@app.route('/api/daily-trends')
def api_daily_trends():
    """API endpoint for daily trends"""
    trends = viewer.get_daily_trends()
    return jsonify(trends)

@app.route('/api/top-authors')
def api_top_authors():
    """API endpoint for top authors"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))
    
    authors = viewer.get_top_authors(page, per_page)
    return jsonify(authors)

if __name__ == '__main__':
    print("🌐 Starting Bluesky Social Justice Data Web Viewer")
    print("📊 Loaded data:")
    print(f"   Total posts: {len(viewer.data_cache.get('all_posts', []))}")
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
