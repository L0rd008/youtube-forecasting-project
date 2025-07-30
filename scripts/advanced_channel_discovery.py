"""
Advanced Sri Lankan YouTube Channel Discovery System
Focuses on finding NEW channels using advanced techniques when basic searches return mostly duplicates

ENHANCED FEATURES:
1. Long-tail keyword combinations with autocomplete expansion
2. Trending hashtag discovery
3. Comment thread mining
4. Playlist collaboration discovery
5. Geographic micro-targeting
6. Popular videos discovery
7. Smart channel categorization
8. Keyword performance tracking
9. Debug mode with detailed logging
10. Enhanced deduplication logic
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
from config import DATA_RAW_PATH, validate_api_key
from utils import setup_logging
from collect_channels import YouTubeAPIManager

# Setup logging
logger = setup_logging()

class AdvancedKeywordEngine:
    """Advanced keyword expansion system with performance tracking"""
    
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
            "milk rice", "kiribath", "kokis making", "aluwa sweet", "kavum oil cake",
            "athirasa", "aggala", "watalappan", "curd treacle", "pol roti",
            
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
            
            # Political figures
            "mahinda rajapaksa", "ranil wickremesinghe", "sajith premadasa", 
            "gotabaya rajapaksa", "sri lankan parliament", "sri lankan politics",
            "sri lankan election", "sri lankan government",
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
    
    def _is_sri_lankan_relevant(self, text: str) -> bool:
        """Check if text is relevant to Sri Lankan content"""
        text_lower = text.lower()
        sri_lankan_indicators = [
            'sri lanka', 'srilanka', 'lanka', 'sinhala', 'tamil', 'ceylon',
            'colombo', 'kandy', 'galle', 'jaffna', 'lankan'
        ]
        return any(indicator in text_lower for indicator in sri_lankan_indicators)
    
    def expand_keywords_comprehensive(self) -> List[str]:
        """Comprehensive keyword expansion using multiple methods"""
        logger.info("🔍 Starting comprehensive keyword expansion...")
        
        all_keywords = set(self.base_keywords)
        
        # Method 1: Autocomplete expansion
        logger.info("📝 Expanding via YouTube autocomplete...")
        for base_keyword in self.base_keywords[:20]:  # Limit to prevent rate limiting
            suggestions = self.get_youtube_autocomplete(base_keyword)
            for suggestion in suggestions:
                if self._is_sri_lankan_relevant(suggestion):
                    all_keywords.add(suggestion)
            time.sleep(0.1)  # Rate limiting
        
        # Method 2: Geographic combinations
        logger.info("🗺️ Generating geographic combinations...")
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
        logger.info("🎭 Generating cultural combinations...")
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
        
        # Update keywords database
        self._update_keywords_database(list(all_keywords))
        
        logger.info(f"✅ Keyword expansion complete: {len(self.base_keywords)} → {len(all_keywords)} keywords")
        return list(all_keywords)
    
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
        
        logger.info(f"📊 Updated keywords database with {len(keywords)} keywords")
    
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
                logger.info(f"⚠️ Deactivated low-performing keyword: {keyword}")

class AdvancedChannelDiscovery:
    """Enhanced discovery system for finding NEW Sri Lankan channels with advanced features"""
    
    def __init__(self, output_dir: str = None, target_new_channels: int = 100, debug_mode: bool = False):
        # Validate API key
        if not validate_api_key():
            raise ValueError("Invalid or missing YouTube API key. Please check your .env file.")
        
        self.api_manager = YouTubeAPIManager()
        self.target_new_channels = target_new_channels
        self.debug_mode = debug_mode
        
        # Setup directories
        if output_dir is None:
            output_dir = DATA_RAW_PATH
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Files
        self.channels_file = self.output_dir / "discovered_channels.json"
        self.new_channels_file = self.output_dir / "new_channels_found.json"
        self.detailed_channels_dir = self.output_dir / "detailed_channels"
        self.detailed_channels_dir.mkdir(exist_ok=True)
        
        # Load existing data with enhanced validation
        self.existing_channels = self._load_existing_channels_enhanced()
        
        # Initialize keyword engine
        self.keyword_engine = AdvancedKeywordEngine(self.output_dir)
        
        # Enhanced discovery statistics
        self.stats = {
            'session_start': datetime.now().isoformat(),
            'channels_at_start': len(self.existing_channels),
            'target_new_channels': target_new_channels,
            'new_channels_found': 0,
            'api_calls_made': 0,
            'techniques_used': [],
            'success_by_technique': {},
            'duplicate_rejections': 0,
            'new_channels_accepted': 0,
            'channels_found_but_rejected': 0,
            'quota_exhausted_count': 0,
            'keywords_processed': 0
        }
        
        logger.info(f"🚀 Enhanced Advanced Discovery initialized. Existing: {len(self.existing_channels)}, Target new: {target_new_channels}")
        if self.debug_mode:
            logger.info("🐛 DEBUG MODE ENABLED - Will show detailed deduplication info")
    
    def _load_existing_channels_enhanced(self) -> Set[str]:
        """Enhanced loading of existing channels with better validation and debugging"""
        if not self.channels_file.exists():
            logger.info("📁 No existing channels file found, starting fresh")
            return set()
        
        try:
            with open(self.channels_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            existing_ids = set()
            total_loaded = 0
            
            for category, channels in data.items():
                if not isinstance(channels, dict):
                    logger.warning(f"Invalid category structure for '{category}', skipping")
                    continue
                    
                for channel_name, channel_id in channels.items():
                    if not isinstance(channel_id, str) or not channel_id.startswith('UC'):
                        logger.warning(f"Invalid channel ID '{channel_id}' for '{channel_name}', skipping")
                        continue
                        
                    # Normalize channel ID (remove any whitespace, ensure proper format)
                    channel_id = channel_id.strip()
                    existing_ids.add(channel_id)
                    total_loaded += 1
            
            logger.info(f"✅ Successfully loaded {total_loaded} existing channels from {len(data)} categories")
            
            # Debug: Show sample of loaded channels
            if self.debug_mode and existing_ids:
                sample_channels = list(existing_ids)[:5]
                logger.info(f"🐛 Sample existing channel IDs: {sample_channels}")
            
            return existing_ids
            
        except Exception as e:
            logger.error(f"❌ Error loading existing channels: {e}")
            return set()
    
    def generate_long_tail_keywords(self) -> List[str]:
        """Generate long-tail keyword combinations that are less likely to have been searched"""
        logger.info("🔍 Generating long-tail keyword combinations...")
        
        # Base terms
        base_terms = ["sri lanka", "srilanka", "lanka", "lankan", "sinhala", "tamil", "ceylon"]
        
        # Specific niches and micro-topics
        niches = [
            # Specific locations (smaller towns/areas)
            "matale", "chilaw", "tangalle", "ella rock", "nuwara eliya tea", "sigiriya village",
            "dambulla cave", "polonnaruwa ancient", "anuradhapura sacred", "mihintale",
            
            # Specific cultural events
            "poya day", "full moon poya", "duruthu perahera", "navam perahera", "kite festival",
            "water cutting ceremony", "pirith chanting", "bana preaching", "dana ceremony",
            
            # Specific food items
            "milk rice", "kiribath", "kokis making", "aluwa sweet", "kavum oil cake",
            "athirasa", "aggala", "watalappan", "curd treacle", "pol roti",
            
            # Specific crafts/skills
            "batik making", "mask carving", "pottery wheel", "coconut husk", "coir rope",
            "brass work", "wood carving", "gem cutting", "tea plucking", "rubber tapping",
            
            # Specific animals/nature
            "elephant orphanage", "turtle hatchery", "leopard safari", "whale watching",
            "bird sanctuary", "butterfly garden", "spice garden", "botanical garden",
            
            # Specific festivals/seasons
            "avurudu games", "kite flying", "oil lamp lighting", "rangoli kolam",
            "vesak lantern", "poson dana", "esala perahera elephant", "kataragama festival",
            
            # Modern/contemporary
            "startup sri lanka", "tech meetup", "coding bootcamp", "digital nomad",
            "coworking space", "social media marketing", "e-commerce", "online business"
        ]
        
        # Time-based modifiers
        time_modifiers = [
            "2024", "2025", "latest", "new", "recent", "today", "this week", "this month",
            "trending", "viral", "popular", "best", "top", "amazing", "incredible"
        ]
        
        # Content type modifiers
        content_types = [
            "vlog", "tutorial", "guide", "tips", "tricks", "secrets", "hidden",
            "behind scenes", "documentary", "interview", "review", "reaction",
            "unboxing", "haul", "challenge", "experiment", "test", "comparison"
        ]
        
        long_tail_keywords = []
        
        # Generate combinations
        for base in base_terms[:3]:  # Limit base terms to prevent too many combinations
            for niche in niches:
                # Base + niche
                long_tail_keywords.append(f"{base} {niche}")
                long_tail_keywords.append(f"{niche} {base}")
                
                # Add time modifier
                for time_mod in time_modifiers[:5]:
                    long_tail_keywords.append(f"{time_mod} {base} {niche}")
                    long_tail_keywords.append(f"{base} {niche} {time_mod}")
                
                # Add content type
                for content_type in content_types[:5]:
                    long_tail_keywords.append(f"{base} {niche} {content_type}")
                    long_tail_keywords.append(f"{content_type} {base} {niche}")
        
        # Remove duplicates and shuffle
        long_tail_keywords = list(set(long_tail_keywords))
        random.shuffle(long_tail_keywords)
        
        logger.info(f"✅ Generated {len(long_tail_keywords)} long-tail keywords")
        return long_tail_keywords[:500]  # Limit to prevent excessive API usage
    
    def discover_from_trending_hashtags(self) -> List[str]:
        """Discover channels from currently trending Sri Lankan hashtags"""
        logger.info("📈 Discovering from trending hashtags...")
        
        # Current trending hashtags (would be updated regularly)
        trending_hashtags = [
            "#SriLanka2025", "#LankaVibes", "#SriLankanLife", "#VisitSriLanka2025",
            "#SinhalaNewYear2025", "#LankanFood", "#SriLankanWedding", "#LankanTradition",
            "#ColomboLife", "#KandyCity", "#GalleVibes", "#JaffnaLife", "#SriLankanArt",
            "#LankanMusic", "#SriLankanDance", "#LankanCulture", "#SriLankanNature",
            "#LankanBeaches", "#SriLankanTea", "#LankanSpices", "#SriLankanGems",
            "#LankanElephants", "#SriLankanCricket", "#LankanStartup", "#SriLankanTech"
        ]
        
        new_channel_ids = set()
        
        for hashtag in trending_hashtags:
            try:
                # Search for recent videos with this hashtag
                response = self.api_manager.make_request(
                    self.api_manager.service.search().list,
                    part='snippet',
                    q=hashtag,
                    type='video',
                    regionCode='LK',
                    publishedAfter=(datetime.now() - timedelta(days=30)).isoformat() + 'Z',
                    maxResults=20,
                    order='relevance'
                )
                
                self.stats['api_calls_made'] += 1
                
                for item in response.get('items', []):
                    channel_id = item['snippet']['channelId']
                    if channel_id not in self.existing_channels:
                        new_channel_ids.add(channel_id)
                
                time.sleep(random.uniform(0.3, 0.6))
                
            except Exception as e:
                logger.debug(f"Error searching hashtag {hashtag}: {e}")
                continue
        
        logger.info(f"📈 Found {len(new_channel_ids)} new channels from trending hashtags")
        return list(new_channel_ids)
    
    def discover_from_comment_threads(self, seed_channels: List[str], max_comments: int = 100) -> List[str]:
        """Mine comment threads for new channel discoveries"""
        logger.info(f"💬 Mining comment threads from {len(seed_channels)} seed channels...")
        
        new_channel_ids = set()
        
        for seed_channel in seed_channels[:10]:  # Limit seed channels
            try:
                # Get recent videos from seed channel
                videos_response = self.api_manager.make_request(
                    self.api_manager.service.search().list,
                    part='snippet',
                    channelId=seed_channel,
                    type='video',
                    order='date',
                    maxResults=5
                )
                
                self.stats['api_calls_made'] += 1
                
                for video in videos_response.get('items', []):
                    video_id = video['id']['videoId']
                    
                    try:
                        # Get comments from this video
                        comments_response = self.api_manager.make_request(
                            self.api_manager.service.commentThreads().list,
                            part='snippet',
                            videoId=video_id,
                            maxResults=20,
                            order='relevance'
                        )
                        
                        self.stats['api_calls_made'] += 1
                        
                        for comment in comments_response.get('items', []):
                            author_channel_id = comment['snippet']['topLevelComment']['snippet'].get('authorChannelId', {}).get('value')
                            if (author_channel_id and 
                                author_channel_id not in self.existing_channels and
                                author_channel_id != seed_channel):
                                new_channel_ids.add(author_channel_id)
                        
                        time.sleep(random.uniform(0.2, 0.4))
                        
                    except Exception as e:
                        logger.debug(f"Could not get comments for video {video_id}: {e}")
                        continue
                
            except Exception as e:
                logger.debug(f"Error processing seed channel {seed_channel}: {e}")
                continue
        
        logger.info(f"💬 Found {len(new_channel_ids)} new channels from comment mining")
        return list(new_channel_ids)
    
    def discover_from_playlists(self, seed_channels: List[str]) -> List[str]:
        """Discover channels from collaborative playlists"""
        logger.info(f"📋 Discovering from playlists of {len(seed_channels)} seed channels...")
        
        new_channel_ids = set()
        
        for seed_channel in seed_channels[:15]:  # Limit to prevent excessive API usage
            try:
                # Get playlists from seed channel
                playlists_response = self.api_manager.make_request(
                    self.api_manager.service.playlists().list,
                    part='snippet',
                    channelId=seed_channel,
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
                            maxResults=30
                        )
                        
                        self.stats['api_calls_made'] += 1
                        
                        for item in playlist_items_response.get('items', []):
                            channel_id = item['snippet'].get('videoOwnerChannelId')
                            if (channel_id and 
                                channel_id not in self.existing_channels and
                                channel_id != seed_channel):
                                new_channel_ids.add(channel_id)
                        
                        time.sleep(random.uniform(0.3, 0.6))
                        
                    except Exception as e:
                        logger.debug(f"Could not get playlist items for {playlist_id}: {e}")
                        continue
                
            except Exception as e:
                logger.debug(f"Error getting playlists for channel {seed_channel}: {e}")
                continue
        
        logger.info(f"📋 Found {len(new_channel_ids)} new channels from playlist discovery")
        return list(new_channel_ids)
    
    def discover_micro_geographic(self) -> List[str]:
        """Discover channels using very specific geographic terms"""
        logger.info("🗺️ Discovering channels using micro-geographic targeting...")
        
        # Very specific locations that might not have been searched before
        micro_locations = [
            # Specific neighborhoods/areas
            "pettah colombo", "fort colombo", "bambalapitiya", "wellawatte", "dehiwala",
            "mount lavinia beach", "negombo fish market", "hikkaduwa coral",
            "unawatuna beach", "mirissa whale", "tangalle bay", "arugam bay surf",
            
            # Specific temples/religious sites
            "gangaramaya temple", "kelaniya temple", "bellanwila temple", "sripada adam",
            "kataragama devalaya", "ruwanwelisaya", "jetavanaramaya", "abhayagiri",
            
            # Specific schools/universities
            "university colombo", "university peradeniya", "university moratuwa",
            "royal college", "st thomas college", "ladies college", "vishaka vidyalaya",
            
            # Specific markets/shopping areas
            "pettah market", "kandy market", "galle fort", "dutch hospital",
            "odel colombo", "majestic city", "liberty plaza", "crescat boulevard",
            
            # Specific natural locations
            "horton plains", "worlds end", "bakers falls", "ella gap", "little adams peak",
            "pidurangala rock", "dambulla cave temple", "minneriya national park"
        ]
        
        new_channel_ids = set()
        
        for location in micro_locations:
            try:
                # Search for channels mentioning this specific location
                response = self.api_manager.make_request(
                    self.api_manager.service.search().list,
                    part='snippet',
                    q=f'"{location}"',  # Use quotes for exact phrase matching
                    type='channel',
                    regionCode='LK',
                    maxResults=15,
                    order='relevance'
                )
                
                self.stats['api_calls_made'] += 1
                
                for item in response.get('items', []):
                    if item['id']['kind'] == 'youtube#channel':
                        channel_id = item['id']['channelId']
                        if channel_id not in self.existing_channels:
                            new_channel_ids.add(channel_id)
                
                time.sleep(random.uniform(0.4, 0.8))
                
            except Exception as e:
                logger.debug(f"Error searching micro-location '{location}': {e}")
                continue
        
        logger.info(f"🗺️ Found {len(new_channel_ids)} new channels from micro-geographic search")
        return list(new_channel_ids)
    
    def get_channel_details_batch(self, channel_ids: List[str]) -> List[Dict]:
        """Get detailed information for a batch of channel IDs"""
        if not channel_ids:
            return []
        
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
                        'sri_lankan_score': self._calculate_sri_lankan_score({
                            'title': snippet.get('title', ''),
                            'description': snippet.get('description', ''),
                            'country': snippet.get('country', ''),
                            'keywords': branding.get('keywords', '').split(',') if branding.get('keywords') else []
                        })
                    }
                    
                    channels.append(channel_data)
                
                time.sleep(random.uniform(0.1, 0.3))
                
            except Exception as e:
                logger.error(f"Error getting channel details for batch: {e}")
                continue
        
        return channels
    
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
        
        return score
    
    def save_new_channels(self, new_channels: List[Dict]):
        """Save newly discovered channels"""
        if not new_channels:
            return
        
        # Save to separate file for new discoveries
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_discovery_file = self.output_dir / f"new_discovery_{timestamp}.json"
        
        with open(new_discovery_file, 'w', encoding='utf-8') as f:
            json.dump(new_channels, f, indent=2, ensure_ascii=False)
        
        # Also append to main file
        if self.channels_file.exists():
            with open(self.channels_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        # Add new channels by category
        for channel in new_channels:
            category = self._categorize_channel(channel)
            if category not in data:
                data[category] = {}
            
            data[category][channel['title']] = channel['channel_id']
        
        # Save updated data
        with open(self.channels_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.stats['new_channels_found'] += len(new_channels)
        logger.info(f"💾 Saved {len(new_channels)} new channels")
    
    def _categorize_channel_smart(self, channel_data: Dict) -> str:
        """Smart channel categorization using content analysis"""
        
        # YouTube category mapping
        YOUTUBE_CATEGORIES = {
            1: "Film & Animation", 2: "Autos & Vehicles", 10: "Music",
            15: "Pets & Animals", 17: "Sports", 19: "Travel & Events",
            20: "Gaming", 22: "People & Blogs", 23: "Comedy",
            24: "Entertainment", 25: "News & Politics", 26: "Howto & Style",
            27: "Education", 28: "Science & Technology"
        }
        
        # Try to get category from recent videos (if quota allows)
        try:
            videos_response = self.api_manager.make_request(
                self.api_manager.service.search().list,
                part='snippet',
                channelId=channel_data['channel_id'],
                type='video',
                order='date',
                maxResults=3  # Reduced to save quota
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
        
        # Fallback to enhanced text-based categorization
        return self._categorize_channel_fallback(channel_data)
    
    def _categorize_channel_fallback(self, channel_data: Dict) -> str:
        """Enhanced fallback categorization using keywords"""
        text_content = ' '.join([
            channel_data.get('title', '').lower(),
            channel_data.get('description', '').lower(),
            ' '.join(channel_data.get('keywords', [])).lower()
        ])
        
        # Enhanced category keyword mapping
        category_keywords = {
            "News & Politics": ['news', 'politics', 'current', 'breaking', 'report', 'media', 'election', 'government'],
            "Music": ['music', 'song', 'singer', 'band', 'album', 'musical', 'concert', 'audio', 'sound'],
            "Entertainment": ['entertainment', 'comedy', 'drama', 'show', 'movie', 'film', 'teledrama', 'funny'],
            "Education": ['education', 'learn', 'tutorial', 'teach', 'lesson', 'study', 'school', 'university'],
            "Sports": ['sports', 'cricket', 'football', 'game', 'match', 'player', 'team', 'tournament'],
            "Gaming": ['gaming', 'game', 'play', 'gamer', 'gameplay', 'esports', 'stream'],
            "Travel & Events": ['travel', 'trip', 'tour', 'visit', 'journey', 'event', 'festival', 'vacation'],
            "Howto & Style": ['howto', 'how to', 'style', 'fashion', 'beauty', 'makeup', 'cooking', 'recipe'],
            "Science & Technology": ['tech', 'technology', 'science', 'computer', 'software', 'ai', 'digital'],
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
    
    def _categorize_channel(self, channel_data: Dict) -> str:
        """Main categorization method - uses smart categorization if quota allows"""
        try:
            return self._categorize_channel_smart(channel_data)
        except Exception as e:
            logger.debug(f"Smart categorization failed, using fallback: {e}")
            return self._categorize_channel_fallback(channel_data)
    
    def discover_from_popular_videos(self) -> List[str]:
        """Discover channels from YouTube's mostPopular chart for Sri Lanka"""
        logger.info("🔥 Discovering channels from popular videos...")
        
        new_channel_ids = set()
        
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
            
            for item in popular_response.get('items', []):
                channel_id = item['snippet']['channelId']
                if channel_id not in self.existing_channels:
                    new_channel_ids.add(channel_id)
            
            logger.info(f"🔥 Found {len(new_channel_ids)} new channels from popular videos")
            
        except Exception as e:
            logger.warning(f"Popular videos discovery failed: {e}")
        
        return list(new_channel_ids)
    
    def search_channels_with_keywords_enhanced(self, keywords: List[str], max_per_keyword: int = 25) -> List[str]:
        """Enhanced keyword search with debug logging and performance tracking"""
        logger.info(f"🔍 Enhanced keyword search with {len(keywords)} keywords...")
        logger.info(f"📊 Current existing channels: {len(self.existing_channels)}")
        
        new_channel_ids = set()
        processed_keywords = 0
        total_found = 0
        total_duplicates = 0
        
        for keyword_idx, keyword in enumerate(keywords):
            if len(new_channel_ids) >= self.target_new_channels:
                logger.info(f"🎯 Target of {self.target_new_channels} new channels reached!")
                break
            
            try:
                if self.debug_mode:
                    logger.info(f"🔎 [{keyword_idx+1}/{len(keywords)}] Searching keyword: '{keyword}'")
                
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
                keyword_duplicates = 0
                
                search_results = response.get('items', [])
                if self.debug_mode:
                    logger.info(f"📥 API returned {len(search_results)} results for '{keyword}'")
                
                for item in search_results:
                    if item['id']['kind'] == 'youtube#channel':
                        channel_id = item['id']['channelId'].strip()
                        channel_title = item['snippet'].get('title', 'Unknown')
                        
                        total_found += 1
                        
                        # Enhanced duplicate checking with debugging
                        is_duplicate = channel_id in self.existing_channels
                        is_already_in_new = channel_id in new_channel_ids
                        
                        if self.debug_mode:
                            logger.info(f"🐛 Channel: '{channel_title}' ({channel_id})")
                            logger.info(f"🐛   - In existing: {is_duplicate}")
                            logger.info(f"🐛   - In new batch: {is_already_in_new}")
                        
                        if is_duplicate:
                            keyword_duplicates += 1
                            total_duplicates += 1
                            if self.debug_mode:
                                logger.info(f"🐛   - DUPLICATE: Already exists in database")
                        elif is_already_in_new:
                            keyword_duplicates += 1
                            if self.debug_mode:
                                logger.info(f"🐛   - DUPLICATE: Already in current search batch")
                        else:
                            # This is a new channel!
                            new_channel_ids.add(channel_id)
                            keyword_channels_found += 1
                            if self.debug_mode:
                                logger.info(f"🐛   - ✅ NEW CHANNEL ACCEPTED!")
                
                # Update keyword performance
                self.keyword_engine.update_keyword_performance(keyword, keyword_channels_found)
                
                if self.debug_mode or keyword_channels_found > 0:
                    logger.info(f"📊 Keyword '{keyword}': {keyword_channels_found} new, {keyword_duplicates} duplicates")
                
                time.sleep(random.uniform(0.3, 0.7))
                
            except Exception as e:
                logger.error(f"❌ Error searching for keyword '{keyword}': {e}")
                if "All API keys exhausted" in str(e) or "quotaExceeded" in str(e):
                    logger.warning("⚠️ All API keys exhausted, stopping keyword search")
                    self.stats['quota_exhausted_count'] += 1
                    break
        
        # Update statistics
        self.stats['keywords_processed'] += processed_keywords
        self.stats['channels_found_but_rejected'] += total_duplicates
        self.stats['duplicate_rejections'] += total_duplicates
        self.stats['new_channels_accepted'] += len(new_channel_ids)
        
        logger.info(f"🎉 Enhanced keyword search complete!")
        logger.info(f"📊 Total API results: {total_found}")
        logger.info(f"📊 New channels found: {len(new_channel_ids)}")
        logger.info(f"📊 Duplicates rejected: {total_duplicates}")
        logger.info(f"📊 Success rate: {(len(new_channel_ids)/max(total_found, 1)*100):.1f}%")
        
        return list(new_channel_ids)
    
    def run_enhanced_discovery(self) -> Dict:
        """Run enhanced discovery with all integrated features"""
        logger.info("🚀 Starting enhanced advanced channel discovery...")
        
        all_new_channel_ids = set()
        
        try:
            # Phase 1: Enhanced long-tail keyword discovery with autocomplete
            logger.info("🔍 Phase 1: Long-tail keyword discovery")
            logger.info("🔍 Generating long-tail keyword combinations...")
            long_tail_keywords = self.generate_long_tail_keywords()
            
            # Also get expanded keywords from keyword engine
            expanded_keywords = self.keyword_engine.expand_keywords_comprehensive()
            high_performance_keywords = self.keyword_engine.get_high_performance_keywords(limit=100)
            
            # Combine and prioritize keywords
            all_keywords = high_performance_keywords + [kw for kw in expanded_keywords if kw not in high_performance_keywords]
            all_keywords.extend([kw for kw in long_tail_keywords if kw not in all_keywords])
            
            logger.info(f"✅ Generated {len(all_keywords)} total keywords")
            
            # Use enhanced keyword search
            keyword_channel_ids = self.search_channels_with_keywords_enhanced(all_keywords[:100], max_per_keyword=15)
            all_new_channel_ids.update(keyword_channel_ids)
            
            self.stats['techniques_used'].append('long_tail_keywords')
            self.stats['success_by_technique']['long_tail_keywords'] = len(keyword_channel_ids)
            
            # Phase 2: Trending hashtag discovery
            logger.info("📈 Phase 2: Trending hashtag discovery")
            logger.info("📈 Discovering from trending hashtags...")
            hashtag_channels = self.discover_from_trending_hashtags()
            all_new_channel_ids.update(hashtag_channels)
            
            self.stats['techniques_used'].append('trending_hashtags')
            self.stats['success_by_technique']['trending_hashtags'] = len(hashtag_channels)
            
            # Phase 3: Comment thread mining
            logger.info("💬 Phase 3: Comment thread mining")
            logger.info("💬 Mining comment threads from seed channels...")
            seed_channels = list(self.existing_channels)[-50:]  # Use recent discoveries as seeds
            comment_channels = self.discover_from_comment_threads(seed_channels)
            all_new_channel_ids.update(comment_channels)
            
            self.stats['techniques_used'].append('comment_mining')
            self.stats['success_by_technique']['comment_mining'] = len(comment_channels)
            
            # Phase 4: Playlist discovery
            logger.info("📋 Phase 4: Playlist discovery")
            logger.info("📋 Discovering from playlists of seed channels...")
            playlist_channels = self.discover_from_playlists(seed_channels)
            all_new_channel_ids.update(playlist_channels)
            
            self.stats['techniques_used'].append('playlist_discovery')
            self.stats['success_by_technique']['playlist_discovery'] = len(playlist_channels)
            
            # Phase 5: Micro-geographic targeting
            logger.info("🗺️ Phase 5: Micro-geographic discovery")
            logger.info("🗺️ Discovering channels using micro-geographic targeting...")
            micro_geo_channels = self.discover_micro_geographic()
            all_new_channel_ids.update(micro_geo_channels)
            
            self.stats['techniques_used'].append('micro_geographic')
            self.stats['success_by_technique']['micro_geographic'] = len(micro_geo_channels)
            
            # Phase 6: Popular videos discovery (NEW)
            logger.info("🔥 Phase 6: Popular videos discovery")
            popular_channels = self.discover_from_popular_videos()
            all_new_channel_ids.update(popular_channels)
            
            self.stats['techniques_used'].append('popular_videos')
            self.stats['success_by_technique']['popular_videos'] = len(popular_channels)
            
            # Get detailed information for all new channels
            if all_new_channel_ids:
                logger.info(f"📊 Getting details for {len(all_new_channel_ids)} potential new channels...")
                detailed_channels = self.get_channel_details_batch(list(all_new_channel_ids))
                
                # Filter for Sri Lankan channels
                sri_lankan_channels = [
                    ch for ch in detailed_channels 
                    if ch['sri_lankan_score'] >= 1.0
                ]
                
                # Save new channels with smart categorization
                if sri_lankan_channels:
                    self.save_new_channels(sri_lankan_channels)
                    logger.info(f"🎉 Successfully discovered {len(sri_lankan_channels)} new Sri Lankan channels!")
                else:
                    logger.info("😔 No new Sri Lankan channels found this session")
            else:
                logger.info("😔 No new channel IDs discovered")
        
        except Exception as e:
            if "All API keys exhausted" in str(e) or "quotaExceeded" in str(e):
                logger.warning("⚠️ All API keys exhausted, stopping discovery")
                self.stats['quota_exhausted_count'] += 1
            else:
                logger.error(f"❌ Discovery error: {e}")
        
        # Final statistics
        self.stats['session_end'] = datetime.now().isoformat()
        
        return self.stats
    
    def run_advanced_discovery(self) -> Dict:
        """Legacy method - calls enhanced discovery"""
        return self.run_enhanced_discovery()

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Enhanced Advanced Sri Lankan YouTube Channel Discovery")
    parser.add_argument('--target', type=int, default=100, help='Target number of new channels to discover')
    parser.add_argument('--output-dir', help='Output directory for discovered channels')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with detailed logging')
    
    args = parser.parse_args()
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize enhanced advanced discovery system
        discovery = AdvancedChannelDiscovery(
            output_dir=args.output_dir,
            target_new_channels=args.target,
            debug_mode=args.debug
        )
        
        # Run enhanced advanced discovery
        stats = discovery.run_enhanced_discovery()
        
        print(f"\n=== Enhanced Advanced Discovery Session Complete ===")
        print(f"Existing channels at start: {stats['channels_at_start']}")
        print(f"New channels discovered: {stats['new_channels_found']}")
        print(f"API calls made: {stats['api_calls_made']}")
        print(f"Techniques used: {', '.join(stats['techniques_used'])}")
        print(f"Success by technique:")
        for technique, count in stats['success_by_technique'].items():
            print(f"  - {technique}: {count} channels")
        
        if args.debug:
            print(f"\nDebug Statistics:")
            print(f"Keywords processed: {stats['keywords_processed']}")
            print(f"Duplicate rejections: {stats['duplicate_rejections']}")
            print(f"New channels accepted: {stats['new_channels_accepted']}")
            print(f"Quota exhausted count: {stats['quota_exhausted_count']}")
        
        if stats['new_channels_found'] > 0:
            print("🎉 SUCCESS! New channels discovered and saved!")
        else:
            print("😔 No new channels found this session. Try again later or adjust search parameters.")
        
    except Exception as e:
        logger.error(f"Enhanced advanced discovery failed: {e}")
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
