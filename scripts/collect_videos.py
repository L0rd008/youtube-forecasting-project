"""
Video Collection Script for YouTube Data Collection System
Collects video metadata and statistics from Sri Lankan YouTube channels
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from tqdm import tqdm

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    SRI_LANKAN_CHANNELS,
    ALL_CHANNEL_IDS,
    MAX_VIDEOS_PER_CHANNEL,
    DATA_RAW_PATH,
    get_channel_ids_by_category,
    get_all_categories,
    validate_api_key
)

from utils import (
    YouTubeAPIClient,
    get_channel_info,
    get_channel_videos,
    get_video_details,
    extract_video_metadata,
    extract_channel_metadata,
    save_to_csv,
    save_to_json,
    validate_video_data,
    setup_logging
)

logger = setup_logging()

class VideoCollector:
    """Main class for collecting video data from YouTube channels"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the video collector"""
        self.client = YouTubeAPIClient(api_key) if api_key else YouTubeAPIClient()
        self.collected_videos = []
        self.collected_channels = []
        self.failed_channels = []
        
        # Validate API key
        if not validate_api_key():
            raise ValueError("Invalid or missing YouTube API key. Please check your .env file.")
    
    def collect_channel_data(self, channel_ids: List[str]) -> List[Dict]:
        """Collect metadata for specified channels"""
        logger.info(f"Collecting data for {len(channel_ids)} channels...")
        
        try:
            channel_data = get_channel_info(self.client, channel_ids)
            channels_metadata = []
            
            for channel in channel_data:
                metadata = extract_channel_metadata(channel)
                if metadata:
                    channels_metadata.append(metadata)
                    logger.debug(f"Collected channel data: {metadata['title']}")
            
            self.collected_channels.extend(channels_metadata)
            logger.info(f"Successfully collected data for {len(channels_metadata)} channels")
            return channels_metadata
            
        except Exception as e:
            logger.error(f"Failed to collect channel data: {e}")
            return []
    
    def collect_videos_from_channel(self, channel_id: str, max_videos: int = MAX_VIDEOS_PER_CHANNEL) -> List[Dict]:
        """Collect videos from a specific channel"""
        logger.info(f"Collecting videos from channel: {channel_id}")
        
        try:
            # Get video IDs from channel
            video_ids = get_channel_videos(self.client, channel_id, max_videos)
            
            if not video_ids:
                logger.warning(f"No videos found for channel: {channel_id}")
                return []
            
            logger.info(f"Found {len(video_ids)} videos in channel {channel_id}")
            
            # Get detailed video information
            video_data = get_video_details(self.client, video_ids)
            videos_metadata = []
            
            for video in video_data:
                metadata = extract_video_metadata(video)
                if metadata and validate_video_data(metadata):
                    # Add collection timestamp
                    metadata['collected_at'] = datetime.now().isoformat()
                    metadata['collection_date'] = datetime.now().date().isoformat()
                    videos_metadata.append(metadata)
                    logger.debug(f"Collected video: {metadata['title'][:50]}...")
            
            logger.info(f"Successfully collected {len(videos_metadata)} valid videos from channel {channel_id}")
            return videos_metadata
            
        except Exception as e:
            logger.error(f"Failed to collect videos from channel {channel_id}: {e}")
            self.failed_channels.append({
                'channel_id': channel_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return []
    
    def collect_videos_by_category(self, category: str, max_videos_per_channel: int = MAX_VIDEOS_PER_CHANNEL) -> List[Dict]:
        """Collect videos from all channels in a specific category"""
        logger.info(f"Collecting videos from category: {category}")
        
        channel_ids = get_channel_ids_by_category(category)
        if not channel_ids:
            logger.warning(f"No channels found for category: {category}")
            return []
        
        all_videos = []
        
        # First collect channel metadata
        self.collect_channel_data(channel_ids)
        
        # Then collect videos from each channel
        for channel_id in tqdm(channel_ids, desc=f"Processing {category} channels"):
            videos = self.collect_videos_from_channel(channel_id, max_videos_per_channel)
            all_videos.extend(videos)
            
            # Add category information to videos
            for video in videos:
                video['channel_category'] = category
        
        logger.info(f"Collected {len(all_videos)} videos from {category} category")
        return all_videos
    
    def collect_all_videos(self, max_videos_per_channel: int = MAX_VIDEOS_PER_CHANNEL) -> List[Dict]:
        """Collect videos from all configured channels"""
        logger.info("Starting collection from all configured channels...")
        
        all_videos = []
        categories = get_all_categories()
        
        for category in categories:
            logger.info(f"Processing category: {category}")
            videos = self.collect_videos_by_category(category, max_videos_per_channel)
            all_videos.extend(videos)
        
        self.collected_videos = all_videos
        logger.info(f"Total videos collected: {len(all_videos)}")
        
        return all_videos
    
    def collect_recent_videos(self, days_back: int = 7, max_videos_per_channel: int = 50) -> List[Dict]:
        """Collect only recent videos from the last N days"""
        logger.info(f"Collecting videos from the last {days_back} days...")
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        all_videos = self.collect_all_videos(max_videos_per_channel)
        
        # Filter for recent videos
        recent_videos = []
        for video in all_videos:
            try:
                published_date = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                if published_date >= cutoff_date:
                    recent_videos.append(video)
            except Exception as e:
                logger.warning(f"Failed to parse date for video {video.get('video_id', 'unknown')}: {e}")
        
        logger.info(f"Found {len(recent_videos)} videos from the last {days_back} days")
        return recent_videos
    
    def save_data(self, output_dir: str = DATA_RAW_PATH, timestamp: bool = True):
        """Save collected data to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp for filenames
        ts = datetime.now().strftime("%Y%m%d_%H%M%S") if timestamp else ""
        
        # Save videos data
        if self.collected_videos:
            video_filename = f"videos_{ts}.csv" if ts else "videos.csv"
            video_filepath = os.path.join(output_dir, video_filename)
            save_to_csv(self.collected_videos, video_filepath)
            
            # Also save as JSON for backup
            json_filename = f"videos_{ts}.json" if ts else "videos.json"
            json_filepath = os.path.join(output_dir, json_filename)
            save_to_json(self.collected_videos, json_filepath)
            
            logger.info(f"Saved {len(self.collected_videos)} videos to {video_filepath}")
        
        # Save channels data
        if self.collected_channels:
            channel_filename = f"channels_{ts}.csv" if ts else "channels.csv"
            channel_filepath = os.path.join(output_dir, channel_filename)
            save_to_csv(self.collected_channels, channel_filepath)
            
            logger.info(f"Saved {len(self.collected_channels)} channels to {channel_filepath}")
        
        # Save failed channels log
        if self.failed_channels:
            failed_filename = f"failed_channels_{ts}.json" if ts else "failed_channels.json"
            failed_filepath = os.path.join(output_dir, failed_filename)
            save_to_json(self.failed_channels, failed_filepath)
            
            logger.warning(f"Saved {len(self.failed_channels)} failed channels to {failed_filepath}")
    
    def get_collection_summary(self) -> Dict:
        """Get summary of collection results"""
        return {
            'total_videos_collected': len(self.collected_videos),
            'total_channels_processed': len(self.collected_channels),
            'failed_channels': len(self.failed_channels),
            'quota_used': self.client.quota_used,
            'collection_timestamp': datetime.now().isoformat(),
            'categories_processed': len(set(video.get('channel_category', 'unknown') 
                                          for video in self.collected_videos))
        }

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Collect YouTube video data from Sri Lankan channels')
    
    parser.add_argument('--category', type=str, help='Specific category to collect (e.g., news_media)')
    parser.add_argument('--recent', type=int, help='Collect videos from last N days only')
    parser.add_argument('--max-videos', type=int, default=MAX_VIDEOS_PER_CHANNEL,
                       help='Maximum videos per channel')
    parser.add_argument('--output-dir', type=str, default=DATA_RAW_PATH,
                       help='Output directory for data files')
    parser.add_argument('--no-timestamp', action='store_true',
                       help='Do not add timestamp to output filenames')
    parser.add_argument('--api-key', type=str, help='YouTube API key (overrides .env)')
    
    args = parser.parse_args()
    
    try:
        # Initialize collector
        collector = VideoCollector(api_key=args.api_key)
        
        # Collect data based on arguments
        if args.category:
            if args.category not in get_all_categories():
                logger.error(f"Invalid category: {args.category}")
                logger.info(f"Available categories: {', '.join(get_all_categories())}")
                return
            
            videos = collector.collect_videos_by_category(args.category, args.max_videos)
            
        elif args.recent:
            videos = collector.collect_recent_videos(args.recent, args.max_videos)
            
        else:
            videos = collector.collect_all_videos(args.max_videos)
        
        # Save data
        collector.save_data(args.output_dir, timestamp=not args.no_timestamp)
        
        # Print summary
        summary = collector.get_collection_summary()
        logger.info("Collection Summary:")
        for key, value in summary.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("Video collection completed successfully!")
        
    except Exception as e:
        logger.error(f"Collection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
