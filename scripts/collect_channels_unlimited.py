"""
Unlimited Sri Lankan YouTube Channel Discovery System
Discovers 10,000+ Sri Lankan YouTube channels using advanced strategies and intelligent keyword expansion
Features quota-efficient processing, deduplication, and progressive discovery
"""

import os
import sys
import json
import time
import random
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict, Counter
import hashlib

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from dotenv import load_dotenv
    import requests
except ImportError as e:
    print(f"Required packages not installed: {e}")
    print("Install with: pip install google-api-python-client python-dotenv requests")
    exit(1)

# Import project modules
from config import (
    DATA_RAW_PATH,
    validate_api_key,
)

from utils import setup_logging

# Setup logging
logger = setup_logging()

class AdvancedKeywordEngine:
    """Advanced keyword expansion system for unlimited channel discovery"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.keywords_db_file = data_dir / "keywords_database.json"
        self.performance_file = data_dir / "keyword_performance.json"
        
        # Load or initialize keyword database
        self.keywords_db = self._load_keywords_database()
        self.performance_metrics = self._load_performance_metrics()
        
        # Comprehensive Sri Lankan keyword base
        self.base_keywords = self._get_comprehensive_base_keywords()
        
    def _get_comprehensive_base_keywords(self) -> List[str]:
        """Get comprehensive base keywords for Sri Lankan content"""
        return [
            # Core terms
            "sri lanka", "srilanka", "ceylon", "lanka", "lankan",
            
            # Languages
            "sinhala", "sinhalese", "tamil", "sinhalen", "தமிழ்", "සිංහල",
            
            # Major cities (all 25 districts)
            "colombo", "kandy", "galle", "jaffna", "trincomalee", "anuradhapura",
            "polonnaruwa", "kurunegala", "ratnapura", "badulla", "matara",
            "negombo", "batticaloa", "puttalam", "kalutara", "gampaha",
            "hambantota", "monaragala", "nuwara eliya", "kegalle", "vavuniya",
            "mannar", "mullaitivu", "kilinochchi", "ampara",
            
            # Cultural terms
            "avurudu", "vesak", "poson", "esala perahera", "kataragama",
            "adam's peak", "poya", "sinhala new year", "tamil new year",
            
            # Food & cuisine
            "kottu", "hoppers", "string hoppers", "pol sambol", "parippu",
            "rice and curry", "dhal curry", "fish curry", "roti", "pittu",
            
            # Popular phrases & slang
            "machang", "aiya", "nangi", "patta", "ado", "malli", "akka",
            "amma", "thatha", "putha", "duwa", "api lankawa", "mage yalu",
            
            # Landmarks & attractions
            "sigiriya", "dambulla", "ella", "temple of tooth", "lotus tower",
            "independence square", "mount lavinia", "bentota", "hikkaduwa",
            "mirissa", "unawatuna", "yala", "udawalawe", "horton plains",
            
            # Content categories
            "news", "music", "comedy", "drama", "teledrama", "film", "movie",
            "cooking", "travel", "vlog", "tutorial", "education", "tech",
            "cricket", "sports", "politics", "election", "festival", "wedding",
            
            # Media & channels
            "tv", "radio", "live", "breaking", "latest", "today", "now",
            "viral", "trending", "popular", "hit", "best", "top",
            
            # Gaming
            "lion kolla", "maniya",
            
            # Political
            "sri lankan politics", "sri lankan election", "sri lankan government", "mahinda rajapaksa",
            "ranil wickremesinghe", "sajith premadasa", "gotabaya rajapaksa", "sri lankan parliament",
        ]
    
    def _load_keywords_database(self) -> Dict:
        """Load keyword database with performance metrics"""
        if self.keywords_db_file.exists():
            try:
                with open(self.keywords_db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading keywords database: {e}")
        
        return {
            "keywords": {},
            "last_updated": datetime.now().isoformat(),
            "total_keywords": 0,
            "active_keywords": 0
        }
    
    def _load_performance_metrics(self) -> Dict:
        """Load keyword performance metrics"""
        if self.performance_file.exists():
            try:
                with open(self.performance_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading performance metrics: {e}")
        
        return {
            "discovery_methods": {},
            "keyword_success_rates": {},
            "last_analysis": datetime.now().isoformat()
        }
    
    def get_youtube_autocomplete(self, query: str, max_suggestions: int = 10) -> List[str]:
        """Get YouTube autocomplete suggestions"""
        try:
            url = "https://suggestqueries.google.com/complete/search"
            params = {
                'client': 'firefox',
                'ds': 'yt',
                'q': query
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                suggestions = response.json()[1][:max_suggestions]
                return [s for s in suggestions if s.lower() != query.lower()]
            
        except Exception as e:
            logger.debug(f"Error getting autocomplete for '{query}': {e}")
        
        return []
    
    def expand_keywords_comprehensive(self) -> List[str]:
        """Comprehensive keyword expansion using multiple methods"""
        logger.info("Starting comprehensive keyword expansion...")
        
        all_keywords = set(self.base_keywords)
        
        # Method 1: Autocomplete expansion
        logger.info("Expanding via YouTube autocomplete...")
        for base_keyword in self.base_keywords[:30]:  # Limit to prevent rate limiting
            suggestions = self.get_youtube_autocomplete(base_keyword)
            for suggestion in suggestions:
                if self._is_sri_lankan_relevant(suggestion):
                    all_keywords.add(suggestion)
            time.sleep(0.1)  # Rate limiting
        
        # Method 2: Geographic combinations
        logger.info("Generating geographic combinations...")
        locations = [
            "colombo", "kandy", "galle", "jaffna", "negombo", "matara",
            "anuradhapura", "polonnaruwa", "trincomalee", "batticaloa"
        ]
        
        topics = [
            "vlog", "travel", "food", "news", "music", "comedy", "drama",
            "wedding", "festival", "cricket", "election", "review"
        ]
        
        for location in locations:
            for topic in topics:
                all_keywords.update([
                    f"{location} {topic}",
                    f"{topic} {location}",
                    f"{location} sri lanka",
                    f"sri lanka {location}"
                ])
        
        # Method 3: Cultural combinations
        logger.info("Generating cultural combinations...")
        cultural_terms = ["sinhala", "tamil", "lankan", "ceylon"]
        content_types = [
            "songs", "movies", "drama", "comedy", "news", "music",
            "dance", "wedding", "cooking", "travel", "vlog"
        ]
        
        for cultural in cultural_terms:
            for content in content_types:
                all_keywords.update([
                    f"{cultural} {content}",
                    f"{content} {cultural}",
                    f"best {cultural} {content}",
                    f"latest {cultural} {content}",
                    f"popular {cultural} {content}"
                ])
        
        # Method 4: Trending patterns
        logger.info("Generating trending patterns...")
        trending_prefixes = ["latest", "new", "viral", "trending", "popular", "best", "top"]
        trending_suffixes = ["2024", "2025", "today", "now", "live"]
        
        for prefix in trending_prefixes:
            for suffix in trending_suffixes:
                all_keywords.update([
                    f"{prefix} sri lanka {suffix}",
                    f"{prefix} sinhala {suffix}",
                    f"{prefix} tamil {suffix}"
                ])
        
        # Update keywords database
        self._update_keywords_database(list(all_keywords))
        
        logger.info(f"Keyword expansion complete: {len(self.base_keywords)} → {len(all_keywords)} keywords")
        return list(all_keywords)
    
    def _is_sri_lankan_relevant(self, text: str) -> bool:
        """Check if text is relevant to Sri Lankan content"""
        text_lower = text.lower()
        sri_lankan_indicators = [
            'sri lanka', 'srilanka', 'lanka', 'sinhala', 'tamil', 'ceylon',
            'colombo', 'kandy', 'galle', 'jaffna', 'lankan'
        ]
        return any(indicator in text_lower for indicator in sri_lankan_indicators)
    
    def _update_keywords_database(self, keywords: List[str]):
        """Update keywords database with new keywords"""
        current_time = datetime.now().isoformat()
        
        for keyword in keywords:
            if keyword not in self.keywords_db["keywords"]:
                self.keywords_db["keywords"][keyword] = {
                    "added_date": current_time,
                    "success_rate": 0.0,
                    "channels_found": 0,
                    "last_used": None,
                    "active": True
                }
        
        self.keywords_db["total_keywords"] = len(self.keywords_db["keywords"])
        self.keywords_db["active_keywords"] = sum(
            1 for k in self.keywords_db["keywords"].values() if k["active"]
        )
        self.keywords_db["last_updated"] = current_time
        
        # Save to file
        with open(self.keywords_db_file, 'w', encoding='utf-8') as f:
            json.dump(self.keywords_db, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Updated keywords database with {len(keywords)} keywords")
    
    def get_high_performance_keywords(self, limit: int = 200) -> List[str]:
        """Get keywords with highest success rates"""
        keywords_with_performance = []
        
        for keyword, data in self.keywords_db["keywords"].items():
            if data["active"]:
                # Calculate performance score
                success_rate = data.get("success_rate", 0.0)
                channels_found = data.get("channels_found", 0)
                recency_bonus = 1.0 if data.get("last_used") is None else 0.5
                
                performance_score = (success_rate * 0.7) + (min(channels_found, 10) * 0.02) + recency_bonus
                keywords_with_performance.append((keyword, performance_score))
        
        # Sort by performance score and return top keywords
        keywords_with_performance.sort(key=lambda x: x[1], reverse=True)
        return [kw[0] for kw in keywords_with_performance[:limit]]
    
    def update_keyword_performance(self, keyword: str, channels_found: int):
        """Update performance metrics for a keyword"""
        if keyword in self.keywords_db["keywords"]:
            data = self.keywords_db["keywords"][keyword]
            
            # Update metrics
            total_uses = data.get("total_uses", 0) + 1
            total_channels = data.get("channels_found", 0) + channels_found
            
            data["total_uses"] = total_uses
            data["channels_found"] = total_channels
            data["success_rate"] = channels_found / total_uses if total_uses > 0 else 0.0
            data["last_used"] = datetime.now().isoformat()
            
            # Deactivate keywords with consistently poor performance
            if total_uses >= 5 and data["success_rate"] < 0.1:
                data["active"] = False
                logger.info(f"Deactivated low-performing keyword: {keyword}")

class UnlimitedChannelDiscovery:
    """Main class for unlimited Sri Lankan YouTube channel discovery"""
    
    def __init__(self, output_dir: str = None, target_channels: int = 10000):
        # Validate API key
        if not validate_api_key():
            raise ValueError("Invalid or missing YouTube API key. Please check your .env file.")
        
        self.api_manager = self._initialize_api_manager()
        self.target_channels = target_channels
        
        # Setup directories
        if output_dir is None:
            output_dir = DATA_RAW_PATH
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Files
        self.channels_file = self.output_dir / "discovered_channels.json"
        self.progress_file = self.output_dir / "discovery_progress.json"
        self.detailed_channels_dir = self.output_dir / "detailed_channels"
        self.detailed_channels_dir.mkdir(exist_ok=True)
        
        # Load existing data
        self.existing_channels = self._load_existing_channels()
        self.progress = self._load_progress()
        
        # Initialize keyword engine
        self.keyword_engine = AdvancedKeywordEngine(self.output_dir)
        
        # Discovery statistics
        self.stats = {
            'session_start': datetime.now().isoformat(),
            'channels_at_start': len(self.existing_channels),
            'target_channels': target_channels,
            'discovered_this_session': 0,
            'api_calls_made': 0,
            'errors_encountered': 0,
            'keywords_processed': 0,
            'quota_exhausted_count': 0
        }
        
        logger.info(f"Initialized discovery system. Current channels: {len(self.existing_channels)}, Target: {target_channels}")
    
    def _initialize_api_manager(self):
        """Initialize API manager with multiple keys"""
        from collect_channels import YouTubeAPIManager
        return YouTubeAPIManager()
    
    def _load_existing_channels(self) -> Dict[str, Dict]:
        """Load existing channels from JSON file"""
        if self.channels_file.exists():
            try:
                with open(self.channels_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Convert nested structure to flat dict for easy lookup
                existing = {}
                for category, channels in data.items():
                    for channel_name, channel_id in channels.items():
                        existing[channel_id] = {
                            'name': channel_name,
                            'category': category,
                            'id': channel_id
                        }
                
                logger.info(f"Loaded {len(existing)} existing channels")
                return existing
            except Exception as e:
                logger.error(f"Error loading existing channels: {e}")
        
        return {}
    
    def _load_progress(self) -> Dict:
        """Load discovery progress"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading progress: {e}")
        
        return {
            'last_session': None,
            'total_sessions': 0,
            'keywords_processed': [],
            'discovery_methods_used': [],
            'last_checkpoint': datetime.now().isoformat()
        }
    
    def _save_progress(self):
        """Save current progress"""
        self.progress['last_session'] = datetime.now().isoformat()
        self.progress['total_sessions'] += 1
        self.progress['last_checkpoint'] = datetime.now().isoformat()
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
    
    def _calculate_sri_lankan_score(self, channel_data: Dict) -> float:
        """Calculate Sri Lankan relevance score"""
        score = 0.0
        
        # Combine text fields for analysis
        text_fields = [
            channel_data.get('title', '').lower(),
            channel_data.get('description', '').lower(),
            ' '.join(channel_data.get('keywords', [])).lower(),
            channel_data.get('country', '').lower()
        ]
        
        combined_text = ' '.join(text_fields)
        
        # High-value indicators
        high_value = ['sri lanka', 'srilanka', 'ceylon', 'lanka']
        for indicator in high_value:
            if indicator in combined_text:
                score += 3.0
        
        # Medium-value indicators
        medium_value = ['colombo', 'kandy', 'galle', 'jaffna', 'sinhala', 'tamil']
        for indicator in medium_value:
            if indicator in combined_text:
                score += 2.0
        
        # Cultural indicators
        cultural = ['lankan', 'ape', 'mage', 'machang', 'aiya', 'nangi']
        for indicator in cultural:
            if indicator in combined_text:
                score += 1.5
        
        # Country code bonus
        if channel_data.get('country', '').upper() == 'LK':
            score += 5.0
        
        # Language bonus
        if channel_data.get('defaultLanguage', '').lower() in ['si', 'ta', 'en']:
            score += 1.0
        
        return score
    
    def _get_channel_details_batch(self, channel_ids: List[str]) -> List[Dict]:
        """Get detailed information for a batch of channel IDs"""
        if not channel_ids:
            return []
        
        # Check if API service is available
        if not hasattr(self.api_manager, 'service') or self.api_manager.service is None:
            logger.error("API service not available - all keys exhausted")
            raise Exception("All API keys exhausted")
        
        channels = []
        batch_size = 50
        
        for i in range(0, len(channel_ids), batch_size):
            batch_ids = channel_ids[i:i + batch_size]
            
            try:
                response = self.api_manager.make_request(
                    self.api_manager.service.channels().list,
                    part='snippet,statistics,brandingSettings',
                    id=','.join(batch_ids),
                    maxResults=50
                )
                
                self.stats['api_calls_made'] += 1
                
                for item in response.get('items', []):
                    snippet = item.get('snippet', {})
                    statistics = item.get('statistics', {})
                    branding = item.get('brandingSettings', {}).get('channel', {})
                    
                    channel_data = {
                        'channel_id': item['id'],
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', ''),
                        'subscriber_count': int(statistics.get('subscriberCount', 0)),
                        'video_count': int(statistics.get('videoCount', 0)),
                        'view_count': int(statistics.get('viewCount', 0)),
                        'published_at': snippet.get('publishedAt', ''),
                        'country': snippet.get('country', ''),
                        'custom_url': snippet.get('customUrl', ''),
                        'defaultLanguage': snippet.get('defaultLanguage', ''),
                        'keywords': branding.get('keywords', '').split(',') if branding.get('keywords') else [],
                        'thumbnail_url': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                        'discovered_at': datetime.now().isoformat(),
                        'sri_lankan_score': 0.0
                    }
                    
                    # Calculate Sri Lankan relevance score
                    channel_data['sri_lankan_score'] = self._calculate_sri_lankan_score(channel_data)
                    
                    channels.append(channel_data)
                
                # Rate limiting
                time.sleep(random.uniform(0.1, 0.3))
                
            except Exception as e:
                logger.error(f"Error getting channel details for batch: {e}")
                self.stats['errors_encountered'] += 1
                
                if "All API keys exhausted" in str(e) or "quotaExceeded" in str(e):
                    self.stats['quota_exhausted_count'] += 1
                    logger.warning("Quota exhausted during channel details retrieval")
                    raise Exception("All API keys exhausted")
                
                time.sleep(random.uniform(1, 3))
        
        return channels
    
    def search_channels_by_keywords(self, keywords: List[str], max_per_keyword: int = 50) -> List[str]:
        """Search for channels using keywords with deduplication"""
        logger.info(f"Searching channels with {len(keywords)} keywords...")
        
        # Check if API service is available
        if not hasattr(self.api_manager, 'service') or self.api_manager.service is None:
            logger.error("API service not available - all keys exhausted")
            raise Exception("All API keys exhausted")
        
        new_channel_ids = set()
        processed_keywords = 0
        
        for keyword in keywords:
            if len(self.existing_channels) + len(new_channel_ids) >= self.target_channels:
                logger.info(f"Target of {self.target_channels} channels reached!")
                break
            
            try:
                # Search for channels
                response = self.api_manager.make_request(
                    self.api_manager.service.search().list,
                    part='snippet',
                    q=keyword,
                    type='channel',
                    regionCode='LK',
                    maxResults=min(max_per_keyword, 50),
                    order='relevance'
                )
                
                self.stats['api_calls_made'] += 1
                processed_keywords += 1
                
                keyword_channels_found = 0
                for item in response.get('items', []):
                    if item['id']['kind'] == 'youtube#channel':
                        channel_id = item['id']['channelId']
                        
                        # Skip if already exists
                        if channel_id not in self.existing_channels:
                            new_channel_ids.add(channel_id)
                            keyword_channels_found += 1
                
                # Update keyword performance
                self.keyword_engine.update_keyword_performance(keyword, keyword_channels_found)
                
                logger.debug(f"Keyword '{keyword}': {keyword_channels_found} new channels")
                time.sleep(random.uniform(0.3, 0.7))
                
            except Exception as e:
                logger.error(f"Error searching for keyword '{keyword}': {e}")
                self.stats['errors_encountered'] += 1
                
                if "All API keys exhausted" in str(e) or "quotaExceeded" in str(e):
                    logger.warning("All API keys exhausted, stopping keyword search")
                    self.stats['quota_exhausted_count'] += 1
                    raise Exception("All API keys exhausted")
        
        self.stats['keywords_processed'] += processed_keywords
        logger.info(f"Keyword search complete: {len(new_channel_ids)} new channels found")
        return list(new_channel_ids)
    
    def discover_related_channels_deep(self, seed_channel_ids: List[str], depth: int = 2) -> List[str]:
        """Deep discovery of related channels through multiple levels"""
        logger.info(f"Deep related channel discovery from {len(seed_channel_ids)} seeds, depth: {depth}")
        
        all_related = set()
        current_level = set(seed_channel_ids[:20])  # Start with limited seeds
        
        for level in range(depth):
            logger.info(f"Processing level {level + 1}/{depth} with {len(current_level)} channels")
            next_level = set()
            
            for seed_id in current_level:
                if len(all_related) >= 1000:  # Limit to prevent excessive API usage
                    break
                
                try:
                    # Get recent videos from seed channel
                    videos_response = self.api_manager.make_request(
                        self.api_manager.service.search().list,
                        part='snippet',
                        channelId=seed_id,
                        type='video',
                        order='date',
                        maxResults=10
                    )
                    
                    self.stats['api_calls_made'] += 1
                    
                    # Extract channel IDs from video comments
                    for video in videos_response.get('items', []):
                        video_id = video['id']['videoId']
                        
                        try:
                            comments_response = self.api_manager.make_request(
                                self.api_manager.service.commentThreads().list,
                                part='snippet',
                                videoId=video_id,
                                maxResults=30,
                                order='relevance'
                            )
                            
                            self.stats['api_calls_made'] += 1
                            
                            for comment in comments_response.get('items', []):
                                author_channel_id = comment['snippet']['topLevelComment']['snippet'].get('authorChannelId', {}).get('value')
                                if (author_channel_id and 
                                    author_channel_id not in self.existing_channels and
                                    author_channel_id not in all_related):
                                    all_related.add(author_channel_id)
                                    next_level.add(author_channel_id)
                            
                            time.sleep(random.uniform(0.2, 0.5))
                            
                        except Exception as e:
                            logger.debug(f"Could not get comments for video {video_id}: {e}")
                            continue
                    
                except Exception as e:
                    logger.debug(f"Error processing seed channel {seed_id}: {e}")
                    continue
            
            current_level = next_level
            if not current_level:
                break
        
        logger.info(f"Deep related discovery found {len(all_related)} channels")
        return list(all_related)
    
    def discover_from_playlists(self, seed_channel_ids: List[str]) -> List[str]:
        """Discover channels from collaborative playlists"""
        logger.info(f"Discovering channels from playlists of {len(seed_channel_ids)} seed channels")
        
        playlist_channel_ids = set()
        
        for seed_id in seed_channel_ids[:15]:  # Limit to prevent excessive API usage
            try:
                # Get playlists from seed channel
                playlists_response = self.api_manager.make_request(
                    self.api_manager.service.playlists().list,
                    part='snippet',
                    channelId=seed_id,
                    maxResults=10
                )
                
                self.stats['api_calls_made'] += 1
                
                for playlist in playlists_response.get('items', []):
                    playlist_id = playlist['id']
                    
                    try:
                        # Get playlist items to find other channels
                        playlist_items_response = self.api_manager.make_request(
                            self.api_manager.service.playlistItems().list,
                            part='snippet',
                            playlistId=playlist_id,
                            maxResults=50
                        )
                        
                        self.stats['api_calls_made'] += 1
                        
                        for item in playlist_items_response.get('items', []):
                            channel_id = item['snippet'].get('videoOwnerChannelId')
                            if (channel_id and 
                                channel_id not in self.existing_channels and
                                channel_id != seed_id):
                                playlist_channel_ids.add(channel_id)
                        
                        time.sleep(random.uniform(0.3, 0.6))
                        
                    except Exception as e:
                        logger.debug(f"Could not get playlist items for {playlist_id}: {e}")
                        continue
                
            except Exception as e:
                logger.debug(f"Error getting playlists for channel {seed_id}: {e}")
                continue
        
        logger.info(f"Playlist discovery found {len(playlist_channel_ids)} channels")
        return list(playlist_channel_ids)
    
    def discover_from_hashtags(self) -> List[str]:
        """Discover channels using Sri Lankan hashtags"""
        logger.info("Discovering channels from Sri Lankan hashtags")
        
        # Check if API service is available
        if not hasattr(self.api_manager, 'service') or self.api_manager.service is None:
            logger.error("API service not available - all keys exhausted")
            raise Exception("All API keys exhausted")
        
        hashtag_channel_ids = set()
        
        # Sri Lankan hashtags
        hashtags = [
            "#SriLanka", "#LKA", "#Ceylon", "#Sinhala", "#Tamil", "#Colombo",
            "#Kandy", "#Galle", "#SriLankanFood", "#LankanCricket", "#VisitSriLanka",
            "#SinhalaMusic", "#TamilMusic", "#LankanNews", "#SriLankanWedding",
            "#Avurudu", "#Vesak", "#SriLankanCulture", "#LankanVlog", "#SriLankanComedy"
        ]
        
        for hashtag in hashtags:
            try:
                # Search for videos with hashtag
                response = self.api_manager.make_request(
                    self.api_manager.service.search().list,
                    part='snippet',
                    q=hashtag,
                    type='video',
                    regionCode='LK',
                    maxResults=30,
                    order='relevance'
                )
                
                self.stats['api_calls_made'] += 1
                
                for item in response.get('items', []):
                    channel_id = item['snippet']['channelId']
                    if channel_id not in self.existing_channels:
                        hashtag_channel_ids.add(channel_id)
                
                time.sleep(random.uniform(0.4, 0.8))
                
            except Exception as e:
                logger.error(f"Error searching for hashtag '{hashtag}': {e}")
                if "All API keys exhausted" in str(e) or "quotaExceeded" in str(e):
                    raise Exception("All API keys exhausted")
        
        logger.info(f"Hashtag discovery found {len(hashtag_channel_ids)} channels")
        return list(hashtag_channel_ids)
    
    def discover_time_based_patterns(self) -> List[str]:
        """Discover channels based on time-based patterns (recent uploads, trending times)"""
        logger.info("Discovering channels using time-based patterns")
        
        # Check if API service is available
        if not hasattr(self.api_manager, 'service') or self.api_manager.service is None:
            logger.error("API service not available - all keys exhausted")
            raise Exception("All API keys exhausted")
        
        time_based_channel_ids = set()
        
        # Different time periods to search
        time_periods = [
            (datetime.now() - timedelta(days=1), "last 24 hours"),
            (datetime.now() - timedelta(days=7), "last week"),
            (datetime.now() - timedelta(days=30), "last month")
        ]
        
        search_terms = [
            "sri lanka latest", "sinhala new", "tamil recent", "lanka today",
            "colombo now", "breaking sri lanka", "viral lanka"
        ]
        
        for period_start, period_name in time_periods:
            logger.info(f"Searching for channels active in {period_name}")
            
            for term in search_terms[:3]:  # Limit to prevent quota exhaustion
                try:
                    response = self.api_manager.make_request(
                        self.api_manager.service.search().list,
                        part='snippet',
                        q=term,
                        type='video',
                        regionCode='LK',
                        publishedAfter=period_start.isoformat() + 'Z',
                        maxResults=25,
                        order='relevance'
                    )
                    
                    self.stats['api_calls_made'] += 1
                    
                    for item in response.get('items', []):
                        channel_id = item['snippet']['channelId']
                        if channel_id not in self.existing_channels:
                            time_based_channel_ids.add(channel_id)
                    
                    time.sleep(random.uniform(0.3, 0.6))
                    
                except Exception as e:
                    logger.error(f"Error in time-based search for '{term}': {e}")
                    if "All API keys exhausted" in str(e) or "quotaExceeded" in str(e):
                        raise Exception("All API keys exhausted")
        
        logger.info(f"Time-based discovery found {len(time_based_channel_ids)} channels")
        return list(time_based_channel_ids)
    
    def categorize_channel_smart(self, channel_data: Dict) -> str:
        """Smart channel categorization using content analysis"""
        
        # YouTube category mapping
        YOUTUBE_CATEGORIES = {
            1: "Film & Animation", 2: "Autos & Vehicles", 10: "Music",
            15: "Pets & Animals", 17: "Sports", 19: "Travel & Events",
            20: "Gaming", 22: "People & Blogs", 23: "Comedy",
            24: "Entertainment", 25: "News & Politics", 26: "Howto & Style",
            27: "Education", 28: "Science & Technology"
        }
        
        # Try to get category from recent videos
        try:
            videos_response = self.api_manager.make_request(
                self.api_manager.service.search().list,
                part='snippet',
                channelId=channel_data['channel_id'],
                type='video',
                order='date',
                maxResults=5
            )
            
            self.stats['api_calls_made'] += 1
            
            video_ids = [item['id']['videoId'] for item in videos_response.get('items', [])]
            
            if video_ids:
                videos_details = self.api_manager.make_request(
                    self.api_manager.service.videos().list,
                    part='snippet',
                    id=','.join(video_ids)
                )
                
                self.stats['api_calls_made'] += 1
                
                # Get most common category from videos
                category_counts = Counter()
                for video in videos_details.get('items', []):
                    category_id = int(video['snippet'].get('categoryId', 22))
                    category_counts[category_id] += 1
                
                if category_counts:
                    most_common_category = category_counts.most_common(1)[0][0]
                    return YOUTUBE_CATEGORIES.get(most_common_category, "People & Blogs")
        
        except Exception as e:
            logger.debug(f"Could not analyze videos for categorization: {e}")
        
        # Fallback to text-based categorization
        text_content = ' '.join([
            channel_data.get('title', '').lower(),
            channel_data.get('description', '').lower(),
            ' '.join(channel_data.get('keywords', [])).lower()
        ])
        
        # Category keyword mapping
        category_keywords = {
            "News & Politics": ['news', 'politics', 'current', 'breaking', 'report', 'media', 'election'],
            "Music": ['music', 'song', 'singer', 'band', 'album', 'musical', 'concert'],
            "Entertainment": ['entertainment', 'comedy', 'drama', 'show', 'movie', 'film', 'teledrama'],
            "Education": ['education', 'learn', 'tutorial', 'teach', 'lesson', 'study', 'school'],
            "Sports": ['sports', 'cricket', 'football', 'game', 'match', 'player', 'team'],
            "Gaming": ['gaming', 'game', 'play', 'gamer', 'gameplay', 'esports'],
            "Travel & Events": ['travel', 'trip', 'tour', 'visit', 'journey', 'event', 'festival'],
            "Howto & Style": ['howto', 'how to', 'style', 'fashion', 'beauty', 'makeup', 'cooking'],
            "Science & Technology": ['tech', 'technology', 'science', 'computer', 'software', 'ai'],
        }
        
        # Score each category
        best_category = "People & Blogs"  # default
        best_score = 0
        
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_content)
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category
    
    def save_channels_incremental(self, new_channels: List[Dict]):
        """Save new channels incrementally to avoid data loss"""
        if not new_channels:
            return
        
        # Load current data
        if self.channels_file.exists():
            with open(self.channels_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        # Add new channels by category
        channels_added = 0
        for channel in new_channels:
            category = channel.get('category', 'People & Blogs')
            if category not in data:
                data[category] = {}
            
            # Only add if not already exists
            if channel['channel_id'] not in self.existing_channels:
                data[category][channel['title']] = channel['channel_id']
                self.existing_channels[channel['channel_id']] = {
                    'name': channel['title'],
                    'category': category,
                    'id': channel['channel_id']
                }
                channels_added += 1
        
        # Save updated data
        with open(self.channels_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save detailed data for analysis
        if channels_added > 0:
            detailed_file = self.detailed_channels_dir / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(detailed_file, 'w', encoding='utf-8') as f:
                json.dump(new_channels, f, indent=2, ensure_ascii=False)
        
        self.stats['discovered_this_session'] += channels_added
        logger.info(f"Saved {channels_added} new channels. Total: {len(self.existing_channels)}")
        
        # Save progress
        self._save_progress()
    
    def run_unlimited_discovery(self) -> Dict:
        """Run unlimited discovery until target is reached or quota exhausted"""
        logger.info(f"Starting unlimited discovery. Target: {self.target_channels}, Current: {len(self.existing_channels)}")
        
        try:
            while len(self.existing_channels) < self.target_channels:
                logger.info(f"Discovery cycle - Current: {len(self.existing_channels)}/{self.target_channels}")
                
                try:
                    # Phase 1: Keyword expansion and search
                    logger.info("Phase 1: Keyword-based discovery")
                    expanded_keywords = self.keyword_engine.expand_keywords_comprehensive()
                    high_performance_keywords = self.keyword_engine.get_high_performance_keywords(limit=100)
                    
                    # Use high-performance keywords first, then expanded keywords
                    all_keywords = high_performance_keywords + [kw for kw in expanded_keywords if kw not in high_performance_keywords]
                    
                    # Search with keywords
                    keyword_channel_ids = self.search_channels_by_keywords(all_keywords[:200], max_per_keyword=25)
                    
                    if keyword_channel_ids:
                        # Get detailed information
                        detailed_channels = self._get_channel_details_batch(keyword_channel_ids)
                        
                        # Filter for Sri Lankan channels
                        sri_lankan_channels = [
                            ch for ch in detailed_channels 
                            if ch['sri_lankan_score'] >= 1.0
                        ]
                        
                        # Categorize channels
                        for channel in sri_lankan_channels:
                            channel['category'] = self.categorize_channel_smart(channel)
                            channel['discovery_method'] = 'keyword_search'
                        
                        # Save incrementally
                        self.save_channels_incremental(sri_lankan_channels)
                    
                    # Check if target reached
                    if len(self.existing_channels) >= self.target_channels:
                        break
                    
                    # Phase 2: Deep related channel discovery
                    logger.info("Phase 2: Deep related channel discovery")
                    seed_channels = list(self.existing_channels.keys())[-50:]  # Use recent discoveries as seeds
                    related_channel_ids = self.discover_related_channels_deep(seed_channels, depth=2)
                    
                    if related_channel_ids:
                        # Get detailed information
                        detailed_channels = self._get_channel_details_batch(related_channel_ids)
                        
                        # Filter for Sri Lankan channels
                        sri_lankan_channels = [
                            ch for ch in detailed_channels 
                            if ch['sri_lankan_score'] >= 1.0
                        ]
                        
                        # Categorize channels
                        for channel in sri_lankan_channels:
                            channel['category'] = self.categorize_channel_smart(channel)
                            channel['discovery_method'] = 'related_channels'
                        
                        # Save incrementally
                        self.save_channels_incremental(sri_lankan_channels)
                    
                    # Check if target reached
                    if len(self.existing_channels) >= self.target_channels:
                        break
                    
                    # Phase 3: Playlist-based discovery
                    logger.info("Phase 3: Playlist-based discovery")
                    seed_channels_for_playlists = list(self.existing_channels.keys())[-30:]
                    playlist_channel_ids = self.discover_from_playlists(seed_channels_for_playlists)
                    
                    if playlist_channel_ids:
                        # Get detailed information
                        detailed_channels = self._get_channel_details_batch(playlist_channel_ids)
                        
                        # Filter for Sri Lankan channels
                        sri_lankan_channels = [
                            ch for ch in detailed_channels 
                            if ch['sri_lankan_score'] >= 1.0
                        ]
                        
                        # Categorize channels
                        for channel in sri_lankan_channels:
                            channel['category'] = self.categorize_channel_smart(channel)
                            channel['discovery_method'] = 'playlist_analysis'
                        
                        # Save incrementally
                        self.save_channels_incremental(sri_lankan_channels)
                    
                    # Check if target reached
                    if len(self.existing_channels) >= self.target_channels:
                        break
                    
                    # Phase 4: Hashtag-based discovery
                    logger.info("Phase 4: Hashtag-based discovery")
                    hashtag_channel_ids = self.discover_from_hashtags()
                    
                    if hashtag_channel_ids:
                        # Get detailed information
                        detailed_channels = self._get_channel_details_batch(hashtag_channel_ids)
                        
                        # Filter for Sri Lankan channels
                        sri_lankan_channels = [
                            ch for ch in detailed_channels 
                            if ch['sri_lankan_score'] >= 1.0
                        ]
                        
                        # Categorize channels
                        for channel in sri_lankan_channels:
                            channel['category'] = self.categorize_channel_smart(channel)
                            channel['discovery_method'] = 'hashtag_tracking'
                        
                        # Save incrementally
                        self.save_channels_incremental(sri_lankan_channels)
                    
                    # Check if target reached
                    if len(self.existing_channels) >= self.target_channels:
                        break
                    
                    # Phase 5: Time-based pattern discovery
                    logger.info("Phase 5: Time-based pattern discovery")
                    time_based_channel_ids = self.discover_time_based_patterns()
                    
                    if time_based_channel_ids:
                        # Get detailed information
                        detailed_channels = self._get_channel_details_batch(time_based_channel_ids)
                        
                        # Filter for Sri Lankan channels
                        sri_lankan_channels = [
                            ch for ch in detailed_channels 
                            if ch['sri_lankan_score'] >= 1.0
                        ]
                        
                        # Categorize channels
                        for channel in sri_lankan_channels:
                            channel['category'] = self.categorize_channel_smart(channel)
                            channel['discovery_method'] = 'time_based_patterns'
                        
                        # Save incrementally
                        self.save_channels_incremental(sri_lankan_channels)
                    
                    # Check if target reached
                    if len(self.existing_channels) >= self.target_channels:
                        break
                    
                    # Phase 6: Popular and trending discovery
                    logger.info("Phase 6: Popular and trending discovery")
                    try:
                        # Get popular videos from Sri Lanka
                        popular_response = self.api_manager.make_request(
                            self.api_manager.service.videos().list,
                            part='snippet',
                            chart='mostPopular',
                            regionCode='LK',
                            maxResults=50
                        )
                        
                        self.stats['api_calls_made'] += 1
                        
                        popular_channel_ids = []
                        for item in popular_response.get('items', []):
                            channel_id = item['snippet']['channelId']
                            if channel_id not in self.existing_channels:
                                popular_channel_ids.append(channel_id)
                        
                        if popular_channel_ids:
                            # Get detailed information
                            detailed_channels = self._get_channel_details_batch(popular_channel_ids)
                            
                            # Filter for Sri Lankan channels
                            sri_lankan_channels = [
                                ch for ch in detailed_channels 
                                if ch['sri_lankan_score'] >= 1.0
                            ]
                            
                            # Categorize channels
                            for channel in sri_lankan_channels:
                                channel['category'] = self.categorize_channel_smart(channel)
                                channel['discovery_method'] = 'popular_videos'
                            
                            # Save incrementally
                            self.save_channels_incremental(sri_lankan_channels)
                    
                    except Exception as e:
                        logger.warning(f"Popular videos discovery failed: {e}")
                    
                    # Progress report
                    logger.info(f"Cycle complete. Discovered: {len(self.existing_channels)}/{self.target_channels}")
                    logger.info(f"API calls made: {self.stats['api_calls_made']}")
                    
                    # Check if we should continue or if quota is exhausted
                    if self.stats['quota_exhausted_count'] >= 3:
                        logger.warning("Multiple quota exhaustions detected. Stopping discovery.")
                        break
                
                except Exception as e:
                    if "All API keys exhausted" in str(e):
                        logger.warning("All API keys exhausted. Saving progress and stopping.")
                        self.stats['quota_exhausted_count'] += 1
                        break
                    else:
                        logger.error(f"Discovery phase error: {e}")
                        self.stats['errors_encountered'] += 1
                        # Continue to next cycle
                        continue
        
        except Exception as e:
            if "All API keys exhausted" in str(e):
                logger.info("All API keys exhausted. Discovery will resume when quotas reset.")
                self.stats['quota_exhausted_count'] += 1
            else:
                logger.error(f"Discovery error: {e}")
        
        # Final statistics
        self.stats['session_end'] = datetime.now().isoformat()
        self.stats['channels_discovered'] = len(self.existing_channels)
        self.stats['success_rate'] = (
            self.stats['discovered_this_session'] / max(self.stats['api_calls_made'], 1)
        ) * 100
        
        logger.info("Discovery session completed!")
        logger.info(f"Final statistics: {self.stats}")
        
        return self.stats

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Unlimited Sri Lankan YouTube Channel Discovery")
    parser.add_argument('--target', type=int, default=10000, help='Target number of channels to discover')
    parser.add_argument('--output-dir', help='Output directory for discovered channels')
    parser.add_argument('--resume', action='store_true', help='Resume from previous session')
    parser.add_argument('--expand-only', action='store_true', help='Only expand keywords, do not discover')
    
    args = parser.parse_args()
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize discovery system
        discovery = UnlimitedChannelDiscovery(
            output_dir=args.output_dir,
            target_channels=args.target
        )
        
        if args.expand_only:
            logger.info("Expanding keywords only...")
            expanded_keywords = discovery.keyword_engine.expand_keywords_comprehensive()
            print(f"Expanded to {len(expanded_keywords)} keywords")
            print("Keywords saved to database for future use")
            return
        
        # Run unlimited discovery
        stats = discovery.run_unlimited_discovery()
        
        print(f"\n=== Discovery Session Complete ===")
        print(f"Channels at start: {stats['channels_at_start']}")
        print(f"Channels discovered this session: {stats['discovered_this_session']}")
        print(f"Total channels now: {stats['channels_discovered']}")
        print(f"Target: {stats['target_channels']}")
        print(f"Progress: {(stats['channels_discovered']/stats['target_channels']*100):.1f}%")
        print(f"API calls made: {stats['api_calls_made']}")
        print(f"Success rate: {stats['success_rate']:.2f}%")
        print(f"Keywords processed: {stats['keywords_processed']}")
        
        if stats['channels_discovered'] >= stats['target_channels']:
            print("🎉 TARGET REACHED! Discovery complete!")
        elif stats['quota_exhausted_count'] > 0:
            print("⏳ Quota exhausted. Run again when quotas reset (1:30 PM Sri Lanka time)")
        else:
            print("✅ Session completed successfully. Run again to continue discovery.")
        
    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
