"""
Configuration file for YouTube Data Collection System
Contains API settings, channel lists, and system parameters
"""

import os
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables
load_dotenv()

# YouTube API Configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'your_youtube_api_key_here')
YOUTUBE_API_BASE_URL = os.getenv('YOUTUBE_API_BASE_URL', 'https://www.googleapis.com/youtube/v3/')
MAX_RESULTS_PER_REQUEST = int(os.getenv('MAX_RESULTS_PER_REQUEST', 50))
DAILY_QUOTA_LIMIT = int(os.getenv('DAILY_QUOTA_LIMIT', 10000))

# Data Collection Settings
DATA_COLLECTION_INTERVAL_HOURS = int(os.getenv('DATA_COLLECTION_INTERVAL_HOURS', 24))
PERFORMANCE_TRACKING_INTERVAL_HOURS = int(os.getenv('PERFORMANCE_TRACKING_INTERVAL_HOURS', 6))
MAX_VIDEOS_PER_CHANNEL = int(os.getenv('MAX_VIDEOS_PER_CHANNEL', 100))

# File Paths
DATA_RAW_PATH = 'data/raw'
DATA_PROCESSED_PATH = 'data/processed'
DATA_SNAPSHOTS_PATH = 'data/snapshots'
DATA_LOGS_PATH = 'data/logs'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'data/logs/youtube_collector.log')

# Timezone
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Colombo')

# Feature Engineering Settings
SENTIMENT_ANALYSIS_ENABLED = os.getenv('SENTIMENT_ANALYSIS_ENABLED', 'true').lower() == 'true'
ADVANCED_FEATURES_ENABLED = os.getenv('ADVANCED_FEATURES_ENABLED', 'true').lower() == 'true'

# Sri Lankan YouTube Channels by Category
SRI_LANKAN_CHANNELS = {
    'news_media': {
        'Ada Derana': 'UCjPRJXoVbOLCtcpYb8foUQw',
        'Hiru News': 'UCDRlK2nf7b6n_GCdhqgdr_w',
        'Sirasa TV': 'UCjQKyJVi_s6sIGWKr6mnhAg',
        'TV Derana': 'UCbkjbWoS8g8pj2rJJbcn2Bg',
        'ITN': 'UCcVdCg6XE2kYdeDVlxz0rPg',
        'Rupavahini': 'UCBVBQp0AjqkGNrjFyNJKbfA',
        'NewsFirst': 'UCrLBfWjp8MlZJNESPaFhtdw',
        'Newswire': 'UCgLKhT-s5c7XnJBXHWGvgmw'
    },
    'entertainment_music': {
        'Wasthi Productions': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Siyatha TV': 'UCjQKyJVi_s6sIGWKr6mnhAg',
        'Charana TV': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Ridma Weerawardena': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Sanuka Wickramasinghe': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Yureni Noshika': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Umaria': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'BnS': 'UCjA5jjMKxjJhJY8WqbZ8wKw'
    },
    'education': {
        'Sinhala Edu': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Learn with Kasun': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Tech Sinhala': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Sinhala Tutorials': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Education Hub LK': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Learn IT Sinhala': 'UCjA5jjMKxjJhJY8WqbZ8wKw'
    },
    'vlogs_lifestyle': {
        'Ape Amma': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Sinhala Vlogs': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Travel with Chatura': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Cooking with Amma': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'SL Food Recipes': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Life in Sri Lanka': 'UCjA5jjMKxjJhJY8WqbZ8wKw'
    },
    'sports': {
        'Sri Lanka Cricket': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'SLC Official': 'UCjA5jjMKxjJhJY8WqbZ8wKw',
        'Sports Hub LK': 'UCjA5jjMKxjJhJY8WqbZ8wKw'
    }
}

# Flatten channel list for easy access
ALL_CHANNEL_IDS = []
for category, channels in SRI_LANKAN_CHANNELS.items():
    ALL_CHANNEL_IDS.extend(channels.values())

# Remove duplicates
ALL_CHANNEL_IDS = list(set(ALL_CHANNEL_IDS))

# YouTube API Endpoints
YOUTUBE_ENDPOINTS = {
    'channels': 'channels',
    'videos': 'videos',
    'search': 'search',
    'playlists': 'playlists',
    'playlistItems': 'playlistItems'
}

# Video Categories (YouTube's predefined categories)
VIDEO_CATEGORIES = {
    1: 'Film & Animation',
    2: 'Autos & Vehicles',
    10: 'Music',
    15: 'Pets & Animals',
    17: 'Sports',
    19: 'Travel & Events',
    20: 'Gaming',
    22: 'People & Blogs',
    23: 'Comedy',
    24: 'Entertainment',
    25: 'News & Politics',
    26: 'Howto & Style',
    27: 'Education',
    28: 'Science & Technology',
    29: 'Nonprofits & Activism'
}

# Data Collection Parameters
COLLECTION_PARAMS = {
    'video_parts': ['snippet', 'statistics', 'contentDetails', 'status'],
    'channel_parts': ['snippet', 'statistics', 'contentDetails'],
    'search_parts': ['snippet'],
    'max_retries': 3,
    'retry_delay': 1,  # seconds
    'rate_limit_delay': 1,  # seconds between requests
}

# Feature Engineering Parameters
FEATURE_PARAMS = {
    'title_max_length': 100,
    'description_max_length': 5000,
    'tags_max_count': 50,
    'engagement_ratio_threshold': 0.05,
    'viral_view_threshold': 100000,
    'trending_hours': 24
}

# Database Configuration
DATABASE_CONFIG = {
    'sqlite_path': 'data/youtube_data.db',
    'tables': {
        'videos': 'videos',
        'channels': 'channels',
        'snapshots': 'performance_snapshots'
    }
}

# Validation Rules
VALIDATION_RULES = {
    'min_video_duration': 10,  # seconds
    'max_video_duration': 14400,  # 4 hours in seconds
    'min_view_count': 0,
    'required_fields': ['video_id', 'title', 'published_at', 'channel_id']
}

def get_channel_ids_by_category(category: str) -> List[str]:
    """Get channel IDs for a specific category"""
    if category in SRI_LANKAN_CHANNELS:
        return list(SRI_LANKAN_CHANNELS[category].values())
    return []

def get_all_categories() -> List[str]:
    """Get all available categories"""
    return list(SRI_LANKAN_CHANNELS.keys())

def validate_api_key() -> bool:
    """Validate if API key is set"""
    return YOUTUBE_API_KEY != 'your_youtube_api_key_here' and len(YOUTUBE_API_KEY) > 10

def get_quota_cost(endpoint: str, parts: List[str]) -> int:
    """Calculate quota cost for API request"""
    base_costs = {
        'channels': 1,
        'videos': 1,
        'search': 100,
        'playlists': 1,
        'playlistItems': 1
    }
    
    part_costs = {
        'snippet': 2,
        'statistics': 2,
        'contentDetails': 2,
        'status': 2,
        'topicDetails': 2
    }
    
    base_cost = base_costs.get(endpoint, 1)
    parts_cost = sum(part_costs.get(part, 0) for part in parts)
    
    return base_cost + parts_cost

# Export main configuration
__all__ = [
    'YOUTUBE_API_KEY',
    'SRI_LANKAN_CHANNELS',
    'ALL_CHANNEL_IDS',
    'COLLECTION_PARAMS',
    'FEATURE_PARAMS',
    'DATABASE_CONFIG',
    'VALIDATION_RULES',
    'get_channel_ids_by_category',
    'get_all_categories',
    'validate_api_key',
    'get_quota_cost'
]
