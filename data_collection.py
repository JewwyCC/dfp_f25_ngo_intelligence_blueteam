from datetime import datetime, timedelta
from textblob import TextBlob
import pandas as pd
import numpy as np
import time


def extract_post_data(post, subreddit: str, sort_method: str):
    try:
        age_hours = (datetime.now() - datetime.fromtimestamp(post.created_utc)).total_seconds() / 3600
        full_text = f"{post.title} {post.selftext}"
        blob = TextBlob(full_text)
        return {
            'id': post.id,
            'subreddit': subreddit,
            'title': post.title,
            'selftext': post.selftext,
            'score': post.score,
            'upvote_ratio': getattr(post, 'upvote_ratio', np.nan),
            'num_comments': post.num_comments,
            'created_utc': datetime.fromtimestamp(post.created_utc),
            'author': str(post.author) if post.author else '[deleted]',
            'url': post.url,
            'is_self': post.is_self,
            'sort_method': sort_method,
            'age_hours': age_hours,
            'engagement_rate': post.num_comments / max(post.score, 1),
            'velocity': post.score / max(age_hours, 1),
            'sentiment_polarity': blob.sentiment.polarity,
            'sentiment_subjectivity': blob.sentiment.subjectivity,
            'text_length': len(full_text),
            'word_count': len(full_text.split()),
        }
    except Exception:
        return None


def _timefilter_to_days(time_filter: str) -> int:
    mapping = {
        'hour': 1,   # effectively ~1 day for safety; GUI-level filtering will cut tighter if needed
        'day': 1,
        'week': 7,
        'month': 30,
        'year': 365,
        'all': 36500,
    }
    return mapping.get(time_filter, 30)


def collect_with_even_distribution(reddit, subreddits, keywords, posts_per_sub: int, time_filter: str, strategy: str):
    """Enhanced data collection with even monthly distribution for better yearly trend analysis."""
    max_age_days = _timefilter_to_days(time_filter)
    min_datetime = datetime.now() - timedelta(days=max_age_days)
    
    # Calculate target posts per month for even distribution
    if time_filter == 'year':
        months_in_range = 12
        posts_per_month = max(posts_per_sub // months_in_range, 2)  # At least 2 posts per month
    else:
        posts_per_month = posts_per_sub
    
    all_posts = []
    monthly_targets = {}
    
    # Initialize monthly targets
    current_date = datetime.now()
    for i in range(12):  # Last 12 months
        month_key = (current_date.year, current_date.month)
        monthly_targets[month_key] = posts_per_month
        current_date = current_date.replace(day=1) - timedelta(days=1)  # Previous month
    
    for sub_name in subreddits:
        try:
            subreddit = reddit.subreddit(sub_name)
            sort_methods = ['hot'] if strategy == 'fast' else ['hot', 'top', 'new']
            
            for sort_method in sort_methods:
                try:
                    limit = posts_per_sub if strategy == 'fast' else max(posts_per_sub // 3, 5)
                    if sort_method == 'top':
                        posts = subreddit.top(time_filter=time_filter, limit=limit)
                    elif sort_method == 'hot':
                        posts = subreddit.hot(limit=limit)
                    else:
                        posts = subreddit.new(limit=limit)

                    posts_checked = 0
                    for post in posts:
                        posts_checked += 1
                        if posts_checked >= limit * 2:
                            break
                            
                        # Check if we still need posts for this month
                        created_dt = datetime.fromtimestamp(post.created_utc)
                        if created_dt < min_datetime:
                            continue
                            
                        month_key = (created_dt.year, created_dt.month)
                        if monthly_targets.get(month_key, 0) <= 0:
                            continue
                            
                        post_text = f"{post.title} {post.selftext}".lower()
                        if any(kw.lower() in post_text for kw in keywords):
                            data = extract_post_data(post, sub_name, sort_method)
                            if data:
                                all_posts.append(data)
                                monthly_targets[month_key] -= 1
                                
                        # Stop if we've collected enough for all months
                        if all(target <= 0 for target in monthly_targets.values()):
                            break
                            
                except Exception:
                    continue
            time.sleep(0.5)
        except Exception:
            continue

    df = pd.DataFrame(all_posts)
    if not df.empty:
        df = df.drop_duplicates(subset=['id'], keep='first').reset_index(drop=True)
    return df


def collect(reddit, subreddits, keywords, posts_per_sub: int, time_filter: str, strategy: str):
    """Original collection method - now uses enhanced version for year-long analysis."""
    if time_filter == 'year':
        return collect_with_even_distribution(reddit, subreddits, keywords, posts_per_sub, time_filter, strategy)
    else:
        # Use original method for shorter timeframes
        max_age_days = _timefilter_to_days(time_filter)
        min_datetime = datetime.now() - timedelta(days=max_age_days)
        all_posts = []
        
        for sub_name in subreddits:
            try:
                subreddit = reddit.subreddit(sub_name)
                posts_collected = 0
                sort_methods = ['hot'] if strategy == 'fast' else ['hot', 'top', 'new']

                for sort_method in sort_methods:
                    if posts_collected >= posts_per_sub:
                        break
                    try:
                        limit = posts_per_sub if strategy == 'fast' else max(posts_per_sub // 3, 5)
                        if sort_method == 'top':
                            posts = subreddit.top(time_filter=time_filter, limit=limit)
                        elif sort_method == 'hot':
                            posts = subreddit.hot(limit=limit)
                        else:
                            posts = subreddit.new(limit=limit)

                        posts_checked = 0
                        for post in posts:
                            posts_checked += 1
                            if posts_collected >= posts_per_sub:
                                break
                            # Enforce timeframe on all sorting methods
                            created_dt = datetime.fromtimestamp(post.created_utc)
                            if created_dt < min_datetime:
                                continue
                            post_text = f"{post.title} {post.selftext}".lower()
                            if any(kw.lower() in post_text for kw in keywords):
                                data = extract_post_data(post, sub_name, sort_method)
                                if data:
                                    all_posts.append(data)
                                    posts_collected += 1
                            if posts_checked >= limit * 2:
                                break
                    except Exception:
                        continue
                time.sleep(0.5)
            except Exception:
                continue

        df = pd.DataFrame(all_posts)
        if not df.empty:
            df = df.drop_duplicates(subset=['id'], keep='first').reset_index(drop=True)
        return df


