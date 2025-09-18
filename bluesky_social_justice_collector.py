#!/usr/bin/env python3
"""
Bluesky Social Justice Data Collector
DFP F25 Social Media Blue Team

Single comprehensive script for collecting social justice data from Bluesky
with author influence metrics and session-based organization.

Features:
- Real-time firehose collection with authentication
- Author follower counts and profile data
- Session-based data organization
- Automatic alltime file generation
- Clean, minimal implementation

Usage:
    python bluesky_social_justice_collector.py --duration 1800  # 30 minutes
    python bluesky_social_justice_collector.py --duration 600   # 10 minutes
"""

import argparse
import json
import os
import re
import signal
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from collections import defaultdict

# Import required libraries
try:
    from atproto import Client, FirehoseSubscribeReposClient, parse_subscribe_repos_message, CAR, IdResolver, DidInMemoryCache
    import pandas as pd
except ImportError as e:
    print(f"Error: Required library not found. Please install: pip install atproto pandas")
    sys.exit(1)


class BlueskySocialJusticeCollector:
    def __init__(self, 
                 duration_seconds: int,
                 session_name: str = None):
        
        self.duration_seconds = duration_seconds
        self.session_name = session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Directory structure
        self.session_dir = f"data/sessions/{self.session_name}"
        self.alltime_dir = "data/alltime"
        
        # Create directories
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.alltime_dir, exist_ok=True)
        os.makedirs("data/config", exist_ok=True)
        
        # Keywords for social justice topics
        self.keywords = [
            "food insecurity", "housing", "homeless", 
            "unemployment", "gender inequality"
        ]
        
        # Enhanced regex patterns for better filtering
        self.regex_patterns = {
            "food insecurity": [
                r"\bfood\s*insecurit(y|ies)\b", r"\bhungry\b", r"\bhunger\b", 
                r"\bstarv(ing|ation)\b", r"\bfood\s*bank\b", r"\bSNAP\b", r"\bEBT\b"
            ],
            "housing": [
                r"\bhousing\s*crisis\b", r"\baffordable\s*housing\b", r"\brent\s*crisis\b",
                r"\bhousing\s*shortage\b", r"\beviction\b", r"\blandlord\b", r"\btenant\b"
            ],
            "homeless": [
                r"\bhomeless(ness)?\b", r"\bunhous(ed|ing)\b", r"\bshelter\b",
                r"\brough\s*sleep", r"\bstreet.*sleep", r"\bencampment\b"
            ],
            "unemployment": [
                r"\bunemploy(ed|ment)\b", r"\bjob\s*loss\b", r"\bjobless\b",
                r"\blayoffs?\b", r"\blaid\s*off\b", r"\bfired\b", r"\bunemployment\s*benefits?\b"
            ],
            "gender inequality": [
                r"\bgender\s*inequalit(y|ies)\b", r"\bgender\s*gap\b", r"\bpay\s*gap\b",
                r"\bwage\s*gap\b", r"\bgender\s*discrimination\b", r"\bequal\s*pay\b"
            ]
        }
        
        # Authentication
        self.client = None
        self.authenticate()
        
        # Runtime state
        self.running = False
        self.seen_uris = set()
        self.post_buffer = []
        self.profile_cache = {}
        self.start_time = None
        self.end_time = None
        
        # Statistics
        self.stats = {
            'session_name': self.session_name,
            'start_time': None,
            'end_time': None,
            'duration_seconds': duration_seconds,
            'total_processed': 0,
            'total_relevant': 0,
            'profiles_fetched': 0,
            'profiles_cached': 0,
            'keyword_matches': defaultdict(int),
            'follower_stats': {'min': float('inf'), 'max': 0, 'total': 0, 'count': 0},
            'last_log_time': 0,
            'errors': 0
        }
        
        # Load existing data for deduplication
        self.load_existing_uris()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)
        
        print(f"🚀 Bluesky Social Justice Collector")
        print(f"   Session: {self.session_name}")
        print(f"   Duration: {duration_seconds} seconds ({duration_seconds/60:.1f} minutes)")
        print(f"   Keywords: {', '.join(self.keywords)}")
        print(f"   Authentication: {'✅ Ready' if self.client else '❌ Failed'}")
        print(f"   Existing posts: {len(self.seen_uris):,}")
    
    def load_credentials(self) -> Dict[str, str]:
        """Load Bluesky credentials from secure file"""
        try:
            credentials_file = "data/config/auth.json"
            if os.path.exists(credentials_file):
                with open(credentials_file, 'r', encoding='utf-8') as f:
                    creds = json.load(f)
                
                bluesky_creds = creds.get('bluesky', {})
                username = bluesky_creds.get('username')
                password = bluesky_creds.get('password')
                
                if username and password:
                    return {'username': username, 'password': password}
            
            print("❌ Credentials not found. Please create data/config/auth.json")
            return {}
            
        except Exception as e:
            print(f"❌ Error loading credentials: {e}")
            return {}
    
    def authenticate(self):
        """Authenticate with Bluesky"""
        try:
            creds = self.load_credentials()
            if not creds:
                return
            
            self.client = Client()
            self.client.login(creds['username'], creds['password'])
            print(f"✅ Authenticated as {creds['username']}")
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            self.client = None
    
    def load_existing_uris(self):
        """Load existing URIs from alltime files to avoid duplicates"""
        for keyword in self.keywords:
            keyword_safe = keyword.replace(" ", "_").replace("-", "_")
            alltime_file = os.path.join(self.alltime_dir, f"{keyword_safe}_alltime.jsonl")
            
            if os.path.exists(alltime_file):
                try:
                    with open(alltime_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                post = json.loads(line.strip())
                                uri = post.get('uri')
                                if uri:
                                    self.seen_uris.add(uri)
                            except json.JSONDecodeError:
                                continue
                except Exception:
                    pass
    
    def passes_regex_filter(self, text: str, keyword: str) -> bool:
        """Check if text matches keyword patterns"""
        if keyword not in self.regex_patterns:
            return keyword.lower() in text.lower()
        
        text_lower = text.lower()
        for pattern in self.regex_patterns[keyword]:
            try:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return True
            except re.error:
                if pattern.lower() in text_lower:
                    return True
        return False
    
    def is_relevant_post(self, text: str) -> Optional[str]:
        """Check if post is relevant to any keyword"""
        for keyword in self.keywords:
            if self.passes_regex_filter(text, keyword):
                return keyword
        return None
    
    def get_author_profile(self, author_handle: str, author_did: str) -> Dict:
        """Get comprehensive author profile with follower data"""
        try:
            # Check cache first
            cache_key = f"profile_{author_did}"
            if cache_key in self.profile_cache:
                self.stats['profiles_cached'] += 1
                return self.profile_cache[cache_key]
            
            if not self.client:
                return self._get_profile_fallback()
            
            # Get authenticated profile data
            profile_data = self.client.get_profile(author_handle)
            
            author_info = {
                'display_name': profile_data.display_name or '',
                'description': profile_data.description or '',
                'followers_count': profile_data.followers_count or 0,
                'following_count': profile_data.follows_count or 0,
                'posts_count': profile_data.posts_count or 0,
                'verified': getattr(profile_data, 'verified', False),
                'created_at': getattr(profile_data, 'created_at', ''),
                'avatar': profile_data.avatar or '',
                'banner': getattr(profile_data, 'banner', ''),
                'profile_fetched_at': datetime.now(timezone.utc).isoformat(),
                
                # Calculate derived metrics
                'account_age_days': self._calculate_account_age(getattr(profile_data, 'created_at', '')),
                'posts_per_day': self._calculate_posts_per_day(
                    profile_data.posts_count or 0, 
                    getattr(profile_data, 'created_at', '')
                ),
                'follower_following_ratio': self._calculate_ff_ratio(
                    profile_data.followers_count or 0,
                    profile_data.follows_count or 0
                ),
                'influence_score': self._calculate_influence_score(
                    profile_data.followers_count or 0,
                    profile_data.posts_count or 0,
                    getattr(profile_data, 'verified', False)
                )
            }
            
            # Update follower statistics
            followers = author_info['followers_count']
            if followers > 0:
                self.stats['follower_stats']['min'] = min(self.stats['follower_stats']['min'], followers)
                self.stats['follower_stats']['max'] = max(self.stats['follower_stats']['max'], followers)
                self.stats['follower_stats']['total'] += followers
                self.stats['follower_stats']['count'] += 1
            
            # Cache the result
            self.profile_cache[cache_key] = author_info
            self.stats['profiles_fetched'] += 1
            
            return author_info
            
        except Exception as e:
            return self._get_profile_fallback()
    
    def _calculate_account_age(self, created_at: str) -> int:
        """Calculate account age in days"""
        try:
            if not created_at:
                return 0
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = datetime.now(timezone.utc) - created
            return age.days
        except:
            return 0
    
    def _calculate_posts_per_day(self, posts_count: int, created_at: str) -> float:
        """Calculate average posts per day"""
        try:
            age_days = self._calculate_account_age(created_at)
            if age_days > 0:
                return posts_count / age_days
            return 0
        except:
            return 0
    
    def _calculate_ff_ratio(self, followers: int, following: int) -> float:
        """Calculate follower/following ratio"""
        try:
            if following > 0:
                return followers / following
            return followers
        except:
            return 0
    
    def _calculate_influence_score(self, followers: int, posts: int, verified: bool) -> float:
        """Calculate influence score"""
        try:
            import math
            score = 0
            
            # Follower component (log scale)
            if followers > 0:
                score += math.log10(followers + 1) * 10
            
            # Engagement component
            if posts > 0 and followers > 0:
                engagement_ratio = followers / posts
                score += min(engagement_ratio * 5, 50)
            
            # Verification bonus
            if verified:
                score += 25
            
            return round(score, 2)
        except:
            return 0
    
    def _get_profile_fallback(self) -> Dict:
        """Fallback profile data"""
        return {
            'display_name': '', 'description': '', 'followers_count': 0,
            'following_count': 0, 'posts_count': 0, 'verified': False,
            'created_at': '', 'avatar': '', 'banner': '',
            'profile_fetched_at': datetime.now(timezone.utc).isoformat(),
            'account_age_days': 0, 'posts_per_day': 0,
            'follower_following_ratio': 0, 'influence_score': 0,
            'fetch_error': 'Authentication failed'
        }
    
    def process_post(self, commit, op, resolver) -> Optional[Dict]:
        """Process post with full enhancement"""
        try:
            author_handle = self._resolve_author_handle(commit.repo, resolver)
            author_did = commit.repo
            
            car = CAR.from_bytes(commit.blocks)
            for record in car.blocks.values():
                if isinstance(record, dict) and record.get('$type') == 'app.bsky.feed.post':
                    text = record.get('text', '')
                    if not text or len(text) < 10:
                        return None
                    
                    matched_keyword = self.is_relevant_post(text)
                    if not matched_keyword:
                        return None
                    
                    # Get author profile
                    author_profile = self.get_author_profile(author_handle, author_did)
                    
                    # Extract content features
                    content_features = self._extract_content_features(text, record)
                    
                    post_data = {
                        # Basic post data
                        'uri': f'at://{commit.repo}/{op.path}',
                        'cid': str(op.cid),
                        'text': text,
                        'created_at': record.get('createdAt', ''),
                        'author_handle': author_handle,
                        'author_did': author_did,
                        'keyword': matched_keyword,
                        'session_name': self.session_name,
                        'collected_at': datetime.now(timezone.utc).isoformat(),
                        'lang': record.get('langs', ['en'])[0] if record.get('langs') else 'en',
                        
                        # Author profile data (with auth)
                        **{f'author_{k}': v for k, v in author_profile.items()},
                        
                        # Content analysis
                        **content_features
                    }
                    
                    return post_data
                    
        except Exception:
            self.stats['errors'] += 1
            return None
    
    def _extract_content_features(self, text: str, record: Dict) -> Dict:
        """Extract content features"""
        try:
            words = text.split()
            hashtags = re.findall(r'#\w+', text)
            mentions = re.findall(r'@[\w.-]+', text)
            urls = re.findall(r'http[s]?://[^\s]+', text)
            
            # Emotional indicators
            emotional_words = ['crisis', 'urgent', 'help', 'desperate', 'struggling', 'need', 'support', 'emergency']
            emotion_score = sum(1 for word in emotional_words if word.lower() in text.lower())
            
            # Media detection
            embed = record.get('embed', {})
            has_images = embed.get('$type') == 'app.bsky.embed.images'
            has_external = embed.get('$type') == 'app.bsky.embed.external'
            
            return {
                'word_count': len(words),
                'char_count': len(text),
                'hashtag_count': len(hashtags),
                'mention_count': len(mentions),
                'url_count': len(urls),
                'hashtags': hashtags,
                'mentions': mentions,
                'urls': urls,
                'has_images': has_images,
                'has_external_link': has_external,
                'has_media': has_images or has_external,
                'emotion_score': emotion_score,
                'is_reply': 'reply' in record,
                'content_analyzed_at': datetime.now(timezone.utc).isoformat()
            }
        except Exception:
            return {
                'word_count': 0, 'char_count': 0, 'hashtag_count': 0,
                'mention_count': 0, 'url_count': 0, 'hashtags': [], 'mentions': [], 'urls': [],
                'has_images': False, 'has_external_link': False, 'has_media': False,
                'emotion_score': 0, 'is_reply': False,
                'content_analyzed_at': datetime.now(timezone.utc).isoformat()
            }
    
    def _resolve_author_handle(self, repo, resolver):
        """Resolve author handle from DID"""
        try:
            resolved_info = resolver.did.resolve(repo)
            return resolved_info.also_known_as[0].split('at://')[1] if resolved_info.also_known_as else repo
        except:
            return repo
    
    def save_session_data(self):
        """Save session data to files"""
        if not self.post_buffer:
            return 0
        
        keyword_posts = defaultdict(list)
        for post in self.post_buffer:
            keyword_posts[post['keyword']].append(post)
        
        saved_count = 0
        for keyword, posts in keyword_posts.items():
            keyword_safe = keyword.replace(" ", "_").replace("-", "_")
            
            # Save to session directory
            session_file = os.path.join(self.session_dir, f"{keyword_safe}_posts.jsonl")
            with open(session_file, 'a', encoding='utf-8') as f:
                for post in posts:
                    f.write(json.dumps(post, ensure_ascii=False) + '\n')
                    saved_count += 1
            
            self.stats['keyword_matches'][keyword] += len(posts)
        
        self.post_buffer.clear()
        return saved_count
    
    def update_alltime_data(self):
        """Update alltime files with new session data - FIXED APPEND"""
        updated_keywords = []
        
        for keyword in self.keywords:
            keyword_safe = keyword.replace(" ", "_").replace("-", "_")
            
            # Session file
            session_file = os.path.join(self.session_dir, f"{keyword_safe}_posts.jsonl")
            if not os.path.exists(session_file):
                continue
            
            # Alltime file
            alltime_file = os.path.join(self.alltime_dir, f"{keyword_safe}_alltime.jsonl")
            
            # Read ALL session posts
            session_posts = []
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                post = json.loads(line)
                                session_posts.append(post)
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                print(f"   ⚠️  Error reading session file {session_file}: {e}")
                continue
            
            if not session_posts:
                continue
            
            # Load existing alltime posts and URIs
            existing_uris = set()
            alltime_posts = []
            
            if os.path.exists(alltime_file):
                try:
                    with open(alltime_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    post = json.loads(line)
                                    uri = post.get('uri')
                                    if uri:
                                        existing_uris.add(uri)
                                        alltime_posts.append(post)
                                except json.JSONDecodeError:
                                    continue
                except Exception as e:
                    print(f"   ⚠️  Error reading alltime file {alltime_file}: {e}")
            
            # Find truly new posts
            new_posts = []
            for post in session_posts:
                uri = post.get('uri')
                if uri and uri not in existing_uris:
                    new_posts.append(post)
                    existing_uris.add(uri)
            
            # Append new posts to alltime collection
            if new_posts:
                alltime_posts.extend(new_posts)
                
                # Sort by creation date
                alltime_posts.sort(key=lambda x: x.get('created_at', ''))
                
                # Save updated alltime JSONL (rewrite entire file to ensure consistency)
                with open(alltime_file, 'w', encoding='utf-8') as f:
                    for post in alltime_posts:
                        f.write(json.dumps(post, ensure_ascii=False) + '\n')
                
                # Save alltime CSV
                alltime_csv = os.path.join(self.alltime_dir, f"{keyword_safe}_alltime.csv")
                try:
                    df = pd.DataFrame(alltime_posts)
                    df.to_csv(alltime_csv, index=False, encoding='utf-8')
                except Exception as e:
                    print(f"   ⚠️  Error saving CSV for {keyword}: {e}")
                
                updated_keywords.append(f"{keyword}: +{len(new_posts)} new (total: {len(alltime_posts)})")
        
        # Report updates
        if updated_keywords:
            print("   📊 Alltime files updated:")
            for update in updated_keywords:
                print(f"     {update}")
        else:
            print("   📊 No new posts to add to alltime files")
    
    def log_progress(self, force: bool = False):
        """Log collection progress"""
        now = time.time()
        if not force and (now - self.stats['last_log_time']) < 60:  # Log every minute
            return
        
        self.stats['last_log_time'] = now
        
        elapsed = now - self.start_time
        remaining = max(0, self.duration_seconds - elapsed)
        progress = (elapsed / self.duration_seconds) * 100
        rate = self.stats['total_processed'] / elapsed if elapsed > 0 else 0
        
        remaining_min = int(remaining // 60)
        remaining_sec = int(remaining % 60)
        
        print(f"\n📊 Collection Progress: {progress:.1f}%")
        print(f"   ⏰ Remaining: {remaining_min}m {remaining_sec}s")
        print(f"   📈 Processed: {self.stats['total_processed']:,} posts ({rate:.1f}/sec)")
        print(f"   🎯 Relevant: {self.stats['total_relevant']:,} posts")
        print(f"   👥 Profiles: {self.stats['profiles_fetched']} fetched, {self.stats['profiles_cached']} cached")
        
        # Follower statistics
        if self.stats['follower_stats']['count'] > 0:
            avg_followers = self.stats['follower_stats']['total'] / self.stats['follower_stats']['count']
            print(f"   📊 Followers: avg={avg_followers:.0f}, max={self.stats['follower_stats']['max']:,}")
        
        if self.stats['keyword_matches']:
            print("   🔍 Keywords:")
            for keyword, count in self.stats['keyword_matches'].items():
                print(f"     {keyword}: {count}")
    
    def shutdown_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, stopping collection...")
        self.running = False
    
    def run_firehose_collection(self):
        """Run firehose collection with authentication"""
        try:
            print("🔌 Connecting to Bluesky firehose...")
            
            client = FirehoseSubscribeReposClient()
            resolver = IdResolver(cache=DidInMemoryCache())
            
            def message_handler(message):
                if time.time() >= self.end_time:
                    print(f"\n⏰ Collection time completed ({self.duration_seconds} seconds)")
                    self.running = False
                    client.stop()
                    return
                
                if not self.running:
                    client.stop()
                    return
                
                try:
                    commit = parse_subscribe_repos_message(message)
                    if not hasattr(commit, 'ops'):
                        return
                    
                    for op in commit.ops:
                        if op.action == 'create' and op.path.startswith('app.bsky.feed.post/'):
                            post_data = self.process_post(commit, op, resolver)
                            
                            if post_data:
                                uri = post_data['uri']
                                
                                if uri not in self.seen_uris:
                                    self.seen_uris.add(uri)
                                    self.post_buffer.append(post_data)
                                    self.stats['total_relevant'] += 1
                                    
                                    # Save every 2 minutes or when buffer is full
                                    time_since_last_save = time.time() - getattr(self, 'last_save_time', 0)
                                    if len(self.post_buffer) >= 25 or time_since_last_save >= 120:  # 2 minutes
                                        saved_count = self.save_session_data()
                                        self.update_alltime_data()  # Update alltime files immediately
                                        self.last_save_time = time.time()
                                        if saved_count > 0:
                                            print(f"💾 Saved batch: {saved_count} posts → Updated alltime files")
                            
                            self.stats['total_processed'] += 1
                            self.log_progress()
                            
                except Exception:
                    self.stats['errors'] += 1
            
            print("✅ Connected! Starting social justice data collection...")
            print(f"   Session: {self.session_name}")
            print(f"   Duration: {self.duration_seconds/60:.1f} minutes")
            print(f"   Enhanced features: follower counts, profiles, content analysis")
            
            client.start(message_handler)
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
        
        return True
    
    def run(self):
        """Main collection process"""
        self.running = True
        self.start_time = time.time()
        self.end_time = self.start_time + self.duration_seconds
        self.stats['start_time'] = datetime.now().isoformat()
        
        print(f"\n🚀 Starting Social Justice Data Collection")
        print(f"   Session: {self.session_name}")
        print(f"   Duration: {self.duration_seconds/60:.1f} minutes")
        print(f"   Keywords: {', '.join(self.keywords)}")
        
        try:
            success = self.run_firehose_collection()
            
            if not success:
                print("❌ Collection failed")
                return
                
        except KeyboardInterrupt:
            print("\n🛑 Collection stopped by user")
            self.running = False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        # Cleanup and finalize
        self.cleanup()
    
    def cleanup(self):
        """Final cleanup and data organization"""
        self.stats['end_time'] = datetime.now().isoformat()
        actual_duration = time.time() - self.start_time if self.start_time else 0
        
        print("\n🧹 Finalizing collection...")
        
        # Save any remaining posts
        if self.post_buffer:
            saved_count = self.save_session_data()
            print(f"💾 Saved final batch: {saved_count} posts")
        
        # Update alltime files with ALL session data
        print("🔗 Updating alltime files with complete session data...")
        self.update_alltime_data()
        
        # Generate session summary
        session_summary = {
            'session_name': self.session_name,
            'session_type': 'social_justice_collection',
            'authentication_used': self.client is not None,
            'planned_duration_seconds': self.duration_seconds,
            'actual_duration_seconds': actual_duration,
            'collection_period': {
                'start': self.stats['start_time'],
                'end': self.stats['end_time']
            },
            'statistics': dict(self.stats),
            'keywords': self.keywords,
            'profile_cache_size': len(self.profile_cache)
        }
        
        summary_file = os.path.join(self.session_dir, "session_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(session_summary, f, indent=2, default=str)
        
        # Final summary
        print(f"\n📊 COLLECTION COMPLETE: {self.session_name}")
        print(f"=" * 60)
        print(f"Duration: {actual_duration/60:.1f} minutes")
        print(f"Posts processed: {self.stats['total_processed']:,}")
        print(f"Relevant posts: {self.stats['total_relevant']:,}")
        print(f"Profiles fetched: {self.stats['profiles_fetched']}")
        print(f"Processing rate: {self.stats['total_processed']/actual_duration:.1f} posts/second")
        
        if self.stats['follower_stats']['count'] > 0:
            avg_followers = self.stats['follower_stats']['total'] / self.stats['follower_stats']['count']
            print(f"\n👥 Author Influence:")
            print(f"   Average followers: {avg_followers:.0f}")
            print(f"   Max followers: {self.stats['follower_stats']['max']:,}")
            print(f"   Authors analyzed: {self.stats['follower_stats']['count']}")
        
        if self.stats['keyword_matches']:
            print(f"\n🔍 Keywords collected:")
            for keyword, count in self.stats['keyword_matches'].items():
                print(f"   {keyword}: {count} posts")
        
        print(f"\n📁 Data saved to:")
        print(f"   Session: {self.session_dir}/")
        print(f"   Alltime: {self.alltime_dir}/")
        
        print("✅ Social justice data collection completed")


def main():
    parser = argparse.ArgumentParser(description="Bluesky Social Justice Data Collector")
    
    parser.add_argument('--duration', type=int, required=True,
                       help='Collection duration in seconds')
    parser.add_argument('--session_name', type=str,
                       help='Custom session name (default: auto-generated)')
    
    args = parser.parse_args()
    
    # Initialize and run collector
    collector = BlueskySocialJusticeCollector(
        duration_seconds=args.duration,
        session_name=args.session_name
    )
    
    collector.run()


if __name__ == "__main__":
    main()
