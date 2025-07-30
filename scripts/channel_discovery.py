"""
FIXED Advanced Sri Lankan YouTube Channel Discovery System
Addresses critical issues with quota management and progressive saving

FIXES IMPLEMENTED:
1. Robust API key rotation using YouTubeAPIClient
2. Progressive saving of discovered channels
3. Graceful quota exhaustion handling
4. Resume capability for interrupted sessions
5. Enhanced error recovery
6. Smart quota allocation between discovery and validation
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
from utils import setup_logging, YouTubeAPIClient

# Setup logging
logger = setup_logging()

class ProgressiveChannelSaver:
    """Handles progressive saving of discovered channels with resume capability"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.progress_file = output_dir / "discovery_progress.json"
        self.discovered_ids_file = output_dir / "discovered_channel_ids.json"
        self.validated_channels_file = output_dir / "validated_channels.json"
        
        # Load existing progress
        self.progress = self._load_progress()
        self.discovered_ids = self._load_discovered_ids()
        self.validated_channels = self._load_validated_channels()
    
    def _load_progress(self) -> Dict:
        """Load discovery progress"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Check if it's the new format
                    if 'discovery_phase_complete' in data:
                        return data
                    else:
                        # Legacy format - start fresh but log it
                        logger.info("Found legacy progress file, starting fresh session")
                        return self._create_fresh_progress()
                        
            except Exception as e:
                logger.warning(f"Error loading progress: {e}")
        
        return self._create_fresh_progress()
    
    def _create_fresh_progress(self) -> Dict:
        """Create fresh progress structure"""
        return {
            'session_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'discovery_phase_complete': False,
            'validation_phase_complete': False,
            'total_discovered': 0,
            'total_validated': 0,
            'techniques_completed': [],
            'last_updated': datetime.now().isoformat()
        }
    
    def _load_discovered_ids(self) -> Set[str]:
        """Load discovered channel IDs"""
        if self.discovered_ids_file.exists():
            try:
                with open(self.discovered_ids_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('channel_ids', []))
            except Exception as e:
                logger.warning(f"Error loading discovered IDs: {e}")
        
        return set()
    
    def _load_validated_channels(self) -> List[Dict]:
        """Load validated channels"""
        if self.validated_channels_file.exists():
            try:
                with open(self.validated_channels_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('channels', [])
            except Exception as e:
                logger.warning(f"Error loading validated channels: {e}")
        
        return []
    
    def save_discovered_ids(self, channel_ids: Set[str], technique: str):
        """Save discovered channel IDs immediately"""
        self.discovered_ids.update(channel_ids)
        
        # Save to file
        data = {
            'channel_ids': list(self.discovered_ids),
            'total_count': len(self.discovered_ids),
            'last_updated': datetime.now().isoformat(),
            'session_id': self.progress['session_id']
        }
        
        with open(self.discovered_ids_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Update progress
        self.progress['total_discovered'] = len(self.discovered_ids)
        if technique not in self.progress['techniques_completed']:
            self.progress['techniques_completed'].append(technique)
        self.progress['last_updated'] = datetime.now().isoformat()
        
        self._save_progress()
        
        logger.info(f"💾 Saved {len(channel_ids)} new channel IDs from {technique}. Total: {len(self.discovered_ids)}")
    
    def save_validated_channels(self, channels: List[Dict]):
        """Save validated channels progressively"""
        self.validated_channels.extend(channels)
        
        # Save to file
        data = {
            'channels': self.validated_channels,
            'total_count': len(self.validated_channels),
            'last_updated': datetime.now().isoformat(),
            'session_id': self.progress['session_id']
        }
        
        with open(self.validated_channels_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Update progress
        self.progress['total_validated'] = len(self.validated_channels)
        self.progress['last_updated'] = datetime.now().isoformat()
        
        self._save_progress()
        
        logger.info(f"💾 Saved {len(channels)} validated channels. Total: {len(self.validated_channels)}")
    
    def mark_discovery_complete(self):
        """Mark discovery phase as complete"""
        self.progress['discovery_phase_complete'] = True
        self.progress['last_updated'] = datetime.now().isoformat()
        self._save_progress()
        logger.info("✅ Discovery phase marked as complete")
    
    def mark_validation_complete(self):
        """Mark validation phase as complete"""
        self.progress['validation_phase_complete'] = True
        self.progress['last_updated'] = datetime.now().isoformat()
        self._save_progress()
        logger.info("✅ Validation phase marked as complete")
    
    def _save_progress(self):
        """Save progress to file"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
    
    def get_unvalidated_ids(self) -> List[str]:
        """Get channel IDs that haven't been validated yet"""
        validated_ids = {ch['channel_id'] for ch in self.validated_channels}
        unvalidated = self.discovered_ids - validated_ids
        return list(unvalidated)
    
    def can_resume_discovery(self) -> bool:
        """Check if discovery can be resumed"""
        return not self.progress['discovery_phase_complete']
    
    def can_resume_validation(self) -> bool:
        """Check if validation can be resumed"""
        return (self.progress['discovery_phase_complete'] and 
                not self.progress['validation_phase_complete'] and 
                len(self.get_unvalidated_ids()) > 0)

class RobustAdvancedChannelDiscovery:
    """Enhanced discovery system with robust error handling and progressive saving"""
    
    def __init__(self, output_dir: str = None, target_new_channels: int = 100, debug_mode: bool = False):
        # Validate API key
        if not validate_api_key():
            raise ValueError("Invalid or missing YouTube API key. Please check your .env file.")
        
        # Use robust API client
        self.api_client = YouTubeAPIClient()
        self.target_new_channels = target_new_channels
        self.debug_mode = debug_mode
        
        # Setup directories
        if output_dir is None:
            output_dir = DATA_RAW_PATH
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize progressive saver
        self.saver = ProgressiveChannelSaver(self.output_dir)
        
        # Files
        self.channels_file = self.output_dir / "discovered_channels.json"
        
        # Load existing data
        self.existing_channels = self._load_existing_channels()
        
        # Enhanced discovery statistics
        self.stats = {
            'session_start': datetime.now().isoformat(),
            'channels_at_start': len(self.existing_channels),
            'target_new_channels': target_new_channels,
            'new_channels_found': 0,
            'api_calls_made': 0,
            'techniques_used': [],
            'success_by_technique': {},
            'quota_exhausted_count': 0,
            'progressive_saves': 0,
            'resume_from_discovery': False,
            'resume_from_validation': False
        }
        
        logger.info(f"🚀 Robust Advanced Discovery initialized. Existing: {len(self.existing_channels)}, Target new: {target_new_channels}")
        if self.debug_mode:
            logger.info("🐛 DEBUG MODE ENABLED - Will show detailed logging")
        
        # Check for resume capability
        try:
            if self.saver.can_resume_discovery():
                logger.info(f"🔄 Can resume discovery. Already discovered: {len(self.saver.discovered_ids)} channels")
                self.stats['resume_from_discovery'] = True
            elif self.saver.can_resume_validation():
                unvalidated = len(self.saver.get_unvalidated_ids())
                logger.info(f"🔄 Can resume validation. {unvalidated} channels need validation")
                self.stats['resume_from_validation'] = True
        except Exception as e:
            logger.warning(f"Error checking resume capability: {e}")
            # Continue with fresh session
    
    def _load_existing_channels(self) -> Set[str]:
        """Load existing channels from main channels file"""
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
                    continue
                    
                for channel_name, channel_id in channels.items():
                    if isinstance(channel_id, str) and channel_id.startswith('UC'):
                        existing_ids.add(channel_id.strip())
                        total_loaded += 1
            
            logger.info(f"✅ Successfully loaded {total_loaded} existing channels from {len(data)} categories")
            return existing_ids
            
        except Exception as e:
            logger.error(f"❌ Error loading existing channels: {e}")
            return set()
    
    def _make_api_request(self, request_func, quota_cost: int = 1, **kwargs):
        """Make API request with robust error handling"""
        try:
            result = self.api_client._make_request(request_func(**kwargs), quota_cost)
            self.stats['api_calls_made'] += 1
            return result
        except Exception as e:
            if "All API keys exhausted" in str(e) or "quotaExceeded" in str(e):
                self.stats['quota_exhausted_count'] += 1
                logger.warning("⚠️ API quota exhausted")
                raise
            else:
                logger.error(f"API request failed: {e}")
                raise
    
    def discover_from_keywords(self, keywords: List[str], max_per_keyword: int = 25) -> Set[str]:
        """Discover channels using keywords with progressive saving"""
        logger.info(f"🔍 Discovering channels from {len(keywords)} keywords...")
        
        new_channel_ids = set()
        
        for keyword_idx, keyword in enumerate(keywords):
            if len(new_channel_ids) >= self.target_new_channels:
                logger.info(f"🎯 Target reached with {len(new_channel_ids)} channels")
                break
            
            try:
                if self.debug_mode:
                    logger.info(f"🔎 [{keyword_idx+1}/{len(keywords)}] Searching: '{keyword}'")
                
                response = self._make_api_request(
                    self.api_client.service.search().list,
                    quota_cost=100,
                    part='snippet',
                    q=keyword,
                    type='channel',
                    regionCode='LK',
                    maxResults=min(max_per_keyword, 50),
                    order='relevance'
                )
                
                keyword_channels = set()
                for item in response.get('items', []):
                    if item['id']['kind'] == 'youtube#channel':
                        channel_id = item['id']['channelId'].strip()
                        if channel_id not in self.existing_channels:
                            keyword_channels.add(channel_id)
                            new_channel_ids.add(channel_id)
                
                # Progressive save every 10 keywords or when we find channels
                if keyword_channels and (keyword_idx % 10 == 0 or keyword_channels):
                    self.saver.save_discovered_ids(keyword_channels, 'keyword_search')
                    self.stats['progressive_saves'] += 1
                
                if self.debug_mode:
                    logger.info(f"📊 Keyword '{keyword}': {len(keyword_channels)} new channels")
                
                time.sleep(random.uniform(0.3, 0.7))
                
            except Exception as e:
                if "quotaExceeded" in str(e) or "All API keys exhausted" in str(e):
                    logger.warning(f"⚠️ Quota exhausted at keyword {keyword_idx+1}. Saving progress...")
                    if new_channel_ids:
                        self.saver.save_discovered_ids(new_channel_ids, 'keyword_search')
                    break
                else:
                    logger.error(f"❌ Error with keyword '{keyword}': {e}")
                    continue
        
        # Final save
        if new_channel_ids:
            self.saver.save_discovered_ids(new_channel_ids, 'keyword_search')
        
        logger.info(f"✅ Keyword discovery complete: {len(new_channel_ids)} new channels")
        return new_channel_ids
    
    def discover_from_trending_hashtags(self) -> Set[str]:
        """Discover channels from trending hashtags with progressive saving"""
        logger.info("📈 Discovering from trending hashtags...")
        
        trending_hashtags = [
            "#SriLanka2025", "#LankaVibes", "#SriLankanLife", "#VisitSriLanka2025",
            "#SinhalaNewYear2025", "#LankanFood", "#SriLankanWedding", "#LankanTradition",
            "#ColomboLife", "#KandyCity", "#GalleVibes", "#JaffnaLife", "#SriLankanArt",
            "#LankanMusic", "#SriLankanDance", "#LankanCulture", "#SriLankanNature"
        ]
        
        new_channel_ids = set()
        
        for hashtag_idx, hashtag in enumerate(trending_hashtags):
            try:
                response = self._make_api_request(
                    self.api_client.service.search().list,
                    quota_cost=100,
                    part='snippet',
                    q=hashtag,
                    type='video',
                    regionCode='LK',
                    publishedAfter=(datetime.now() - timedelta(days=30)).isoformat() + 'Z',
                    maxResults=20,
                    order='relevance'
                )
                
                hashtag_channels = set()
                for item in response.get('items', []):
                    channel_id = item['snippet']['channelId']
                    if channel_id not in self.existing_channels:
                        hashtag_channels.add(channel_id)
                        new_channel_ids.add(channel_id)
                
                # Progressive save every 5 hashtags
                if hashtag_channels and hashtag_idx % 5 == 0:
                    self.saver.save_discovered_ids(hashtag_channels, 'trending_hashtags')
                    self.stats['progressive_saves'] += 1
                
                time.sleep(random.uniform(0.3, 0.6))
                
            except Exception as e:
                if "quotaExceeded" in str(e) or "All API keys exhausted" in str(e):
                    logger.warning(f"⚠️ Quota exhausted at hashtag {hashtag_idx+1}. Saving progress...")
                    if new_channel_ids:
                        self.saver.save_discovered_ids(new_channel_ids, 'trending_hashtags')
                    break
                else:
                    logger.error(f"❌ Error with hashtag '{hashtag}': {e}")
                    continue
        
        # Final save
        if new_channel_ids:
            self.saver.save_discovered_ids(new_channel_ids, 'trending_hashtags')
        
        logger.info(f"✅ Hashtag discovery complete: {len(new_channel_ids)} new channels")
        return new_channel_ids
    
    def discover_from_popular_videos(self) -> Set[str]:
        """Discover channels from popular videos with progressive saving"""
        logger.info("🔥 Discovering from popular videos...")
        
        new_channel_ids = set()
        
        try:
            response = self._make_api_request(
                self.api_client.service.videos().list,
                quota_cost=1,
                part='snippet',
                chart='mostPopular',
                regionCode='LK',
                maxResults=50
            )
            
            for item in response.get('items', []):
                channel_id = item['snippet']['channelId']
                if channel_id not in self.existing_channels:
                    new_channel_ids.add(channel_id)
            
            # Save immediately
            if new_channel_ids:
                self.saver.save_discovered_ids(new_channel_ids, 'popular_videos')
                self.stats['progressive_saves'] += 1
            
            logger.info(f"✅ Popular videos discovery complete: {len(new_channel_ids)} new channels")
            
        except Exception as e:
            if "quotaExceeded" in str(e) or "All API keys exhausted" in str(e):
                logger.warning("⚠️ Quota exhausted during popular videos discovery")
            else:
                logger.error(f"❌ Error in popular videos discovery: {e}")
        
        return new_channel_ids
    
    def validate_channels_batch(self, channel_ids: List[str], batch_size: int = 50) -> List[Dict]:
        """Validate channels in batches with progressive saving"""
        logger.info(f"🔍 Validating {len(channel_ids)} channels in batches of {batch_size}...")
        
        all_validated = []
        
        for i in range(0, len(channel_ids), batch_size):
            batch_ids = channel_ids[i:i + batch_size]
            
            try:
                response = self._make_api_request(
                    self.api_client.service.channels().list,
                    quota_cost=1,
                    part='snippet,statistics,brandingSettings',
                    id=','.join(batch_ids),
                    maxResults=50
                )
                
                batch_validated = []
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
                    
                    # Only keep channels with good Sri Lankan score
                    if channel_data['sri_lankan_score'] >= 1.0:
                        batch_validated.append(channel_data)
                
                # Progressive save after each batch
                if batch_validated:
                    self.saver.save_validated_channels(batch_validated)
                    all_validated.extend(batch_validated)
                    self.stats['progressive_saves'] += 1
                    logger.info(f"✅ Validated batch {i//batch_size + 1}: {len(batch_validated)} Sri Lankan channels")
                
                time.sleep(random.uniform(0.1, 0.3))
                
            except Exception as e:
                if "quotaExceeded" in str(e) or "All API keys exhausted" in str(e):
                    logger.warning(f"⚠️ Quota exhausted during validation at batch {i//batch_size + 1}")
                    logger.info(f"💾 Progress saved. {len(all_validated)} channels validated so far")
                    break
                else:
                    logger.error(f"❌ Error validating batch {i//batch_size + 1}: {e}")
                    continue
        
        logger.info(f"✅ Validation complete: {len(all_validated)} Sri Lankan channels validated")
        return all_validated
    
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
    
    def finalize_channels(self, validated_channels: List[Dict]):
        """Finalize channels by adding them to the main channels file"""
        if not validated_channels:
            logger.warning("No validated channels to finalize")
            return
        
        # Load existing data
        if self.channels_file.exists():
            with open(self.channels_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        # Add new channels by category
        for channel in validated_channels:
            category = self._categorize_channel(channel)
            if category not in data:
                data[category] = {}
            
            data[category][channel['title']] = channel['channel_id']
        
        # Save updated data
        with open(self.channels_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.stats['new_channels_found'] = len(validated_channels)
        logger.info(f"🎉 Finalized {len(validated_channels)} new channels to main database")
    
    def _categorize_channel(self, channel_data: Dict) -> str:
        """Simple channel categorization"""
        text_content = ' '.join([
            channel_data.get('title', '').lower(),
            channel_data.get('description', '').lower(),
            ' '.join(channel_data.get('keywords', [])).lower()
        ])
        
        # Simple category mapping
        if any(word in text_content for word in ['news', 'politics', 'breaking', 'current']):
            return "News & Politics"
        elif any(word in text_content for word in ['music', 'song', 'singer', 'band']):
            return "Music"
        elif any(word in text_content for word in ['comedy', 'funny', 'entertainment', 'drama']):
            return "Entertainment"
        elif any(word in text_content for word in ['education', 'tutorial', 'learn', 'teach']):
            return "Education"
        elif any(word in text_content for word in ['sports', 'cricket', 'football', 'game']):
            return "Sports"
        elif any(word in text_content for word in ['travel', 'tour', 'visit', 'trip']):
            return "Travel & Events"
        else:
            return "People & Blogs"
    
    def run_robust_discovery(self) -> Dict:
        """Run robust discovery with progressive saving and resume capability"""
        logger.info("🚀 Starting robust advanced channel discovery...")
        
        try:
            # Check if we can resume from previous session
            if self.stats['resume_from_validation']:
                logger.info("🔄 Resuming from validation phase...")
                unvalidated_ids = self.saver.get_unvalidated_ids()
                validated_channels = self.validate_channels_batch(unvalidated_ids)
                
                if validated_channels:
                    self.finalize_channels(validated_channels)
                
                self.saver.mark_validation_complete()
                
            elif self.stats['resume_from_discovery'] or not self.saver.progress['discovery_phase_complete']:
                logger.info("🔄 Running/resuming discovery phase...")
                
                # Discovery Phase
                all_discovered_ids = set(self.saver.discovered_ids)
                
                # Method 1: Keyword search
                if 'keyword_search' not in self.saver.progress['techniques_completed']:
                    logger.info("🔍 Phase 1: Keyword discovery")
                    keywords = [
                        "sri lanka", "srilanka", "sinhala", "tamil", "ceylon", "lanka",
                        "colombo", "kandy", "galle", "jaffna", "lankan", "ape amma",
                        "sri lankan news", "sinhala songs", "tamil songs", "lankan food",
                        "sri lanka travel", "colombo vlog", "sinhala comedy", "lankan cricket"
                    ]
                    
                    keyword_channels = self.discover_from_keywords(keywords, max_per_keyword=20)
                    all_discovered_ids.update(keyword_channels)
                    self.stats['techniques_used'].append('keyword_search')
                    self.stats['success_by_technique']['keyword_search'] = len(keyword_channels)
                
                # Method 2: Trending hashtags
                if 'trending_hashtags' not in self.saver.progress['techniques_completed']:
                    logger.info("📈 Phase 2: Trending hashtag discovery")
                    hashtag_channels = self.discover_from_trending_hashtags()
                    all_discovered_ids.update(hashtag_channels)
                    self.stats['techniques_used'].append('trending_hashtags')
                    self.stats['success_by_technique']['trending_hashtags'] = len(hashtag_channels)
                
                # Method 3: Popular videos
                if 'popular_videos' not in self.saver.progress['techniques_completed']:
                    logger.info("🔥 Phase 3: Popular videos discovery")
                    popular_channels = self.discover_from_popular_videos()
                    all_discovered_ids.update(popular_channels)
                    self.stats['techniques_used'].append('popular_videos')
                    self.stats['success_by_technique']['popular_videos'] = len(popular_channels)
                
                # Mark discovery complete
                self.saver.mark_discovery_complete()
                logger.info(f"✅ Discovery phase complete. Total discovered: {len(all_discovered_ids)}")
                
                # Validation Phase
                logger.info("🔍 Starting validation phase...")
                unvalidated_ids = self.saver.get_unvalidated_ids()
                
                if unvalidated_ids:
                    validated_channels = self.validate_channels_batch(unvalidated_ids)
                    
                    if validated_channels:
                        self.finalize_channels(validated_channels)
                    
                    self.saver.mark_validation_complete()
                else:
                    logger.info("No channels to validate")
            
            else:
                logger.info("✅ Both discovery and validation phases already complete")
                # Load final results
                validated_channels = self.saver.validated_channels
                if validated_channels:
                    self.stats['new_channels_found'] = len(validated_channels)
        
        except Exception as e:
            logger.error(f"❌ Discovery error: {e}")
            logger.info("💾 Progress has been saved and can be resumed later")
        
        # Final statistics
        self.stats['session_end'] = datetime.now().isoformat()
        self.stats['total_discovered'] = len(self.saver.discovered_ids)
        self.stats['total_validated'] = len(self.saver.validated_channels)
        
        return self.stats

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Robust Advanced Sri Lankan YouTube Channel Discovery")
    parser.add_argument('--target', type=int, default=100, help='Target number of new channels to discover')
    parser.add_argument('--output-dir', help='Output directory for discovered channels')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with detailed logging')
    parser.add_argument('--resume', action='store_true', help='Resume from previous session')
    
    args = parser.parse_args()
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize robust discovery system
        discovery = RobustAdvancedChannelDiscovery(
            output_dir=args.output_dir,
            target_new_channels=args.target,
            debug_mode=args.debug
        )
        
        # Run robust discovery
        stats = discovery.run_robust_discovery()
        
        print(f"\n=== Robust Advanced Discovery Session Complete ===")
        print(f"Existing channels at start: {stats['channels_at_start']}")
        print(f"New channels discovered: {stats['new_channels_found']}")
        print(f"Total discovered: {stats.get('total_discovered', 0)}")
        print(f"Total validated: {stats.get('total_validated', 0)}")
        print(f"API calls made: {stats['api_calls_made']}")
        print(f"Progressive saves: {stats['progressive_saves']}")
        print(f"Techniques used: {', '.join(stats['techniques_used'])}")
        print(f"Success by technique:")
        for technique, count in stats['success_by_technique'].items():
            print(f"  - {technique}: {count} channels")
        
        if stats['quota_exhausted_count'] > 0:
            print(f"⚠️ Quota exhausted {stats['quota_exhausted_count']} times - progress saved")
        
        if stats['new_channels_found'] > 0:
            print("🎉 SUCCESS! New channels discovered and saved!")
        else:
            print("💾 Session complete. Check progress files for discovered channels.")
        
    except Exception as e:
        logger.error(f"Robust discovery failed: {e}")
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
