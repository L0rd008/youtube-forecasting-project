"""
Channel Discovery Script for YouTube Data Collection System
Discovers and validates Sri Lankan YouTube channels using various methods
"""

import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Set
import pandas as pd
from tqdm import tqdm

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    DATA_RAW_PATH,
    SRI_LANKAN_CHANNELS,
    CHANNEL_CATEGORIES,
    validate_api_key
)

from utils import (
    YouTubeAPIClient,
    save_to_csv,
    load_from_csv,
    setup_logging
)

logger = setup_logging()

class ChannelDiscovery:
    """Main class for discovering and validating YouTube channels"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the channel discovery system"""
        self.client = YouTubeAPIClient(api_key) if api_key else YouTubeAPIClient()
        self.discovered_channels = []
        self.validated_channels = []
        self.failed_channels = []
        
        # Validate API key
        if not validate_api_key():
            raise ValueError("Invalid or missing YouTube API key. Please check your .env file.")
    
    def search_channels_by_keywords(self, keywords: List[str], region_code: str = 'LK', 
                                  max_results: int = 50) -> List[Dict]:
        """Search for channels using keywords and region filtering"""
        logger.info(f"Searching for channels with keywords: {keywords}")
        
        discovered = []
        
        for keyword in tqdm(keywords, desc="Processing keywords"):
            try:
                # Search for channels
                search_response = self.client.service.search().list(
                    part='snippet',
                    q=keyword,
                    type='channel',
                    regionCode=region_code,
                    relevanceLanguage='en',
                    maxResults=min(max_results, 50),
                    order='relevance'
                ).execute()
                
                for item in search_response.get('items', []):
                    channel_info = {
                        'channel_id': item['id']['channelId'],
                        'channel_title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'discovery_keyword': keyword,
                        'discovery_method': 'keyword_search',
                        'discovered_at': datetime.now().isoformat()
                    }
                    discovered.append(channel_info)
                
                logger.info(f"Found {len(search_response.get('items', []))} channels for keyword: {keyword}")
                
            except Exception as e:
                logger.error(f"Failed to search for keyword '{keyword}': {e}")
                continue
        
        # Remove duplicates based on channel_id
        unique_channels = {}
        for channel in discovered:
            channel_id = channel['channel_id']
            if channel_id not in unique_channels:
                unique_channels[channel_id] = channel
        
        discovered = list(unique_channels.values())
        logger.info(f"Discovered {len(discovered)} unique channels")
        
        self.discovered_channels.extend(discovered)
        return discovered
    
    def search_channels_by_location(self, location: str = 'Sri Lanka', 
                                  max_results: int = 50) -> List[Dict]:
        """Search for channels by location"""
        logger.info(f"Searching for channels in location: {location}")
        
        try:
            # Search for channels with location-based queries
            location_queries = [
                f"{location} news",
                f"{location} entertainment",
                f"{location} music",
                f"{location} vlog",
                f"{location} cooking",
                f"{location} travel"
            ]
            
            return self.search_channels_by_keywords(location_queries, max_results=max_results//len(location_queries))
            
        except Exception as e:
            logger.error(f"Failed to search by location '{location}': {e}")
            return []
    
    def validate_existing_channels(self, channel_ids: List[str]) -> List[Dict]:
        """Validate existing channel IDs and get their current information"""
        logger.info(f"Validating {len(channel_ids)} existing channels")
        
        validated = []
        batch_size = 50
        
        for i in tqdm(range(0, len(channel_ids), batch_size), desc="Validating channels"):
            batch_ids = channel_ids[i:i + batch_size]
            
            try:
                # Get channel details
                channels_response = self.client.service.channels().list(
                    part='snippet,statistics,brandingSettings',
                    id=','.join(batch_ids)
                ).execute()
                
                for item in channels_response.get('items', []):
                    channel_info = {
                        'channel_id': item['id'],
                        'channel_title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'subscriber_count': int(item['statistics'].get('subscriberCount', 0)),
                        'video_count': int(item['statistics'].get('videoCount', 0)),
                        'view_count': int(item['statistics'].get('viewCount', 0)),
                        'published_at': item['snippet']['publishedAt'],
                        'country': item['snippet'].get('country', ''),
                        'custom_url': item['snippet'].get('customUrl', ''),
                        'discovery_method': 'validation',
                        'validated_at': datetime.now().isoformat()
                    }
                    
                    # Add branding information if available
                    if 'brandingSettings' in item:
                        branding = item['brandingSettings']
                        if 'channel' in branding:
                            channel_info.update({
                                'keywords': branding['channel'].get('keywords', ''),
                                'default_language': branding['channel'].get('defaultLanguage', ''),
                                'country_branding': branding['channel'].get('country', '')
                            })
                    
                    validated.append(channel_info)
                
                logger.debug(f"Validated batch {i//batch_size + 1}: {len(channels_response.get('items', []))} channels")
                
            except Exception as e:
                logger.error(f"Failed to validate batch {i//batch_size + 1}: {e}")
                # Add failed channel IDs to failed list
                for channel_id in batch_ids:
                    self.failed_channels.append({
                        'channel_id': channel_id,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        logger.info(f"Successfully validated {len(validated)} channels")
        self.validated_channels.extend(validated)
        return validated
    
    def categorize_channels(self, channels: List[Dict]) -> List[Dict]:
        """Categorize channels based on their content and keywords"""
        logger.info("Categorizing channels...")
        
        # Category keywords for classification
        category_keywords = {
            'news_media': ['news', 'media', 'current', 'politics', 'breaking', 'report', 'journalist'],
            'entertainment_music': ['music', 'song', 'entertainment', 'movie', 'film', 'drama', 'comedy', 'dance'],
            'education': ['education', 'learn', 'tutorial', 'teach', 'school', 'university', 'study', 'knowledge'],
            'vlogs_lifestyle': ['vlog', 'lifestyle', 'daily', 'life', 'personal', 'family', 'travel', 'food'],
            'sports': ['sport', 'cricket', 'football', 'game', 'match', 'player', 'team', 'fitness'],
            'technology': ['tech', 'technology', 'computer', 'mobile', 'software', 'review', 'gadget'],
            'cooking_food': ['cooking', 'recipe', 'food', 'kitchen', 'chef', 'meal', 'dish'],
            'business': ['business', 'entrepreneur', 'finance', 'money', 'investment', 'startup']
        }
        
        for channel in tqdm(channels, desc="Categorizing channels"):
            # Combine title, description, and keywords for analysis
            text_content = ' '.join([
                channel.get('channel_title', '').lower(),
                channel.get('description', '').lower(),
                channel.get('keywords', '').lower()
            ])
            
            # Score each category
            category_scores = {}
            for category, keywords in category_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_content)
                if score > 0:
                    category_scores[category] = score
            
            # Assign category with highest score
            if category_scores:
                best_category = max(category_scores, key=category_scores.get)
                channel['channel_category'] = best_category
                channel['category_confidence'] = category_scores[best_category]
            else:
                channel['channel_category'] = 'other'
                channel['category_confidence'] = 0
        
        return channels
    
    def filter_sri_lankan_channels(self, channels: List[Dict]) -> List[Dict]:
        """Filter channels that are likely Sri Lankan"""
        logger.info("Filtering for Sri Lankan channels...")
        
        sri_lankan_indicators = [
            'sri lanka', 'srilanka', 'lk', 'colombo', 'kandy', 'galle', 'jaffna',
            'sinhala', 'tamil', 'sinhalese', 'ceylon', 'lanka'
        ]
        
        filtered_channels = []
        
        for channel in tqdm(channels, desc="Filtering channels"):
            # Check various fields for Sri Lankan indicators
            text_fields = [
                channel.get('channel_title', '').lower(),
                channel.get('description', '').lower(),
                channel.get('keywords', '').lower(),
                channel.get('country', '').lower(),
                channel.get('country_branding', '').lower()
            ]
            
            text_content = ' '.join(text_fields)
            
            # Calculate Sri Lankan relevance score
            relevance_score = sum(1 for indicator in sri_lankan_indicators 
                                if indicator in text_content)
            
            # Additional checks
            if channel.get('country') == 'LK':
                relevance_score += 5
            
            if relevance_score > 0:
                channel['sri_lankan_relevance'] = relevance_score
                filtered_channels.append(channel)
        
        logger.info(f"Filtered to {len(filtered_channels)} potentially Sri Lankan channels")
        return filtered_channels
    
    def get_channel_statistics(self, channels: List[Dict]) -> List[Dict]:
        """Get detailed statistics for channels"""
        logger.info("Getting detailed channel statistics...")
        
        channel_ids = [ch['channel_id'] for ch in channels]
        detailed_channels = self.validate_existing_channels(channel_ids)
        
        # Merge with existing channel data
        channel_dict = {ch['channel_id']: ch for ch in channels}
        
        for detailed_ch in detailed_channels:
            channel_id = detailed_ch['channel_id']
            if channel_id in channel_dict:
                # Merge the data
                channel_dict[channel_id].update(detailed_ch)
        
        return list(channel_dict.values())
    
    def save_discovered_channels(self, output_dir: str = DATA_RAW_PATH, 
                               include_validation: bool = True):
        """Save discovered channels to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        if not self.discovered_channels and not self.validated_channels:
            logger.warning("No channels to save")
            return
        
        # Combine discovered and validated channels
        all_channels = self.discovered_channels.copy()
        if include_validation:
            all_channels.extend(self.validated_channels)
        
        # Remove duplicates
        unique_channels = {}
        for channel in all_channels:
            channel_id = channel['channel_id']
            if channel_id not in unique_channels:
                unique_channels[channel_id] = channel
            else:
                # Merge data, preferring more complete records
                existing = unique_channels[channel_id]
                for key, value in channel.items():
                    if key not in existing or not existing[key]:
                        existing[key] = value
        
        final_channels = list(unique_channels.values())
        
        # Categorize and filter
        final_channels = self.categorize_channels(final_channels)
        final_channels = self.filter_sri_lankan_channels(final_channels)
        
        # Generate filename with current date
        current_date = datetime.now().date().isoformat()
        filename = f"discovered_channels_{current_date}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Save channels
        save_to_csv(final_channels, filepath)
        logger.info(f"Saved {len(final_channels)} channels to {filepath}")
        
        # Save failed channels if any
        if self.failed_channels:
            failed_filename = f"failed_channels_{current_date}.json"
            failed_filepath = os.path.join(output_dir, failed_filename)
            
            import json
            with open(failed_filepath, 'w') as f:
                json.dump(self.failed_channels, f, indent=2)
            
            logger.warning(f"Saved {len(self.failed_channels)} failed channels to {failed_filepath}")
    
    def get_discovery_summary(self) -> Dict:
        """Get summary of discovery results"""
        all_channels = self.discovered_channels + self.validated_channels
        
        if not all_channels:
            return {'error': 'No channels discovered'}
        
        # Remove duplicates for summary
        unique_channels = {}
        for channel in all_channels:
            channel_id = channel['channel_id']
            if channel_id not in unique_channels:
                unique_channels[channel_id] = channel
        
        channels_df = pd.DataFrame(list(unique_channels.values()))
        
        summary = {
            'total_discovered': len(unique_channels),
            'failed_channels': len(self.failed_channels),
            'quota_used': self.client.quota_used,
            'discovery_timestamp': datetime.now().isoformat()
        }
        
        # Category breakdown
        if 'channel_category' in channels_df.columns:
            category_counts = channels_df['channel_category'].value_counts().to_dict()
            summary['categories'] = category_counts
        
        # Statistics
        if 'subscriber_count' in channels_df.columns:
            summary.update({
                'avg_subscribers': channels_df['subscriber_count'].mean(),
                'total_subscribers': channels_df['subscriber_count'].sum(),
                'avg_videos': channels_df['video_count'].mean() if 'video_count' in channels_df.columns else 0
            })
        
        return summary

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Discover and validate YouTube channels')
    
    parser.add_argument('--keywords', type=str, nargs='+',
                       help='Keywords to search for channels')
    parser.add_argument('--validate-existing', action='store_true',
                       help='Validate existing channels from config')
    parser.add_argument('--location-search', action='store_true',
                       help='Search by location (Sri Lanka)')
    parser.add_argument('--max-results', type=int, default=100,
                       help='Maximum results per search')
    parser.add_argument('--output-dir', type=str, default=DATA_RAW_PATH,
                       help='Output directory for discovered channels')
    parser.add_argument('--api-key', type=str, help='YouTube API key (overrides .env)')
    
    args = parser.parse_args()
    
    try:
        # Initialize discovery system
        discovery = ChannelDiscovery(api_key=args.api_key)
        
        # Validate existing channels if requested
        if args.validate_existing:
            logger.info("Validating existing channels from config...")
            existing_channel_ids = []
            for category_channels in SRI_LANKAN_CHANNELS.values():
                existing_channel_ids.extend(category_channels.keys())
            
            discovery.validate_existing_channels(existing_channel_ids)
        
        # Search by keywords if provided
        if args.keywords:
            discovery.search_channels_by_keywords(args.keywords, max_results=args.max_results)
        
        # Search by location if requested
        if args.location_search:
            discovery.search_channels_by_location(max_results=args.max_results)
        
        # If no specific search requested, do a comprehensive search
        if not any([args.keywords, args.validate_existing, args.location_search]):
            logger.info("No specific search requested, performing comprehensive discovery...")
            
            # Default keywords for Sri Lankan content
            default_keywords = [
                'Sri Lanka news', 'Sinhala music', 'Tamil songs', 'Sri Lankan cooking',
                'Colombo vlog', 'Sri Lanka travel', 'Lankan entertainment',
                'Sinhala comedy', 'Sri Lanka cricket', 'Ceylon tea'
            ]
            
            discovery.search_channels_by_keywords(default_keywords, max_results=args.max_results//len(default_keywords))
            discovery.validate_existing_channels(list(SRI_LANKAN_CHANNELS.get('news_media', {}).keys())[:10])
        
        # Save results
        discovery.save_discovered_channels(args.output_dir)
        
        # Print summary
        summary = discovery.get_discovery_summary()
        logger.info("Discovery Summary:")
        for key, value in summary.items():
            if isinstance(value, dict):
                logger.info(f"  {key}:")
                for sub_key, sub_value in value.items():
                    logger.info(f"    {sub_key}: {sub_value}")
            elif isinstance(value, float):
                logger.info(f"  {key}: {value:.2f}")
            else:
                logger.info(f"  {key}: {value}")
        
        logger.info("Channel discovery completed successfully!")
        
    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
