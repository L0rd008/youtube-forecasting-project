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
        'Ada Derana': 'UCRDDfbYPHX_GUJ4lcQYTc8A',
        'Hiru News': 'UCOtYyt7W5PmPnwQjWWF_Z-Q',
        'NewsFirst': 'UCJpM66ypgqDMT-buL1ALuLA',
        'Newswire': 'UCV-hall6WGCn1NY7dofVJJA'
    },
    'music': {
        'Ridma Weerawardena': 'UCYfYZgkolI8VpiIpL767N7g',
        'Sanuka Wickramasinghe': 'UCPHWwelDVlaWqrT2F8qwmiA',
        'Yureni Noshika': 'UC-mOUuQBUvlB94pjZdjB5ig',
        'Umaria': 'UCWYXLMuL0m10w53wnMaUf3g',
        'BnS': 'UCvivK4AwTrkPBnmrObTFxaQ'
    },
    'entertainment': {
        'Blok & Dino': 'UCTcATaNqlaCF4zkZp29BJRQ',
        'Siyatha TV': 'UCHhk9EHspPZejY9PnR1PLVg',
        'Charana TV': 'UCmNv8608OO9T6pONDTipm0A',
        'Wasthi Productions': 'UCMQYRNX1Fg-HJ8Ey7Z3WPrA',
        'Sirasa TV': 'UCn0XmAUFv6d2tofMFEesSNw',
        'TV Derana': 'UCRDDfbYPHX_GUJ4lcQYTc8A',
        'ITN': 'UCQTcNhAZidy1i9wwmdgf2Lw',
        'Rupavahini': 'UCT83ymyAGm7Gnk_4ifxjxIA',
    },
    'education': {
        'Edu sinhalen': 'UCmzOKlGqbaaxVLzmlQ1xjwA',
        'DP Education 1': 'UCaXHgF7cAdDElEtgG2XSjlw',
        'DP Education 2': 'UC0CXMeU0432EMgBnlBaY_yA',
        'Sinhala Tech': 'UCAhZgaf5PEpnStllKJRhvVg',
        'Sinhala Guitar Lessons': 'UCzPYh2hr7QSSLs7gUX0ofFg',
        'Ruchira Wijesena': 'UCR5y9OV23c0jJ4RGwDvGnLw',
        'Darshana Ukuwela': 'UCSfrW0G4yQy587afT5uCxFQ',
        'Dinesh Muthugala': 'UCUz06yHz7YZWF737tof7rYQ',
        'Raamuwa': 'UCY7Gd6C6q74h11ZAbie8xoQ',
    },
    'vlogs_lifestyle': {
        'Ape Amma': 'UCtAv4S_gDY34sHW4vK0YvVw',
        'Minoli Disanayaka': 'UCPHLNkCri7sfGt4IP2tUYfA',
        'Thilini Nimeshi': 'UC3aHg03ut7j87ACMxy215_Q',
        'Travel with Chatura': 'UCyzPvmM5qpGmAb48SXcikiw',
        'Yash and Hass': 'UCAo_wAxH1WT6rFmK5yCd1Cg',
        'Wild Cookbook': 'UC0jl0-twIcRptNHGnINyk9Q',
        'Saaraa’s Japan Diaries': 'UCIG2lbAXX9hkj8AbjVJlhkg',
        'SharaDh': 'UCZ246KOECqjh9TTPk5Sf86w',
        'Samee and Sandu':'UCDkGNkHKVxQ7PRk5D0migrw',
        'Solo Hiker': 'UCBkyh-TXXmPpTjAXiklLoEA',
        'kavindu karunarathne': 'UC56HPjeRngN3-2LSNlp80yQ',
        'Yohani Hettiarachchi': 'UCULeO4zpJMcG3kQI8iZ9PCw',
        'Man Saranna': 'UCGe9vzavXCSu7GBIgoPebeQ',
        'Dinesh A Pathum': 'UCN2GByhXeLkilxHV45JwA-A',
        'Ginger Family': 'UCh3ZGM0EBlcKSa4ZzUEfAOw',
        'Pawani Perera': 'UCjW1eTO3QBPr1M_Z7UA0crA',
        'Seri saranna': 'UCORaJXeMZxCvf-z4_fdGZlg'
    },
    'sports': {
        'Sri Lanka Cricket': 'UCJA-NQ4MtcRIog66wziD8fA',
        'Football Sri Lanka TV': 'UCl4MonVoWRx3HqAh3Efw2Jg',
        'Sri Lankan Sports TV': 'UCrcATWZGF_p53r38i6VK0eA',
        'Ceylon Sports': 'UCHySsgSdKQ3Ssq7lEN4i2-w'
    }
}

# Flatten channel list for easy access
ALL_CHANNEL_IDS = []
for category, channels in SRI_LANKAN_CHANNELS.items():
    ALL_CHANNEL_IDS.extend(channels.values())

# Remove duplicates
ALL_CHANNEL_IDS = list(set(ALL_CHANNEL_IDS))

# Channel categories (derived from SRI_LANKAN_CHANNELS keys)
CHANNEL_CATEGORIES = list(SRI_LANKAN_CHANNELS.keys())

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
    'CHANNEL_CATEGORIES',
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
