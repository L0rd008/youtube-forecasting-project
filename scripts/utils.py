"""
Utility functions for YouTube Data Collection System
Contains helper functions for API interactions, data processing, and common operations
"""

import re
import time
import logging
import pytz
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from isodate import parse_duration
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import json

from config import (
    YOUTUBE_API_KEY, 
    YOUTUBE_API_KEYS,
    TIMEZONE, 
    COLLECTION_PARAMS,
    LOG_LEVEL,
    LOG_FILE_PATH
)

# Detect if we're on Windows and console doesn't support Unicode
def _supports_unicode():
    """Check if the current console supports Unicode characters"""
    try:
        # Try to encode some Unicode characters
        test_chars = "🚀✅❌"
        if sys.platform.startswith('win'):
            # On Windows, check if we can encode to the console's encoding
            console_encoding = sys.stdout.encoding or 'cp1252'
            test_chars.encode(console_encoding)
        return True
    except (UnicodeEncodeError, AttributeError):
        return False

# Unicode-safe logging symbols
UNICODE_SUPPORT = _supports_unicode()

class LogSymbols:
    """Platform-safe logging symbols"""
    if UNICODE_SUPPORT:
        ROCKET = "🚀"
        SUCCESS = "✅"
        ERROR = "❌"
        WARNING = "⚠️"
        INFO = "ℹ️"
        STOP = "⏹️"
        CLEANUP = "🧹"
        TEST = "🧪"
        CHART = "📊"
        SEARCH = "🔍"
        PROCESS = "🔄"
    else:
        ROCKET = "[START]"
        SUCCESS = "[OK]"
        ERROR = "[FAIL]"
        WARNING = "[WARN]"
        INFO = "[INFO]"
        STOP = "[STOP]"
        CLEANUP = "[CLEAN]"
        TEST = "[TEST]"
        CHART = "[CHART]"
        SEARCH = "[SEARCH]"
        PROCESS = "[PROC]"

# Set up logging
def setup_logging():
    """Set up logging configuration with Windows-safe formatting"""
    # Create a custom formatter that handles encoding issues
    class SafeFormatter(logging.Formatter):
        def format(self, record):
            # Get the original formatted message
            formatted = super().format(record)
            
            # If we don't support Unicode, replace common emoji with safe alternatives
            if not UNICODE_SUPPORT:
                replacements = {
                    '🚀': LogSymbols.ROCKET,
                    '✅': LogSymbols.SUCCESS,
                    '❌': LogSymbols.ERROR,
                    '⚠️': LogSymbols.WARNING,
                    'ℹ️': LogSymbols.INFO,
                    '⏹️': LogSymbols.STOP,
                    '🧹': LogSymbols.CLEANUP,
                    '🧪': LogSymbols.TEST,
                    '📊': LogSymbols.CHART,
                    '🔍': LogSymbols.SEARCH,
                    '🔄': LogSymbols.PROCESS,
                }
                
                for unicode_char, safe_char in replacements.items():
                    formatted = formatted.replace(unicode_char, safe_char)
            
            return formatted
    
    # Set up handlers
    handlers = []
    
    # File handler (always supports UTF-8)
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    handlers.append(file_handler)
    
    # Console handler with safe formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(SafeFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    handlers.append(console_handler)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

class YouTubeAPIClient:
    """YouTube API client with multi-key rotation, rate limiting and error handling"""
    
    def __init__(self, api_keys: List[str] = None):
        self.api_keys = api_keys or YOUTUBE_API_KEYS
        if not self.api_keys:
            raise ValueError("No valid API keys found. Please check your .env file.")
        
        self.current_key_index = 0
        self.current_key = self.api_keys[0]
        self.service = None
        self.quota_used = 0
        self.last_request_time = 0
        self.key_quotas = {key: 0 for key in self.api_keys}  # Track quota per key
        self.exhausted_keys = set()  # Track exhausted keys
        
        self._initialize_service()
        logger.info(f"Initialized YouTube API client with {len(self.api_keys)} API key(s)")
    
    def _initialize_service(self):
        """Initialize YouTube API service with current key"""
        try:
            if not self.current_key:
                raise ValueError("Invalid or missing YouTube API key. Please check your .env file.")
            
            self.service = build('youtube', 'v3', developerKey=self.current_key)
            logger.info(f"YouTube API service initialized with key {self.current_key_index + 1}")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube API service: {e}")
            raise
    
    def _rotate_api_key(self):
        """Rotate to next available API key"""
        if len(self.api_keys) <= 1:
            logger.warning("Only one API key available, cannot rotate")
            return False
        
        # Find next non-exhausted key
        original_index = self.current_key_index
        attempts = 0
        
        while attempts < len(self.api_keys):
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            next_key = self.api_keys[self.current_key_index]
            
            if next_key not in self.exhausted_keys:
                self.current_key = next_key
                self._initialize_service()
                logger.info(f"Rotated to API key {self.current_key_index + 1}")
                return True
            
            attempts += 1
        
        # All keys exhausted
        logger.error("All API keys have been exhausted")
        return False
    
    def _mark_key_exhausted(self, key: str):
        """Mark an API key as quota exhausted"""
        self.exhausted_keys.add(key)
        logger.warning(f"API key {self.api_keys.index(key) + 1} marked as exhausted")
    
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = COLLECTION_PARAMS['rate_limit_delay']
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, request, quota_cost: int = 1):
        """Make API request with error handling, retry logic, and key rotation"""
        max_retries = COLLECTION_PARAMS['max_retries']
        retry_delay = COLLECTION_PARAMS['retry_delay']
        
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                response = request.execute()
                
                # Update quota tracking
                self.quota_used += quota_cost
                self.key_quotas[self.current_key] += quota_cost
                
                logger.debug(f"API request successful. Total quota used: {self.quota_used}, Current key quota: {self.key_quotas[self.current_key]}")
                return response
                
            except HttpError as e:
                error_code = e.resp.status
                error_message = str(e)
                
                if error_code == 403 and 'quotaExceeded' in error_message:
                    logger.warning(f"API key {self.current_key_index + 1} quota exceeded")
                    self._mark_key_exhausted(self.current_key)
                    
                    # Try to rotate to next key
                    if self._rotate_api_key():
                        logger.info("Retrying with new API key...")
                        # Rebuild the request with new service
                        continue
                    else:
                        logger.error("All API keys exhausted. Please try again tomorrow.")
                        raise Exception("All API keys exhausted. Please try again tomorrow.")
                
                elif error_code == 403 and ('keyInvalid' in error_message or 'forbidden' in error_message.lower()):
                    logger.error(f"Invalid API key {self.current_key_index + 1}: {error_message}")
                    self._mark_key_exhausted(self.current_key)
                    
                    # Try to rotate to next key
                    if self._rotate_api_key():
                        logger.info("Retrying with new API key...")
                        continue
                    else:
                        logger.error("No valid API keys available")
                        raise Exception("Invalid or missing YouTube API key. Please check your .env file.")
                
                elif error_code in [500, 502, 503, 504]:
                    # Server errors - retry with exponential backoff
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"Server error {error_code}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Server error {error_code} after {max_retries} attempts")
                        raise
                
                else:
                    logger.error(f"API error {error_code}: {error_message}")
                    raise
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Request failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Request failed after {max_retries} attempts: {e}")
                    raise
        
        return None
    
    def get_quota_status(self) -> Dict:
        """Get current quota usage status"""
        return {
            'total_quota_used': self.quota_used,
            'key_quotas': self.key_quotas.copy(),
            'current_key_index': self.current_key_index,
            'exhausted_keys': len(self.exhausted_keys),
            'available_keys': len(self.api_keys) - len(self.exhausted_keys)
        }
    
    def reset_quota_tracking(self):
        """Reset quota tracking (call this daily)"""
        self.quota_used = 0
        self.key_quotas = {key: 0 for key in self.api_keys}
        self.exhausted_keys.clear()
        logger.info("Quota tracking reset")
    
    def reset_exhausted_keys(self):
        """Reset exhausted keys tracking for fresh session"""
        self.exhausted_keys.clear()
        logger.info("Exhausted keys tracking reset")

# YouTube API Helper Functions
def get_channel_info(client: YouTubeAPIClient, channel_ids: List[str]) -> List[Dict]:
    """Get channel information for given channel IDs"""
    if not channel_ids:
        return []
    
    # YouTube API allows up to 50 IDs per request
    batch_size = 50
    all_channels = []
    
    for i in range(0, len(channel_ids), batch_size):
        batch_ids = channel_ids[i:i + batch_size]
        id_string = ','.join(batch_ids)
        
        request = client.service.channels().list(
            part=','.join(COLLECTION_PARAMS['channel_parts']),
            id=id_string
        )
        
        response = client._make_request(request, quota_cost=5)
        if response and 'items' in response:
            all_channels.extend(response['items'])
    
    return all_channels

def get_channel_videos(client: YouTubeAPIClient, channel_id: str, max_results: int = 50) -> List[str]:
    """Get video IDs from a channel"""
    video_ids = []
    next_page_token = None
    
    while len(video_ids) < max_results:
        request = client.service.search().list(
            part='snippet',
            channelId=channel_id,
            type='video',
            order='date',
            maxResults=min(50, max_results - len(video_ids)),
            pageToken=next_page_token
        )
        
        response = client._make_request(request, quota_cost=100)
        if not response or 'items' not in response:
            break
        
        for item in response['items']:
            video_ids.append(item['id']['videoId'])
        
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    
    return video_ids

def get_video_details(client: YouTubeAPIClient, video_ids: List[str]) -> List[Dict]:
    """Get detailed information for given video IDs"""
    if not video_ids:
        return []
    
    batch_size = 50
    all_videos = []
    
    for i in range(0, len(video_ids), batch_size):
        batch_ids = video_ids[i:i + batch_size]
        id_string = ','.join(batch_ids)
        
        request = client.service.videos().list(
            part=','.join(COLLECTION_PARAMS['video_parts']),
            id=id_string
        )
        
        response = client._make_request(request, quota_cost=5)
        if response and 'items' in response:
            all_videos.extend(response['items'])
    
    return all_videos

# Data Processing Helper Functions
def parse_iso_duration(iso_duration: str) -> int:
    """Convert ISO 8601 duration to seconds"""
    try:
        duration = parse_duration(iso_duration)
        return int(duration.total_seconds())
    except Exception as e:
        logger.warning(f"Failed to parse duration '{iso_duration}': {e}")
        return 0

def convert_to_local_time(utc_time_str: str, timezone: str = TIMEZONE) -> datetime:
    """Convert UTC time string to local timezone"""
    try:
        # Parse UTC time
        utc_time = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
        
        # Convert to local timezone
        local_tz = pytz.timezone(timezone)
        local_time = utc_time.astimezone(local_tz)
        
        return local_time
    except Exception as e:
        logger.warning(f"Failed to convert time '{utc_time_str}': {e}")
        return datetime.now(pytz.timezone(timezone))

def extract_video_metadata(video_data: Dict) -> Dict:
    """Extract and normalize video metadata from API response"""
    try:
        snippet = video_data.get('snippet', {})
        statistics = video_data.get('statistics', {})
        content_details = video_data.get('contentDetails', {})
        status = video_data.get('status', {})
        
        # Basic metadata
        metadata = {
            'video_id': video_data.get('id', ''),
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'channel_id': snippet.get('channelId', ''),
            'channel_title': snippet.get('channelTitle', ''),
            'published_at': snippet.get('publishedAt', ''),
            'category_id': int(snippet.get('categoryId', 0)),
            'tags': snippet.get('tags', []),
            'default_language': snippet.get('defaultLanguage', ''),
            'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
        }
        
        # Statistics
        metadata.update({
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
        })
        
        # Content details
        duration_iso = content_details.get('duration', 'PT0S')
        metadata['duration_seconds'] = parse_iso_duration(duration_iso)
        metadata['definition'] = content_details.get('definition', 'sd')
        metadata['caption'] = content_details.get('caption', 'false')
        
        # Status
        metadata['privacy_status'] = status.get('privacyStatus', 'public')
        metadata['upload_status'] = status.get('uploadStatus', 'processed')
        
        # Derived fields
        metadata['published_at_local'] = convert_to_local_time(metadata['published_at'])
        metadata['title_length'] = len(metadata['title'])
        metadata['description_length'] = len(metadata['description'])
        metadata['tag_count'] = len(metadata['tags'])
        
        # Engagement metrics
        if metadata['view_count'] > 0:
            metadata['like_ratio'] = metadata['like_count'] / metadata['view_count']
            metadata['comment_ratio'] = metadata['comment_count'] / metadata['view_count']
            metadata['engagement_ratio'] = (metadata['like_count'] + metadata['comment_count']) / metadata['view_count']
        else:
            metadata['like_ratio'] = 0
            metadata['comment_ratio'] = 0
            metadata['engagement_ratio'] = 0
        
        return metadata
        
    except Exception as e:
        logger.error(f"Failed to extract video metadata: {e}")
        return {}

def extract_channel_metadata(channel_data: Dict) -> Dict:
    """Extract and normalize channel metadata from API response"""
    try:
        snippet = channel_data.get('snippet', {})
        statistics = channel_data.get('statistics', {})
        content_details = channel_data.get('contentDetails', {})
        
        metadata = {
            'channel_id': channel_data.get('id', ''),
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'custom_url': snippet.get('customUrl', ''),
            'published_at': snippet.get('publishedAt', ''),
            'country': snippet.get('country', ''),
            'default_language': snippet.get('defaultLanguage', ''),
            'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
            
            # Statistics
            'subscriber_count': int(statistics.get('subscriberCount', 0)),
            'video_count': int(statistics.get('videoCount', 0)),
            'view_count': int(statistics.get('viewCount', 0)),
            
            # Content details
            'uploads_playlist_id': content_details.get('relatedPlaylists', {}).get('uploads', ''),
        }
        
        # Derived fields
        metadata['published_at_local'] = convert_to_local_time(metadata['published_at'])
        metadata['avg_views_per_video'] = metadata['view_count'] / max(metadata['video_count'], 1)
        
        return metadata
        
    except Exception as e:
        logger.error(f"Failed to extract channel metadata: {e}")
        return {}

# File I/O Helper Functions
def save_to_csv(data: List[Dict], filepath: str, append: bool = False):
    """Save data to CSV file"""
    try:
        df = pd.DataFrame(data)
        mode = 'a' if append else 'w'
        header = not append
        
        df.to_csv(filepath, mode=mode, header=header, index=False, encoding='utf-8')
        logger.info(f"Saved {len(data)} records to {filepath}")
        
    except Exception as e:
        logger.error(f"Failed to save data to {filepath}: {e}")
        raise

def save_to_json(data: Union[Dict, List], filepath: str):
    """Save data to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Saved data to {filepath}")
        
    except Exception as e:
        logger.error(f"Failed to save data to {filepath}: {e}")
        raise

def load_from_csv(filepath: str) -> pd.DataFrame:
    """Load data from CSV file"""
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
        logger.info(f"Loaded {len(df)} records from {filepath}")
        return df
        
    except Exception as e:
        logger.error(f"Failed to load data from {filepath}: {e}")
        return pd.DataFrame()

def load_from_json(filepath: str) -> Union[Dict, List]:
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded data from {filepath}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load data from {filepath}: {e}")
        return {}

# Validation Functions
def validate_video_data(video_data: Dict) -> bool:
    """Validate video data meets minimum requirements"""
    from config import VALIDATION_RULES
    
    required_fields = VALIDATION_RULES['required_fields']
    
    # Check required fields
    for field in required_fields:
        if field not in video_data or not video_data[field]:
            logger.warning(f"Video missing required field: {field}")
            return False
    
    # Check duration limits
    duration = video_data.get('duration_seconds', 0)
    if duration < VALIDATION_RULES['min_video_duration']:
        logger.warning(f"Video too short: {duration}s")
        return False
    
    if duration > VALIDATION_RULES['max_video_duration']:
        logger.warning(f"Video too long: {duration}s")
        return False
    
    # Check view count
    view_count = video_data.get('view_count', 0)
    if view_count < VALIDATION_RULES['min_view_count']:
        logger.warning(f"Video has insufficient views: {view_count}")
        return False
    
    return True

def clean_text(text: str) -> str:
    """Clean and normalize text data"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove non-printable characters
    text = ''.join(char for char in text if char.isprintable() or char.isspace())
    
    return text

def get_time_features(timestamp: datetime) -> Dict:
    """Extract time-based features from timestamp"""
    return {
        'year': timestamp.year,
        'month': timestamp.month,
        'day': timestamp.day,
        'hour': timestamp.hour,
        'day_of_week': timestamp.weekday(),
        'day_of_year': timestamp.timetuple().tm_yday,
        'week_of_year': timestamp.isocalendar()[1],
        'is_weekend': timestamp.weekday() >= 5,
        'quarter': (timestamp.month - 1) // 3 + 1
    }

# Export main functions
__all__ = [
    'YouTubeAPIClient',
    'setup_logging',
    'get_channel_info',
    'get_channel_videos',
    'get_video_details',
    'parse_iso_duration',
    'convert_to_local_time',
    'extract_video_metadata',
    'extract_channel_metadata',
    'save_to_csv',
    'save_to_json',
    'load_from_csv',
    'load_from_json',
    'validate_video_data',
    'clean_text',
    'get_time_features'
]
