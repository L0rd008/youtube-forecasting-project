"""
Enhanced Sri Lankan YouTube Channel Discovery Script
Discovers unlimited Sri Lankan YouTube channels using multiple strategies and API key rotation
Compatible with the existing YouTube forecasting project system
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
from collections import defaultdict

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Required packages not installed: {e}")
    print("Install with: pip install google-api-python-client python-dotenv")
    exit(1)

# Import project modules
from config import (
    DATA_RAW_PATH,
    SRI_LANKAN_CHANNELS,
    CHANNEL_CATEGORIES,
    VIDEO_CATEGORIES,
    validate_api_key,
    YOUTUBE_API_KEY
)

from utils import (
    YouTubeAPIClient,
    save_to_csv,
    load_from_csv,
    setup_logging
)

# Setup logging using project's logging system
logger = setup_logging()

# Additional imports for keyword expansion
try:
    import requests
    from pytrends.request import TrendReq
except ImportError:
    logger.warning("Optional packages not installed. Install with: pip install requests pytrends")
    requests = None
    TrendReq = None

class KeywordExpansionEngine:
    """Intelligent keyword expansion system for astronomical scaling"""
    
    def __init__(self):
        self.base_keywords = [
            "sri lanka", "srilanka", "sinhala", "tamil", "ceylon", "lanka",
            "colombo", "kandy", "galle", "jaffna", "ape amma", "lankan",
            "sri lankan news", "sinhala songs", "tamil songs", "lankan food",
            "sri lanka travel", "colombo vlog", "sinhala comedy", "lankan cricket"
        ]
        
        self.expanded_keywords = set(self.base_keywords)
        self.validated_keywords = set()
        
        # Geographic expansion database
        self.sri_lankan_locations = [
            # Major cities
            'colombo', 'kandy', 'galle', 'jaffna', 'trincomalee', 'anuradhapura',
            'polonnaruwa', 'kurunegala', 'ratnapura', 'badulla', 'matara',
            'negombo', 'batticaloa', 'puttalam', 'kalutara', 'gampaha',
            
            # Districts and provinces
            'western province', 'central province', 'southern province',
            'northern province', 'eastern province', 'north western province',
            'north central province', 'uva province', 'sabaragamuwa province',
            
            # Popular areas and landmarks
            'mount lavinia', 'bentota', 'hikkaduwa', 'mirissa', 'unawatuna',
            'sigiriya', 'dambulla', 'ella', 'nuwara eliya', 'adams peak',
            'temple of tooth', 'lotus tower', 'independence square'
        ]
        
        # Cultural and linguistic terms
        self.cultural_terms = [
            # Sinhala terms
            'machang', 'aiya', 'nangi', 'patta', 'ado', 'malli', 'akka',
            'amma', 'thatha', 'seeya', 'achchi', 'putha', 'duwa',
            
            # Cultural events and festivals
            'avurudu', 'vesak', 'poson', 'esala perahera', 'kataragama',
            'adam\'s peak', 'poya day', 'sinhala new year',
            
            # Popular phrases
            'mage yalu', 'lankawe', 'api lankawa', 'mother lanka',
            'pearl of indian ocean', 'teardrop of india',
            
            # Food and cuisine
            'rice and curry', 'kottu', 'hoppers', 'string hoppers',
            'pol sambol', 'parippu', 'dhal curry', 'fish curry'
        ]
        
        # Trending search terms template
        self.trending_templates = [
            "{location} vlog", "{location} travel", "{location} food",
            "sinhala {topic}", "tamil {topic}", "lankan {topic}",
            "sri lanka {topic}", "{topic} lanka", "{topic} colombo"
        ]
    
    def get_youtube_suggestions(self, query: str) -> List[str]:
        """Get YouTube autocomplete suggestions"""
        if not requests:
            logger.warning("requests package not available for autocomplete")
            return []
        
        try:
            url = "https://suggestqueries.google.com/complete/search"
            params = {
                'client': 'firefox',
                'ds': 'yt',
                'q': query
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                suggestions = response.json()[1]
                return [s for s in suggestions if s.lower() != query.lower()]
            
        except Exception as e:
            logger.debug(f"Error getting suggestions for '{query}': {e}")
        
        return []
    
    def get_trending_terms(self) -> List[str]:
        """Get trending terms from Google Trends for Sri Lanka"""
        if not TrendReq:
            logger.warning("pytrends package not available for trending terms")
            return []
        
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            
            # Get trending searches for Sri Lanka
            trending_searches = pytrends.trending_searches(pn='sri_lanka')
            if not trending_searches.empty:
                return trending_searches['query'].head(20).tolist()
            
        except Exception as e:
            logger.debug(f"Error getting trending terms: {e}")
        
        return []
    
    def expand_via_autocomplete(self, max_suggestions: int = 5) -> Set[str]:
        """Expand keywords using YouTube autocomplete"""
        logger.info("Expanding keywords via YouTube autocomplete...")
        
        new_keywords = set()
        
        for keyword in list(self.expanded_keywords)[:50]:  # Limit to prevent excessive requests
            suggestions = self.get_youtube_suggestions(keyword)
            
            for suggestion in suggestions[:max_suggestions]:
                # Filter for Sri Lankan relevance
                suggestion_lower = suggestion.lower()
                if any(indicator in suggestion_lower for indicator in 
                      ['sri lanka', 'srilanka', 'lanka', 'sinhala', 'tamil', 'colombo', 'kandy']):
                    new_keywords.add(suggestion)
            
            time.sleep(0.1)  # Rate limiting
        
        logger.info(f"Autocomplete expansion found {len(new_keywords)} new keywords")
        return new_keywords
    
    def expand_via_geography(self) -> Set[str]:
        """Expand keywords using geographic terms"""
        logger.info("Expanding keywords via geographic terms...")
        
        new_keywords = set()
        
        # Add location-based combinations
        for location in self.sri_lankan_locations:
            new_keywords.update([
                f"{location} vlog",
                f"{location} travel",
                f"{location} food",
                f"{location} news",
                f"{location} music",
                f"visit {location}",
                f"{location} sri lanka"
            ])
        
        # Add cultural term combinations
        for term in self.cultural_terms:
            new_keywords.update([
                f"{term} sri lanka",
                f"sinhala {term}",
                f"lankan {term}"
            ])
        
        logger.info(f"Geographic expansion generated {len(new_keywords)} new keywords")
        return new_keywords
    
    def expand_via_trends(self) -> Set[str]:
        """Expand keywords using trending terms"""
        logger.info("Expanding keywords via trending terms...")
        
        new_keywords = set()
        trending_terms = self.get_trending_terms()
        
        for term in trending_terms:
            # Create Sri Lankan variations
            new_keywords.update([
                f"{term} sri lanka",
                f"{term} sinhala",
                f"{term} lankan",
                f"sri lanka {term}"
            ])
        
        logger.info(f"Trending expansion generated {len(new_keywords)} new keywords")
        return new_keywords
    
    def expand_via_templates(self) -> Set[str]:
        """Expand keywords using template patterns"""
        logger.info("Expanding keywords via template patterns...")
        
        new_keywords = set()
        
        # Popular topics for template expansion
        topics = [
            'news', 'music', 'comedy', 'food', 'travel', 'vlog', 'review',
            'tutorial', 'dance', 'song', 'movie', 'drama', 'cricket',
            'election', 'festival', 'wedding', 'cooking', 'fashion'
        ]
        
        for template in self.trending_templates:
            for location in self.sri_lankan_locations[:20]:  # Top 20 locations
                for topic in topics:
                    try:
                        keyword = template.format(location=location, topic=topic)
                        new_keywords.add(keyword)
                    except KeyError:
                        continue
        
        logger.info(f"Template expansion generated {len(new_keywords)} new keywords")
        return new_keywords
    
    def validate_keywords(self, keywords: Set[str], api_manager) -> Set[str]:
        """Validate keywords by testing them against YouTube search"""
        logger.info(f"Validating {len(keywords)} keywords...")
        
        validated = set()
        
        for keyword in list(keywords)[:100]:  # Limit validation to prevent quota exhaustion
            try:
                # Test keyword with minimal search
                response = api_manager.make_request(
                    api_manager.service.search().list,
                    part='snippet',
                    q=keyword,
                    type='channel',
                    regionCode='LK',
                    maxResults=1
                )
                
                # If we get results, keyword is valid
                if response.get('items'):
                    validated.add(keyword)
                
                time.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Error validating keyword '{keyword}': {e}")
                continue
        
        logger.info(f"Validated {len(validated)} keywords")
        return validated
    
    def run_comprehensive_expansion(self, api_manager=None) -> List[str]:
        """Run comprehensive keyword expansion using all methods"""
        logger.info("Starting comprehensive keyword expansion...")
        
        # Phase 1: Autocomplete expansion
        autocomplete_keywords = self.expand_via_autocomplete()
        self.expanded_keywords.update(autocomplete_keywords)
        
        # Phase 2: Geographic expansion
        geographic_keywords = self.expand_via_geography()
        self.expanded_keywords.update(geographic_keywords)
        
        # Phase 3: Trending expansion
        trending_keywords = self.expand_via_trends()
        self.expanded_keywords.update(trending_keywords)
        
        # Phase 4: Template expansion
        template_keywords = self.expand_via_templates()
        self.expanded_keywords.update(template_keywords)
        
        # Phase 5: Validation (if API manager provided)
        if api_manager:
            new_keywords = self.expanded_keywords - set(self.base_keywords)
            validated = self.validate_keywords(new_keywords, api_manager)
            self.validated_keywords.update(validated)
            final_keywords = list(set(self.base_keywords) | validated)
        else:
            final_keywords = list(self.expanded_keywords)
        
        logger.info(f"Keyword expansion complete: {len(self.base_keywords)} → {len(final_keywords)} keywords")
        
        return final_keywords
    
    def save_expanded_keywords(self, output_path: str):
        """Save expanded keywords to file"""
        keywords_data = {
            'base_keywords': self.base_keywords,
            'expanded_keywords': list(self.expanded_keywords),
            'validated_keywords': list(self.validated_keywords),
            'expansion_date': datetime.now().isoformat(),
            'total_count': len(self.expanded_keywords)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(keywords_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved expanded keywords to {output_path}")

@dataclass
class ChannelInfo:
    """Data class for channel information"""
    channel_id: str
    title: str
    description: str
    subscriber_count: int
    video_count: int
    view_count: int
    published_at: str
    country: str
    custom_url: str
    category_id: str
    default_language: str
    keywords: List[str]
    thumbnail_url: str
    discovery_method: str
    discovery_keyword: str
    sri_lankan_score: float
    discovered_at: str

class YouTubeAPIManager:
    """Manages multiple YouTube API keys with automatic rotation"""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        self.quota_usage = {}
        self.rate_limited_keys = set()
        self.service = None
        self._initialize_service()
        
        if not self.api_keys:
            raise ValueError("No YouTube API keys found in .env file")
    
    def _load_api_keys(self) -> List[str]:
        """Load all available API keys from environment"""
        keys = []
        
        # Check for primary key
        primary_key = os.getenv('YOUTUBE_API_KEY')
        if primary_key:
            keys.append(primary_key)
        
        # Check for numbered keys
        i = 1
        while True:
            key = os.getenv(f'YOUTUBE_API_KEY_{i}')
            if key:
                keys.append(key)
                i += 1
            else:
                break
        
        logger.info(f"Loaded {len(keys)} API keys")
        return keys
    
    def _initialize_service(self):
        """Initialize YouTube API service with current key"""
        if self.current_key_index < len(self.api_keys):
            current_key = self.api_keys[self.current_key_index]
            if current_key not in self.rate_limited_keys:
                try:
                    self.service = build('youtube', 'v3', developerKey=current_key)
                    logger.info(f"Initialized API service with key {self.current_key_index + 1}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to initialize service with key {self.current_key_index + 1}: {e}")
        return False
    
    def _rotate_key(self) -> bool:
        """Rotate to next available API key"""
        self.current_key_index += 1
        if self.current_key_index >= len(self.api_keys):
            self.current_key_index = 0
        
        # Check if we've tried all keys
        if len(self.rate_limited_keys) >= len(self.api_keys):
            logger.error("All API keys are rate limited")
            return False
        
        return self._initialize_service()
    
    def make_request(self, request_func, **kwargs):
        """Make API request with automatic key rotation on rate limit"""
        max_retries = len(self.api_keys) * 2
        
        for attempt in range(max_retries):
            if not self.service:
                if not self._rotate_key():
                    raise Exception("No available API keys")
            
            try:
                current_key = self.api_keys[self.current_key_index]
                
                # Track quota usage
                if current_key not in self.quota_usage:
                    self.quota_usage[current_key] = 0
                self.quota_usage[current_key] += 1
                
                result = request_func(**kwargs).execute()
                return result
                
            except HttpError as e:
                if e.resp.status == 403 and 'quotaExceeded' in str(e):
                    logger.warning(f"API key {self.current_key_index + 1} quota exceeded")
                    self.rate_limited_keys.add(self.api_keys[self.current_key_index])
                    self.service = None
                    
                    if not self._rotate_key():
                        raise Exception("All API keys exhausted")
                    continue
                else:
                    raise e
            except Exception as e:
                logger.error(f"API request failed: {e}")
                time.sleep(random.uniform(1, 3))
                continue
        
        raise Exception("Max retries exceeded")

class SriLankanChannelDiscovery:
    """Main class for discovering Sri Lankan YouTube channels"""
    
    # Official YouTube category mapping (only specified categories)
    YOUTUBE_CATEGORIES = {
        1: "Film & Animation",
        2: "Autos & Vehicles", 
        10: "Music",
        15: "Pets & Animals",
        17: "Sports",
        19: "Travel & Events",
        20: "Gaming",
        22: "People & Blogs",
        23: "Comedy",
        24: "Entertainment",
        25: "News & Politics",
        26: "Howto & Style",
        27: "Education",
        28: "Science & Technology"
    }
    
    # Sri Lankan indicators for channel detection
    SRI_LANKAN_INDICATORS = {
        'high_value': ['sri lanka', 'srilanka', 'ceylon', 'lanka'],
        'medium_value': ['colombo', 'kandy', 'galle', 'jaffna', 'anuradhapura', 'polonnaruwa'],
        'language': ['sinhala', 'sinhalese', 'tamil', 'sinhalen'],
        'cultural': ['lk', 'ape', 'mage', 'lankan', 'islanders'],
        'cities': ['negombo', 'matara', 'badulla', 'ratnapura', 'kurunegala', 'batticaloa']
    }
    
    def __init__(self, output_dir: str = None):
        # Validate API key using project's validation
        if not validate_api_key():
            raise ValueError("Invalid or missing YouTube API key. Please check your .env file.")
        
        self.api_manager = YouTubeAPIManager()
        
        # Use project's data path structure
        if output_dir is None:
            output_dir = DATA_RAW_PATH
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save discovered channels in project format
        self.channels_file = self.output_dir / "discovered_channels.json"
        self.existing_channels = self._load_existing_channels()
        
        # Discovery statistics
        self.stats = {
            'discovered': 0,
            'validated': 0,
            'filtered': 0,
            'api_calls': 0,
            'errors': 0
        }
    
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
    
    def _calculate_sri_lankan_score(self, channel_data: Dict) -> float:
        """Calculate how likely a channel is Sri Lankan based on various indicators"""
        score = 0.0
        
        # Combine text fields for analysis
        text_fields = [
            channel_data.get('title', '').lower(),
            channel_data.get('description', '').lower(),
            ' '.join(channel_data.get('keywords', [])).lower(),
            channel_data.get('country', '').lower()
        ]
        
        combined_text = ' '.join(text_fields)
        
        # Score based on indicators
        for indicator in self.SRI_LANKAN_INDICATORS['high_value']:
            if indicator in combined_text:
                score += 3.0
        
        for indicator in self.SRI_LANKAN_INDICATORS['medium_value']:
            if indicator in combined_text:
                score += 2.0
        
        for indicator in self.SRI_LANKAN_INDICATORS['language']:
            if indicator in combined_text:
                score += 2.5
        
        for indicator in self.SRI_LANKAN_INDICATORS['cultural']:
            if indicator in combined_text:
                score += 1.5
        
        for indicator in self.SRI_LANKAN_INDICATORS['cities']:
            if indicator in combined_text:
                score += 1.0
        
        # Country code bonus
        if channel_data.get('country', '').upper() == 'LK':
            score += 5.0
        
        # Language bonus
        if channel_data.get('defaultLanguage', '').lower() in ['si', 'ta', 'en']:
            score += 1.0
        
        return score
    
    def _get_channel_details(self, channel_ids: List[str]) -> List[Dict]:
        """Get detailed information for a list of channel IDs"""
        if not channel_ids:
            return []
        
        channels = []
        batch_size = 50
        
        for i in range(0, len(channel_ids), batch_size):
            batch_ids = channel_ids[i:i + batch_size]
            
            try:
                response = self.api_manager.make_request(
                    self.api_manager.service.channels().list,
                    part='snippet,statistics,brandingSettings,topicDetails',
                    id=','.join(batch_ids),
                    maxResults=50
                )
                
                self.stats['api_calls'] += 1
                
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
                        'discovered_at': datetime.now().isoformat()
                    }
                    
                    # Calculate Sri Lankan relevance score
                    channel_data['sri_lankan_score'] = self._calculate_sri_lankan_score(channel_data)
                    
                    channels.append(channel_data)
                
                # Rate limiting protection
                time.sleep(random.uniform(0.1, 0.5))
                
            except Exception as e:
                logger.error(f"Error getting channel details for batch: {e}")
                self.stats['errors'] += 1
                time.sleep(random.uniform(1, 3))
        
        return channels
    
    def search_by_keywords(self, keywords: List[str], max_per_keyword: int = 50) -> List[str]:
        """Search for channels using keywords"""
        logger.info(f"Searching by keywords: {keywords}")
        
        channel_ids = set()
        
        # Check if API service is available
        if not self.api_manager.service:
            logger.error("No API service available - all API keys may be exhausted")
            return list(channel_ids)
        
        for keyword in keywords:
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
                
                self.stats['api_calls'] += 1
                
                for item in response.get('items', []):
                    if item['id']['kind'] == 'youtube#channel':
                        channel_ids.add(item['id']['channelId'])
                
                logger.debug(f"Found {len(response.get('items', []))} channels for '{keyword}'")
                time.sleep(random.uniform(0.5, 1.0))
                
            except Exception as e:
                logger.error(f"Error searching for keyword '{keyword}': {e}")
                self.stats['errors'] += 1
                
                # If all API keys are exhausted, stop trying
                if "All API keys exhausted" in str(e):
                    logger.warning("All API keys exhausted, stopping keyword search")
                    break
        
        logger.info(f"Found {len(channel_ids)} unique channels from keyword search")
        return list(channel_ids)
    
    def discover_from_popular_videos(self, max_videos: int = 100) -> List[str]:
        """Discover channels from popular videos in Sri Lanka"""
        logger.info("Discovering channels from popular videos")
        
        channel_ids = set()
        
        # Check if API service is available
        if not self.api_manager.service:
            logger.error("No API service available - all API keys may be exhausted")
            return list(channel_ids)
        
        try:
            # Get popular videos from Sri Lanka
            response = self.api_manager.make_request(
                self.api_manager.service.videos().list,
                part='snippet',
                chart='mostPopular',
                regionCode='LK',
                maxResults=min(max_videos, 50)
            )
            
            self.stats['api_calls'] += 1
            
            for item in response.get('items', []):
                channel_id = item['snippet']['channelId']
                channel_ids.add(channel_id)
            
            logger.info(f"Found {len(channel_ids)} channels from popular videos")
            
        except Exception as e:
            logger.error(f"Error getting popular videos: {e}")
            self.stats['errors'] += 1
        
        return list(channel_ids)
    
    def discover_related_channels(self, seed_channel_ids: List[str]) -> List[str]:
        """Discover related channels by analyzing their video comments and subscriptions"""
        logger.info(f"Discovering related channels from {len(seed_channel_ids)} seed channels")
        
        related_channel_ids = set()
        
        for seed_id in seed_channel_ids[:10]:  # Limit to prevent excessive API usage
            try:
                # Get recent videos from seed channel
                videos_response = self.api_manager.make_request(
                    self.api_manager.service.search().list,
                    part='snippet',
                    channelId=seed_id,
                    type='video',
                    order='date',
                    maxResults=5
                )
                
                self.stats['api_calls'] += 1
                
                for video in videos_response.get('items', []):
                    video_id = video['id']['videoId']
                    
                    try:
                        # Get comments to find other channels
                        comments_response = self.api_manager.make_request(
                            self.api_manager.service.commentThreads().list,
                            part='snippet',
                            videoId=video_id,
                            maxResults=20,
                            order='relevance'
                        )
                        
                        self.stats['api_calls'] += 1
                        
                        for comment in comments_response.get('items', []):
                            author_channel_id = comment['snippet']['topLevelComment']['snippet'].get('authorChannelId', {}).get('value')
                            if author_channel_id and author_channel_id not in self.existing_channels:
                                related_channel_ids.add(author_channel_id)
                        
                        time.sleep(random.uniform(0.5, 1.0))
                        
                    except Exception as e:
                        logger.debug(f"Could not get comments for video {video_id}: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error processing seed channel {seed_id}: {e}")
                self.stats['errors'] += 1
        
        logger.info(f"Found {len(related_channel_ids)} related channels")
        return list(related_channel_ids)
    
    def discover_trending_channels(self) -> List[str]:
        """Discover channels from trending content"""
        logger.info("Discovering trending channels")
        
        channel_ids = set()
        
        # Check if API service is available
        if not self.api_manager.service:
            logger.error("No API service available - all API keys may be exhausted")
            return list(channel_ids)
        
        search_terms = [
            "sri lanka trending",
            "sinhala viral",
            "tamil trending",
            "lanka latest",
            "colombo today"
        ]
        
        for term in search_terms:
            try:
                response = self.api_manager.make_request(
                    self.api_manager.service.search().list,
                    part='snippet',
                    q=term,
                    type='video',
                    regionCode='LK',
                    order='viewCount',
                    publishedAfter=(datetime.now() - timedelta(days=30)).isoformat() + 'Z',
                    maxResults=20
                )
                
                self.stats['api_calls'] += 1
                
                for item in response.get('items', []):
                    channel_id = item['snippet']['channelId']
                    channel_ids.add(channel_id)
                
                time.sleep(random.uniform(0.3, 0.7))
                
            except Exception as e:
                logger.error(f"Error searching for trending term '{term}': {e}")
                self.stats['errors'] += 1
                
                # If all API keys are exhausted, stop trying
                if "All API keys exhausted" in str(e):
                    logger.warning("All API keys exhausted, stopping trending search")
                    break
        
        logger.info(f"Found {len(channel_ids)} channels from trending search")
        return list(channel_ids)
    
    def categorize_channel(self, channel_data: Dict) -> str:
        """Determine the best category for a channel based on content analysis"""
        
        # First try to get category from video analysis
        try:
            # Get recent videos to analyze category
            videos_response = self.api_manager.make_request(
                self.api_manager.service.search().list,
                part='snippet',
                channelId=channel_data['channel_id'],
                type='video',
                order='date',
                maxResults=5
            )
            
            self.stats['api_calls'] += 1
            
            video_ids = [item['id']['videoId'] for item in videos_response.get('items', [])]
            
            if video_ids:
                videos_details = self.api_manager.make_request(
                    self.api_manager.service.videos().list,
                    part='snippet',
                    id=','.join(video_ids)
                )
                
                self.stats['api_calls'] += 1
                
                # Get most common category from videos
                category_counts = defaultdict(int)
                for video in videos_details.get('items', []):
                    category_id = int(video['snippet'].get('categoryId', 22))
                    category_counts[category_id] += 1
                
                if category_counts:
                    most_common_category = max(category_counts, key=category_counts.get)
                    return self.YOUTUBE_CATEGORIES.get(most_common_category, "People & Blogs")
        
        except Exception as e:
            logger.debug(f"Could not analyze videos for categorization: {e}")
        
        # Fallback to content-based categorization
        text_content = ' '.join([
            channel_data.get('title', '').lower(),
            channel_data.get('description', '').lower(),
            ' '.join(channel_data.get('keywords', [])).lower()
        ])
        
        # Category keyword mapping
        category_keywords = {
            "News & Politics": ['news', 'politics', 'current', 'breaking', 'report', 'media'],
            "Music": ['music', 'song', 'singer', 'band', 'album', 'musical'],
            "Entertainment": ['entertainment', 'comedy', 'drama', 'show', 'movie', 'film'],
            "Education": ['education', 'learn', 'tutorial', 'teach', 'lesson', 'study'],
            "Sports": ['sports', 'cricket', 'football', 'game', 'match', 'player'],
            "Gaming": ['gaming', 'game', 'play', 'gamer', 'gameplay'],
            "Travel & Events": ['travel', 'trip', 'tour', 'visit', 'journey', 'event'],
            "Howto & Style": ['howto', 'how to', 'style', 'fashion', 'beauty', 'makeup'],
            "Science & Technology": ['tech', 'technology', 'science', 'computer', 'software'],
            "Autos & Vehicles": ['car', 'auto', 'vehicle', 'bike', 'motorcycle', 'driving']
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
    
    def run_comprehensive_discovery(self, max_channels: int = 1000) -> Dict:
        """Run comprehensive channel discovery using multiple methods"""
        logger.info(f"Starting comprehensive discovery (target: {max_channels} channels)")
        
        all_channel_ids = set()
        
        # Method 1: Keyword-based search
        sri_lankan_keywords = [
            "sri lanka", "srilanka", "sinhala", "tamil", "ceylon", "lanka",
            "colombo", "kandy", "galle", "jaffna", "ape amma", "lankan",
            "sri lankan news", "sinhala songs", "tamil songs", "lankan food",
            "sri lanka travel", "colombo vlog", "sinhala comedy", "lankan cricket"
        ]
        
        keyword_channels = self.search_by_keywords(sri_lankan_keywords, max_per_keyword=30)
        all_channel_ids.update(keyword_channels)
        logger.info(f"Keyword search found {len(keyword_channels)} channels")
        
        # Method 2: Popular videos discovery
        if len(all_channel_ids) < max_channels:
            popular_channels = self.discover_from_popular_videos(100)
            all_channel_ids.update(popular_channels)
            logger.info(f"Popular videos found {len(popular_channels)} additional channels")
        
        # Method 3: Trending discovery
        if len(all_channel_ids) < max_channels:
            trending_channels = self.discover_trending_channels()
            all_channel_ids.update(trending_channels)
            logger.info(f"Trending search found {len(trending_channels)} additional channels")
        
        # Method 4: Related channels discovery
        if len(all_channel_ids) < max_channels:
            seed_channels = list(all_channel_ids)[:20]  # Use discovered channels as seeds
            related_channels = self.discover_related_channels(seed_channels)
            all_channel_ids.update(related_channels)
            logger.info(f"Related channels found {len(related_channels)} additional channels")
        
        # Remove already known channels
        new_channel_ids = [cid for cid in all_channel_ids if cid not in self.existing_channels]
        logger.info(f"Found {len(new_channel_ids)} new channels to process")
        
        if not new_channel_ids:
            logger.info("No new channels to process")
            return self.stats
        
        # Get detailed information for all new channels
        logger.info("Getting detailed channel information...")
        detailed_channels = self._get_channel_details(new_channel_ids)
        self.stats['discovered'] = len(detailed_channels)
        
        # Filter for Sri Lankan channels
        logger.info("Filtering for Sri Lankan channels...")
        sri_lankan_channels = [
            ch for ch in detailed_channels 
            if ch['sri_lankan_score'] >= 1.0  # Minimum threshold
        ]
        self.stats['filtered'] = len(sri_lankan_channels)
        
        logger.info(f"Filtered to {len(sri_lankan_channels)} Sri Lankan channels")
        
        # Categorize channels
        logger.info("Categorizing channels...")
        for channel in sri_lankan_channels:
            try:
                channel['category'] = self.categorize_channel(channel)
                self.stats['validated'] += 1
            except Exception as e:
                logger.error(f"Error categorizing channel {channel['channel_id']}: {e}")
                channel['category'] = "People & Blogs"  # fallback
        
        # Save results
        self._save_channels(sri_lankan_channels)
        
        logger.info("Discovery completed successfully!")
        logger.info(f"Statistics: {self.stats}")
        
        return self.stats
    
    def _save_channels(self, channels: List[Dict]):
        """Save discovered channels to JSON file"""
        if not channels:
            logger.warning("No channels to save")
            return
        
        # Load existing data or create new structure
        if self.channels_file.exists():
            with open(self.channels_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        # Group channels by category
        for channel in channels:
            category = channel['category']
            if category not in data:
                data[category] = {}
            
            data[category][channel['title']] = channel['channel_id']
        
        # Save updated data
        with open(self.channels_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(channels)} channels to {self.channels_file}")
        
        # Also save detailed data for analysis
        detailed_file = self.output_dir / f"detailed_channels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(channels, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved detailed data to {detailed_file}")

def main():
    """Main execution function with command-line interface"""
    parser = argparse.ArgumentParser(description="Discover and validate YouTube channels")
    parser.add_argument('--keywords', nargs='+', help='Keywords to search for channels')
    parser.add_argument('--validate-existing', action='store_true', help='Validate existing channels from config')
    parser.add_argument('--location-search', action='store_true', help='Search by location (Sri Lanka)')
    parser.add_argument('--expand-keywords', action='store_true', help='Use intelligent keyword expansion')
    parser.add_argument('--max-results', type=int, default=1000, help='Maximum results per search')
    parser.add_argument('--output-dir', help='Output directory for discovered channels')
    parser.add_argument('--api-key', help='YouTube API key (overrides .env)')
    
    args = parser.parse_args()
    
    try:
        # Override API key if provided
        if args.api_key:
            os.environ['YOUTUBE_API_KEY'] = args.api_key
        
        # Initialize discovery system
        discovery = SriLankanChannelDiscovery(output_dir=args.output_dir)
        
        if args.validate_existing:
            logger.info("Validating existing channels from config...")
            # Get all channel IDs from config
            all_config_channels = []
            for category, channels in SRI_LANKAN_CHANNELS.items():
                all_config_channels.extend(channels.values())
            
            logger.info(f"Validating {len(all_config_channels)} existing channels")
            
            # Get detailed information for validation
            detailed_channels = discovery._get_channel_details(all_config_channels)
            
            # Filter valid channels
            valid_channels = [ch for ch in detailed_channels if ch['subscriber_count'] > 0]
            
            if valid_channels:
                discovery._save_channels(valid_channels)
                logger.info(f"Successfully validated {len(valid_channels)} channels")
            else:
                logger.warning("No channels to save")
            
            print(f"\n=== Validation Summary ===")
            print(f"Channels validated: {len(valid_channels)}")
            print(f"API calls made: {discovery.stats['api_calls']}")
            print(f"Errors encountered: {discovery.stats['errors']}")
            
        elif args.keywords:
            logger.info(f"Searching for channels with keywords: {args.keywords}")
            
            # Search by provided keywords
            channel_ids = discovery.search_by_keywords(args.keywords, max_per_keyword=args.max_results//len(args.keywords))
            
            if channel_ids:
                # Get detailed information
                detailed_channels = discovery._get_channel_details(channel_ids)
                
                # Filter for Sri Lankan channels
                sri_lankan_channels = [
                    ch for ch in detailed_channels 
                    if ch['sri_lankan_score'] >= 1.0
                ]
                
                # Categorize channels
                for channel in sri_lankan_channels:
                    channel['category'] = discovery.categorize_channel(channel)
                
                # Save results
                discovery._save_channels(sri_lankan_channels)
                
                print(f"\n=== Keyword Search Summary ===")
                print(f"Channels found: {len(channel_ids)}")
                print(f"Sri Lankan channels: {len(sri_lankan_channels)}")
                print(f"API calls made: {discovery.stats['api_calls']}")
            else:
                print("No channels found for the provided keywords")
                
        elif args.expand_keywords:
            logger.info("Using intelligent keyword expansion for channel discovery")
            
            # Initialize keyword expansion engine
            keyword_engine = KeywordExpansionEngine()
            
            # Run comprehensive keyword expansion
            expanded_keywords = keyword_engine.run_comprehensive_expansion(discovery.api_manager)
            
            # Save expanded keywords for future reference
            keywords_file = discovery.output_dir / f"expanded_keywords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            keyword_engine.save_expanded_keywords(str(keywords_file))
            
            logger.info(f"Expanded from {len(keyword_engine.base_keywords)} to {len(expanded_keywords)} keywords")
            
            # Use expanded keywords for channel search
            channel_ids = discovery.search_by_keywords(expanded_keywords[:200], max_per_keyword=10)  # Limit to prevent quota exhaustion
            
            if channel_ids:
                # Get detailed information
                detailed_channels = discovery._get_channel_details(channel_ids)
                
                # Filter for Sri Lankan channels
                sri_lankan_channels = [
                    ch for ch in detailed_channels 
                    if ch['sri_lankan_score'] >= 1.0
                ]
                
                # Categorize channels
                for channel in sri_lankan_channels:
                    channel['category'] = discovery.categorize_channel(channel)
                
                # Save results
                discovery._save_channels(sri_lankan_channels)
                
                print(f"\n=== Keyword Expansion Summary ===")
                print(f"Base keywords: {len(keyword_engine.base_keywords)}")
                print(f"Expanded keywords: {len(expanded_keywords)}")
                print(f"Validated keywords: {len(keyword_engine.validated_keywords)}")
                print(f"Channels found: {len(channel_ids)}")
                print(f"Sri Lankan channels: {len(sri_lankan_channels)}")
                print(f"API calls made: {discovery.stats['api_calls']}")
            else:
                print("No channels found with expanded keywords")
                
        elif args.location_search:
            logger.info("Performing location-based search for Sri Lankan channels")
            
            # Use comprehensive discovery with location focus
            stats = discovery.run_comprehensive_discovery(max_channels=args.max_results)
            
            print(f"\n=== Location Search Summary ===")
            print(f"Channels discovered: {stats['discovered']}")
            print(f"Sri Lankan channels filtered: {stats['filtered']}")
            print(f"Channels categorized: {stats['validated']}")
            print(f"API calls made: {stats['api_calls']}")
            print(f"Errors encountered: {stats['errors']}")
            
        else:
            # Default: Run comprehensive discovery
            logger.info("Running comprehensive channel discovery")
            stats = discovery.run_comprehensive_discovery(max_channels=args.max_results)
            
            print(f"\n=== Discovery Summary ===")
            print(f"Channels discovered: {stats['discovered']}")
            print(f"Sri Lankan channels filtered: {stats['filtered']}")
            print(f"Channels categorized: {stats['validated']}")
            print(f"API calls made: {stats['api_calls']}")
            print(f"Errors encountered: {stats['errors']}")
        
        print("Channel discovery completed successfully!")
        
    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
