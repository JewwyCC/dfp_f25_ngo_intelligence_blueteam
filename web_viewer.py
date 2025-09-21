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
        # Map from data format (with spaces) to internal format (with underscores)
        self.data_keyword_mapping = {
            "food insecurity": "food_insecurity",
            "housing": "housing",
            "homeless": "homeless", 
            "unemployment": "unemployment",
            "gender inequality": "gender_inequality"
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
                    keyword_posts = []
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                post = json.loads(line.strip())
                                # Map the data keyword to internal keyword format
                                data_keyword = post.get('keyword', '')
                                internal_keyword = self.data_keyword_mapping.get(data_keyword, keyword)
                                post['keyword_label'] = self.keyword_labels.get(internal_keyword, data_keyword)
                                post['internal_keyword'] = internal_keyword
                                keyword_posts.append(post)
                                all_posts.append(post)
                            except json.JSONDecodeError:
                                continue
                    print(f"Loaded {keyword}: {len(keyword_posts)} posts")
                except Exception as e:
                    print(f"Error loading {keyword}: {e}")
        
        self.data_cache['all_posts'] = all_posts
        print(f"Total posts loaded: {len(all_posts)}")
    
    def search_posts(self, query="", page=1, per_page=20, keyword_filter=""):
        """Search posts with wildcard matching and keyword filtering"""
        all_posts = self.data_cache.get('all_posts', [])
        
        filtered_posts = all_posts
        
        # Apply keyword filter first
        if keyword_filter:
            # Map keyword label back to internal keyword
            label_to_keyword = {v: k for k, v in self.keyword_labels.items()}
            internal_keyword = label_to_keyword.get(keyword_filter)
            if internal_keyword:
                filtered_posts = [
                    post for post in filtered_posts 
                    if post.get('internal_keyword') == internal_keyword
                ]
        
        # Apply text search filter
        if query:
            # Wildcard search in text content
            filtered_posts = [
                post for post in filtered_posts 
                if query.lower() in post.get('text', '').lower()
            ]
        
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
            internal_keyword = post.get('internal_keyword', '')
            if internal_keyword in self.keyword_labels:
                keyword_counts[internal_keyword] += 1
        
        # Include all keywords, even those with 0 posts
        all_keywords_with_counts = []
        for keyword in self.keywords:
            count = keyword_counts[keyword]
            all_keywords_with_counts.append((self.keyword_labels[keyword], count))
        
        # Sort by count (descending)
        all_keywords_with_counts.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'labels': [item[0] for item in all_keywords_with_counts],
            'data': [item[1] for item in all_keywords_with_counts]
        }
    
    def get_daily_trends(self):
        """Get daily trends for all themes"""
        all_posts = self.data_cache.get('all_posts', [])
        daily_counts = defaultdict(lambda: defaultdict(int))
        
        for post in all_posts:
            internal_keyword = post.get('internal_keyword', '')
            if internal_keyword in self.keyword_labels:
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
                        daily_counts[date_str][internal_keyword] += 1
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
    
    def get_top_authors(self, page=1, per_page=5, keyword_filter="", sort_by="posts"):
        """Get top authors with optional keyword filtering and sorting options"""
        all_posts = self.data_cache.get('all_posts', [])
        
        # Apply keyword filter if specified
        if keyword_filter:
            # Map keyword label back to internal keyword
            label_to_keyword = {v: k for k, v in self.keyword_labels.items()}
            internal_keyword = label_to_keyword.get(keyword_filter)
            if internal_keyword:
                all_posts = [
                    post for post in all_posts 
                    if post.get('internal_keyword') == internal_keyword
                ]
        
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
        
        # Sort based on sort_by parameter
        if sort_by == "followers":
            # Sort by follower count first, then by post count
            sorted_authors = sorted(
                author_stats.values(),
                key=lambda x: (x['followers_count'], x['total_posts']),
                reverse=True
            )
        else:  # sort_by == "posts" (default)
            # Sort by post count first, then by follower count
            sorted_authors = sorted(
                author_stats.values(),
                key=lambda x: (x['total_posts'], x['followers_count']),
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
    
    def get_author_posts(self, author_handle, page=1, per_page=20):
        """Get all posts by a specific author"""
        all_posts = self.data_cache.get('all_posts', [])
        
        # Filter posts by author
        author_posts = [
            post for post in all_posts 
            if post.get('author_handle', '').lower() == author_handle.lower()
        ]
        
        # Sort by creation date (newest first)
        author_posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_posts = author_posts[start_idx:end_idx]
        
        # Get author info from first post
        author_info = {}
        if author_posts:
            first_post = author_posts[0]
            author_info = {
                'handle': first_post.get('author_handle', ''),
                'display_name': first_post.get('author_display_name', ''),
                'followers_count': first_post.get('author_followers_count', 0),
                'total_posts': len(author_posts)
            }
        
        return {
            'posts': page_posts,
            'author_info': author_info,
            'total': len(author_posts),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(author_posts) + per_page - 1) // per_page
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
    keyword_filter = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    result = viewer.search_posts(query, page, per_page, keyword_filter)
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
    keyword_filter = request.args.get('keyword', '')
    sort_by = request.args.get('sort_by', 'posts')  # 'posts' or 'followers'
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))
    
    authors = viewer.get_top_authors(page, per_page, keyword_filter, sort_by)
    return jsonify(authors)

@app.route('/api/author-posts')
def api_author_posts():
    """API endpoint for author's posts"""
    author_handle = request.args.get('handle', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    if not author_handle:
        return jsonify({'error': 'Author handle required'}), 400
    
    posts = viewer.get_author_posts(author_handle, page, per_page)
    return jsonify(posts)

if __name__ == '__main__':
    import sys
    
    # Parse command line arguments for port
    port = 8080  # Default to 8080 to avoid AirPlay conflicts
    if len(sys.argv) > 1 and sys.argv[1].startswith('--port'):
        try:
            port = int(sys.argv[1].split('=')[1])
        except:
            pass
    
    print("🌐 Starting Bluesky Social Justice Data Web Viewer")
    print("📊 Loaded data:")
    print(f"   Total posts: {len(viewer.data_cache.get('all_posts', []))}")
    print(f"🌐 Starting web server on port {port}...")
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='127.0.0.1', port=port)
