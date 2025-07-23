"""
Performance Tracking Script for YouTube Data Collection System
Tracks daily changes in video engagement metrics (views, likes, comments)
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import pandas as pd
from tqdm import tqdm

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    DATA_RAW_PATH,
    DATA_SNAPSHOTS_PATH,
    PERFORMANCE_TRACKING_INTERVAL_HOURS,
    validate_api_key
)

from utils import (
    YouTubeAPIClient,
    get_video_details,
    extract_video_metadata,
    save_to_csv,
    load_from_csv,
    setup_logging
)

logger = setup_logging()

class PerformanceTracker:
    """Main class for tracking video performance over time"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the performance tracker"""
        self.client = YouTubeAPIClient(api_key) if api_key else YouTubeAPIClient()
        self.snapshots = []
        self.failed_videos = []
        
        # Validate API key
        if not validate_api_key():
            raise ValueError("Invalid or missing YouTube API key. Please check your .env file.")
    
    def get_video_ids_from_raw_data(self, days_back: int = 30) -> Set[str]:
        """Get video IDs from raw data files for tracking"""
        video_ids = set()
        
        try:
            # Look for video files in raw data directory
            raw_files = [f for f in os.listdir(DATA_RAW_PATH) if f.startswith('videos_') and f.endswith('.csv')]
            
            if not raw_files:
                logger.warning("No video data files found in raw data directory")
                return video_ids
            
            # Load videos from recent files
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for file in raw_files:
                try:
                    filepath = os.path.join(DATA_RAW_PATH, file)
                    df = load_from_csv(filepath)
                    
                    if 'video_id' in df.columns and 'published_at' in df.columns:
                        # Filter for recent videos
                        df['published_at'] = pd.to_datetime(df['published_at'])
                        recent_videos = df[df['published_at'] >= cutoff_date]
                        video_ids.update(recent_videos['video_id'].tolist())
                        
                        logger.info(f"Found {len(recent_videos)} recent videos in {file}")
                    
                except Exception as e:
                    logger.warning(f"Failed to process file {file}: {e}")
            
            logger.info(f"Total unique video IDs for tracking: {len(video_ids)}")
            return video_ids
            
        except Exception as e:
            logger.error(f"Failed to get video IDs from raw data: {e}")
            return video_ids
    
    def get_video_ids_from_snapshots(self) -> Set[str]:
        """Get video IDs that are already being tracked"""
        video_ids = set()
        
        try:
            # Look for snapshot files
            snapshot_files = [f for f in os.listdir(DATA_SNAPSHOTS_PATH) 
                            if f.startswith('snapshot_') and f.endswith('.csv')]
            
            if not snapshot_files:
                return video_ids
            
            # Get the most recent snapshot file
            latest_file = max(snapshot_files)
            filepath = os.path.join(DATA_SNAPSHOTS_PATH, latest_file)
            
            df = load_from_csv(filepath)
            if 'video_id' in df.columns:
                video_ids.update(df['video_id'].tolist())
                logger.info(f"Found {len(video_ids)} videos in latest snapshot")
            
        except Exception as e:
            logger.warning(f"Failed to get video IDs from snapshots: {e}")
        
        return video_ids
    
    def track_video_performance(self, video_ids: List[str]) -> List[Dict]:
        """Track performance metrics for given video IDs"""
        logger.info(f"Tracking performance for {len(video_ids)} videos...")
        
        snapshots = []
        current_time = datetime.now()
        
        # Process videos in batches to respect API limits
        batch_size = 50
        
        for i in tqdm(range(0, len(video_ids), batch_size), desc="Processing video batches"):
            batch_ids = video_ids[i:i + batch_size]
            
            try:
                # Get current video data
                video_data = get_video_details(self.client, batch_ids)
                
                for video in video_data:
                    metadata = extract_video_metadata(video)
                    
                    if metadata:
                        # Create snapshot record
                        snapshot = {
                            'video_id': metadata['video_id'],
                            'snapshot_date': current_time.date().isoformat(),
                            'snapshot_datetime': current_time.isoformat(),
                            'view_count': metadata['view_count'],
                            'like_count': metadata['like_count'],
                            'comment_count': metadata['comment_count'],
                            'engagement_ratio': metadata['engagement_ratio'],
                            'title': metadata['title'],
                            'channel_id': metadata['channel_id'],
                            'channel_title': metadata['channel_title'],
                            'published_at': metadata['published_at'],
                            'duration_seconds': metadata['duration_seconds'],
                            'category_id': metadata['category_id']
                        }
                        
                        # Calculate days since publication
                        try:
                            pub_date = datetime.fromisoformat(metadata['published_at'].replace('Z', '+00:00'))
                            days_since_pub = (current_time - pub_date.replace(tzinfo=None)).days
                            snapshot['days_since_published'] = days_since_pub
                        except:
                            snapshot['days_since_published'] = None
                        
                        snapshots.append(snapshot)
                        logger.debug(f"Tracked video: {metadata['title'][:50]}...")
                
            except Exception as e:
                logger.error(f"Failed to track batch {i//batch_size + 1}: {e}")
                # Add failed video IDs to failed list
                for video_id in batch_ids:
                    self.failed_videos.append({
                        'video_id': video_id,
                        'error': str(e),
                        'timestamp': current_time.isoformat()
                    })
        
        self.snapshots = snapshots
        logger.info(f"Successfully tracked {len(snapshots)} videos")
        return snapshots
    
    def calculate_growth_metrics(self, video_id: str, current_snapshot: Dict) -> Dict:
        """Calculate growth metrics by comparing with previous snapshots"""
        growth_metrics = {
            'view_growth_24h': 0,
            'like_growth_24h': 0,
            'comment_growth_24h': 0,
            'view_growth_7d': 0,
            'like_growth_7d': 0,
            'comment_growth_7d': 0
        }
        
        try:
            # Look for previous snapshots
            snapshot_files = [f for f in os.listdir(DATA_SNAPSHOTS_PATH) 
                            if f.startswith('snapshot_') and f.endswith('.csv')]
            
            if not snapshot_files:
                return growth_metrics
            
            # Load recent snapshots
            current_date = datetime.now().date()
            date_24h_ago = current_date - timedelta(days=1)
            date_7d_ago = current_date - timedelta(days=7)
            
            snapshot_24h = None
            snapshot_7d = None
            
            for file in sorted(snapshot_files, reverse=True):
                try:
                    filepath = os.path.join(DATA_SNAPSHOTS_PATH, file)
                    df = load_from_csv(filepath)
                    
                    if 'video_id' not in df.columns:
                        continue
                    
                    video_data = df[df['video_id'] == video_id]
                    if video_data.empty:
                        continue
                    
                    # Parse snapshot date from filename or data
                    if 'snapshot_date' in df.columns:
                        snapshot_date = pd.to_datetime(video_data.iloc[0]['snapshot_date']).date()
                    else:
                        # Try to parse from filename
                        date_str = file.replace('snapshot_', '').replace('.csv', '')
                        try:
                            snapshot_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        except:
                            continue
                    
                    # Find closest snapshots to target dates
                    if not snapshot_24h and snapshot_date <= date_24h_ago:
                        snapshot_24h = video_data.iloc[0].to_dict()
                    
                    if not snapshot_7d and snapshot_date <= date_7d_ago:
                        snapshot_7d = video_data.iloc[0].to_dict()
                        break  # We have both snapshots
                    
                except Exception as e:
                    logger.debug(f"Failed to process snapshot file {file}: {e}")
                    continue
            
            # Calculate growth metrics
            current_views = current_snapshot['view_count']
            current_likes = current_snapshot['like_count']
            current_comments = current_snapshot['comment_count']
            
            if snapshot_24h:
                growth_metrics['view_growth_24h'] = current_views - snapshot_24h.get('view_count', 0)
                growth_metrics['like_growth_24h'] = current_likes - snapshot_24h.get('like_count', 0)
                growth_metrics['comment_growth_24h'] = current_comments - snapshot_24h.get('comment_count', 0)
            
            if snapshot_7d:
                growth_metrics['view_growth_7d'] = current_views - snapshot_7d.get('view_count', 0)
                growth_metrics['like_growth_7d'] = current_likes - snapshot_7d.get('like_count', 0)
                growth_metrics['comment_growth_7d'] = current_comments - snapshot_7d.get('comment_count', 0)
            
        except Exception as e:
            logger.warning(f"Failed to calculate growth metrics for video {video_id}: {e}")
        
        return growth_metrics
    
    def save_snapshots(self, output_dir: str = DATA_SNAPSHOTS_PATH, include_growth: bool = True):
        """Save performance snapshots to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        if not self.snapshots:
            logger.warning("No snapshots to save")
            return
        
        # Add growth metrics if requested
        if include_growth:
            logger.info("Calculating growth metrics...")
            for snapshot in tqdm(self.snapshots, desc="Adding growth metrics"):
                growth_metrics = self.calculate_growth_metrics(snapshot['video_id'], snapshot)
                snapshot.update(growth_metrics)
        
        # Generate filename with current date
        current_date = datetime.now().date().isoformat()
        filename = f"snapshot_{current_date}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Save snapshots
        save_to_csv(self.snapshots, filepath)
        logger.info(f"Saved {len(self.snapshots)} snapshots to {filepath}")
        
        # Save failed videos if any
        if self.failed_videos:
            failed_filename = f"failed_tracking_{current_date}.json"
            failed_filepath = os.path.join(output_dir, failed_filename)
            
            import json
            with open(failed_filepath, 'w') as f:
                json.dump(self.failed_videos, f, indent=2)
            
            logger.warning(f"Saved {len(self.failed_videos)} failed videos to {failed_filepath}")
    
    def get_tracking_summary(self) -> Dict:
        """Get summary of tracking results"""
        if not self.snapshots:
            return {'error': 'No snapshots available'}
        
        df = pd.DataFrame(self.snapshots)
        
        summary = {
            'total_videos_tracked': len(self.snapshots),
            'failed_videos': len(self.failed_videos),
            'quota_used': self.client.quota_used,
            'tracking_timestamp': datetime.now().isoformat(),
            'avg_view_count': df['view_count'].mean(),
            'avg_like_count': df['like_count'].mean(),
            'avg_comment_count': df['comment_count'].mean(),
            'avg_engagement_ratio': df['engagement_ratio'].mean(),
            'total_views': df['view_count'].sum(),
            'total_likes': df['like_count'].sum(),
            'total_comments': df['comment_count'].sum()
        }
        
        # Add growth metrics if available
        if 'view_growth_24h' in df.columns:
            summary.update({
                'avg_view_growth_24h': df['view_growth_24h'].mean(),
                'avg_like_growth_24h': df['like_growth_24h'].mean(),
                'avg_comment_growth_24h': df['comment_growth_24h'].mean(),
                'total_view_growth_24h': df['view_growth_24h'].sum(),
                'total_like_growth_24h': df['like_growth_24h'].sum(),
                'total_comment_growth_24h': df['comment_growth_24h'].sum()
            })
        
        return summary

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Track YouTube video performance over time')
    
    parser.add_argument('--days-back', type=int, default=30,
                       help='Track videos published in the last N days')
    parser.add_argument('--video-ids', type=str, nargs='+',
                       help='Specific video IDs to track')
    parser.add_argument('--output-dir', type=str, default=DATA_SNAPSHOTS_PATH,
                       help='Output directory for snapshot files')
    parser.add_argument('--no-growth', action='store_true',
                       help='Skip growth metrics calculation')
    parser.add_argument('--api-key', type=str, help='YouTube API key (overrides .env)')
    
    args = parser.parse_args()
    
    try:
        # Initialize tracker
        tracker = PerformanceTracker(api_key=args.api_key)
        
        # Get video IDs to track
        if args.video_ids:
            video_ids = args.video_ids
            logger.info(f"Tracking {len(video_ids)} specified videos")
        else:
            # Get video IDs from raw data
            video_ids_set = tracker.get_video_ids_from_raw_data(args.days_back)
            
            # Also include videos from previous snapshots
            existing_ids = tracker.get_video_ids_from_snapshots()
            video_ids_set.update(existing_ids)
            
            video_ids = list(video_ids_set)
            logger.info(f"Tracking {len(video_ids)} videos from data files")
        
        if not video_ids:
            logger.error("No video IDs found to track")
            return
        
        # Track performance
        snapshots = tracker.track_video_performance(video_ids)
        
        # Save snapshots
        tracker.save_snapshots(args.output_dir, include_growth=not args.no_growth)
        
        # Print summary
        summary = tracker.get_tracking_summary()
        logger.info("Tracking Summary:")
        for key, value in summary.items():
            if isinstance(value, float):
                logger.info(f"  {key}: {value:.2f}")
            else:
                logger.info(f"  {key}: {value}")
        
        logger.info("Performance tracking completed successfully!")
        
    except Exception as e:
        logger.error(f"Tracking failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
