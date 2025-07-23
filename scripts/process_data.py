"""
Data Processing Script for YouTube Data Collection System
Cleans raw data and engineers features for machine learning models
"""

import os
import sys
import argparse
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from textblob import TextBlob
from tqdm import tqdm

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    DATA_RAW_PATH,
    DATA_PROCESSED_PATH,
    DATA_SNAPSHOTS_PATH,
    FEATURE_PARAMS,
    VIDEO_CATEGORIES,
    SENTIMENT_ANALYSIS_ENABLED,
    ADVANCED_FEATURES_ENABLED,
    TIMEZONE
)

from utils import (
    load_from_csv,
    save_to_csv,
    clean_text,
    get_time_features,
    convert_to_local_time,
    setup_logging
)

logger = setup_logging()

class DataProcessor:
    """Main class for processing and feature engineering YouTube data"""
    
    def __init__(self):
        """Initialize the data processor"""
        self.raw_videos = pd.DataFrame()
        self.raw_channels = pd.DataFrame()
        self.snapshots = pd.DataFrame()
        self.processed_data = pd.DataFrame()
        self.feature_stats = {}
    
    def load_raw_data(self, data_dir: str = DATA_RAW_PATH) -> bool:
        """Load raw data from CSV files"""
        logger.info("Loading raw data files...")
        
        try:
            # Load video data
            video_files = [f for f in os.listdir(data_dir) 
                          if f.startswith('videos_') and f.endswith('.csv')]
            
            if video_files:
                # Load the most recent video file
                latest_video_file = max(video_files)
                video_path = os.path.join(data_dir, latest_video_file)
                self.raw_videos = load_from_csv(video_path)
                logger.info(f"Loaded {len(self.raw_videos)} videos from {latest_video_file}")
            else:
                logger.warning("No video data files found")
                return False
            
            # Load channel data
            channel_files = [f for f in os.listdir(data_dir) 
                           if f.startswith('channels_') and f.endswith('.csv')]
            
            if channel_files:
                latest_channel_file = max(channel_files)
                channel_path = os.path.join(data_dir, latest_channel_file)
                self.raw_channels = load_from_csv(channel_path)
                logger.info(f"Loaded {len(self.raw_channels)} channels from {latest_channel_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load raw data: {e}")
            return False
    
    def load_snapshot_data(self, snapshots_dir: str = DATA_SNAPSHOTS_PATH) -> bool:
        """Load performance snapshot data"""
        logger.info("Loading snapshot data...")
        
        try:
            snapshot_files = [f for f in os.listdir(snapshots_dir) 
                            if f.startswith('snapshot_') and f.endswith('.csv')]
            
            if not snapshot_files:
                logger.warning("No snapshot files found")
                return False
            
            # Load all snapshot files and combine
            all_snapshots = []
            for file in snapshot_files:
                file_path = os.path.join(snapshots_dir, file)
                df = load_from_csv(file_path)
                if not df.empty:
                    all_snapshots.append(df)
            
            if all_snapshots:
                self.snapshots = pd.concat(all_snapshots, ignore_index=True)
                logger.info(f"Loaded {len(self.snapshots)} snapshot records from {len(all_snapshots)} files")
                return True
            
        except Exception as e:
            logger.error(f"Failed to load snapshot data: {e}")
        
        return False
    
    def clean_video_data(self) -> pd.DataFrame:
        """Clean and normalize video data"""
        logger.info("Cleaning video data...")
        
        df = self.raw_videos.copy()
        initial_count = len(df)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['video_id'])
        logger.info(f"Removed {initial_count - len(df)} duplicate videos")
        
        # Clean text fields
        text_fields = ['title', 'description', 'channel_title']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].fillna('').apply(clean_text)
        
        # Handle missing values
        numeric_fields = ['view_count', 'like_count', 'comment_count', 'duration_seconds']
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
        
        # Convert timestamps
        if 'published_at' in df.columns:
            df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
        
        # Filter out invalid data
        valid_mask = (
            (df['duration_seconds'] >= FEATURE_PARAMS.get('min_video_duration', 10)) &
            (df['duration_seconds'] <= FEATURE_PARAMS.get('max_video_duration', 14400)) &
            (df['view_count'] >= 0) &
            (df['title'].str.len() > 0)
        )
        
        df = df[valid_mask]
        logger.info(f"Filtered to {len(df)} valid videos")
        
        return df
    
    def engineer_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer basic features from video metadata"""
        logger.info("Engineering basic features...")
        
        # Title and description features
        df['title_length'] = df['title'].str.len()
        df['title_word_count'] = df['title'].str.split().str.len()
        df['description_length'] = df['description'].str.len()
        df['description_word_count'] = df['description'].str.split().str.len()
        
        # Tag features
        if 'tags' in df.columns:
            df['tag_count'] = df['tags'].apply(lambda x: len(eval(x)) if isinstance(x, str) and x.startswith('[') else 0)
        else:
            df['tag_count'] = 0
        
        # Duration features
        df['duration_minutes'] = df['duration_seconds'] / 60
        df['duration_category'] = pd.cut(df['duration_seconds'], 
                                       bins=[0, 60, 300, 600, 1800, float('inf')],
                                       labels=['very_short', 'short', 'medium', 'long', 'very_long'])
        
        # Engagement features
        df['like_ratio'] = df['like_count'] / (df['view_count'] + 1)
        df['comment_ratio'] = df['comment_count'] / (df['view_count'] + 1)
        df['engagement_ratio'] = (df['like_count'] + df['comment_count']) / (df['view_count'] + 1)
        
        # Category features
        df['category_name'] = df['category_id'].map(VIDEO_CATEGORIES).fillna('Unknown')
        
        # Channel features (if channel data is available)
        if not self.raw_channels.empty:
            channel_features = self.raw_channels[['channel_id', 'subscriber_count', 'video_count', 'avg_views_per_video']].copy()
            df = df.merge(channel_features, on='channel_id', how='left')
            
            # Channel size categories
            df['channel_size'] = pd.cut(df['subscriber_count'].fillna(0),
                                      bins=[0, 1000, 10000, 100000, 1000000, float('inf')],
                                      labels=['micro', 'small', 'medium', 'large', 'mega'])
        
        return df
    
    def engineer_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer time-based features"""
        logger.info("Engineering time features...")
        
        if 'published_at' not in df.columns:
            logger.warning("No published_at column found, skipping time features")
            return df
        
        # Convert to local timezone
        df['published_at_local'] = df['published_at'].apply(
            lambda x: convert_to_local_time(x.isoformat()) if pd.notna(x) else None
        )
        
        # Extract time features
        time_features_list = []
        for idx, row in df.iterrows():
            if pd.notna(row['published_at_local']):
                time_features = get_time_features(row['published_at_local'])
                time_features_list.append(time_features)
            else:
                time_features_list.append({key: None for key in ['year', 'month', 'day', 'hour', 'day_of_week', 'is_weekend']})
        
        time_df = pd.DataFrame(time_features_list)
        df = pd.concat([df, time_df], axis=1)
        
        # Time-based categories
        df['publish_time_category'] = pd.cut(df['hour'].fillna(12),
                                           bins=[0, 6, 12, 18, 24],
                                           labels=['night', 'morning', 'afternoon', 'evening'],
                                           include_lowest=True)
        
        # Days since publication
        current_time = datetime.now()
        # Make current_time timezone-aware to match published_at
        if df['published_at'].dt.tz is not None:
            import pytz
            current_time = current_time.replace(tzinfo=pytz.UTC)
        
        df['days_since_published'] = (current_time - df['published_at']).dt.days
        df['weeks_since_published'] = df['days_since_published'] / 7
        
        return df
    
    def engineer_text_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer text-based features including sentiment analysis"""
        logger.info("Engineering text features...")
        
        if not SENTIMENT_ANALYSIS_ENABLED:
            logger.info("Sentiment analysis disabled, skipping text features")
            return df
        
        # Sentiment analysis for titles
        logger.info("Analyzing title sentiment...")
        title_sentiments = []
        for title in tqdm(df['title'], desc="Processing titles"):
            try:
                blob = TextBlob(title)
                sentiment = {
                    'title_sentiment_polarity': blob.sentiment.polarity,
                    'title_sentiment_subjectivity': blob.sentiment.subjectivity
                }
            except:
                sentiment = {
                    'title_sentiment_polarity': 0.0,
                    'title_sentiment_subjectivity': 0.0
                }
            title_sentiments.append(sentiment)
        
        sentiment_df = pd.DataFrame(title_sentiments)
        df = pd.concat([df, sentiment_df], axis=1)
        
        # Text complexity features
        df['title_exclamation_count'] = df['title'].str.count('!')
        df['title_question_count'] = df['title'].str.count('\?')
        df['title_caps_ratio'] = df['title'].apply(lambda x: sum(1 for c in x if c.isupper()) / max(len(x), 1))
        
        # Keyword features (common YouTube keywords)
        youtube_keywords = ['tutorial', 'review', 'unboxing', 'vlog', 'challenge', 'reaction', 'how to', 'tips', 'tricks']
        for keyword in youtube_keywords:
            df[f'title_has_{keyword.replace(" ", "_")}'] = df['title'].str.lower().str.contains(keyword, na=False)
        
        return df
    
    def engineer_performance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer performance-based features using snapshot data"""
        logger.info("Engineering performance features...")
        
        if self.snapshots.empty:
            logger.warning("No snapshot data available, skipping performance features")
            return df
        
        # Calculate growth metrics from snapshots
        growth_features = []
        
        for video_id in tqdm(df['video_id'], desc="Processing performance data"):
            video_snapshots = self.snapshots[self.snapshots['video_id'] == video_id]
            
            if len(video_snapshots) < 2:
                # Not enough data for growth calculation
                growth_features.append({
                    'view_growth_rate': 0,
                    'like_growth_rate': 0,
                    'comment_growth_rate': 0,
                    'peak_daily_views': 0,
                    'consistency_score': 0
                })
                continue
            
            # Sort by date
            video_snapshots = video_snapshots.sort_values('snapshot_date')
            
            # Calculate growth rates
            first_snapshot = video_snapshots.iloc[0]
            last_snapshot = video_snapshots.iloc[-1]
            
            days_diff = max((pd.to_datetime(last_snapshot['snapshot_date']) - 
                           pd.to_datetime(first_snapshot['snapshot_date'])).days, 1)
            
            view_growth_rate = (last_snapshot['view_count'] - first_snapshot['view_count']) / days_diff
            like_growth_rate = (last_snapshot['like_count'] - first_snapshot['like_count']) / days_diff
            comment_growth_rate = (last_snapshot['comment_count'] - first_snapshot['comment_count']) / days_diff
            
            # Peak daily views (if daily growth data available)
            peak_daily_views = 0
            if 'view_growth_24h' in video_snapshots.columns:
                peak_daily_views = video_snapshots['view_growth_24h'].max()
            
            # Consistency score (coefficient of variation of daily growth)
            consistency_score = 0
            if 'view_growth_24h' in video_snapshots.columns and len(video_snapshots) > 2:
                daily_growth = video_snapshots['view_growth_24h']
                if daily_growth.std() > 0:
                    consistency_score = daily_growth.mean() / daily_growth.std()
            
            growth_features.append({
                'view_growth_rate': view_growth_rate,
                'like_growth_rate': like_growth_rate,
                'comment_growth_rate': comment_growth_rate,
                'peak_daily_views': peak_daily_views,
                'consistency_score': consistency_score
            })
        
        growth_df = pd.DataFrame(growth_features)
        df = pd.concat([df, growth_df], axis=1)
        
        return df
    
    def create_target_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create target variables for machine learning"""
        logger.info("Creating target variables...")
        
        # Viewership categories based on percentiles
        view_percentiles = df['view_count'].quantile([0.25, 0.5, 0.75, 0.9])
        
        def categorize_viewership(views):
            if views <= view_percentiles[0.25]:
                return 'low'
            elif views <= view_percentiles[0.5]:
                return 'medium_low'
            elif views <= view_percentiles[0.75]:
                return 'medium_high'
            elif views <= view_percentiles[0.9]:
                return 'high'
            else:
                return 'viral'
        
        df['viewership_category'] = df['view_count'].apply(categorize_viewership)
        
        # Binary viral classification
        viral_threshold = FEATURE_PARAMS.get('viral_view_threshold', 100000)
        df['is_viral'] = (df['view_count'] >= viral_threshold).astype(int)
        
        # Engagement level
        engagement_percentiles = df['engagement_ratio'].quantile([0.33, 0.67])
        df['engagement_level'] = pd.cut(df['engagement_ratio'],
                                      bins=[0, engagement_percentiles[0.33], engagement_percentiles[0.67], float('inf')],
                                      labels=['low', 'medium', 'high'])
        
        # Success score (composite metric)
        # Normalize metrics to 0-1 scale
        df['view_score'] = (df['view_count'] - df['view_count'].min()) / (df['view_count'].max() - df['view_count'].min())
        df['engagement_score'] = (df['engagement_ratio'] - df['engagement_ratio'].min()) / (df['engagement_ratio'].max() - df['engagement_ratio'].min())
        
        # Weighted success score
        df['success_score'] = 0.7 * df['view_score'] + 0.3 * df['engagement_score']
        
        return df
    
    def calculate_feature_statistics(self, df: pd.DataFrame):
        """Calculate and store feature statistics"""
        logger.info("Calculating feature statistics...")
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        self.feature_stats = {
            'total_videos': len(df),
            'date_range': {
                'start': df['published_at'].min().isoformat() if 'published_at' in df.columns else None,
                'end': df['published_at'].max().isoformat() if 'published_at' in df.columns else None
            },
            'numeric_features': {}
        }
        
        for col in numeric_columns:
            self.feature_stats['numeric_features'][col] = {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'median': float(df[col].median()),
                'missing_count': int(df[col].isna().sum())
            }
        
        # Category distributions
        categorical_columns = ['viewership_category', 'engagement_level', 'category_name', 'channel_category']
        self.feature_stats['categorical_features'] = {}
        
        for col in categorical_columns:
            if col in df.columns:
                self.feature_stats['categorical_features'][col] = df[col].value_counts().to_dict()
    
    def process_all_data(self, include_snapshots: bool = True) -> pd.DataFrame:
        """Process all data with full feature engineering pipeline"""
        logger.info("Starting full data processing pipeline...")
        
        # Load data
        if not self.load_raw_data():
            raise ValueError("Failed to load raw data")
        
        if include_snapshots:
            self.load_snapshot_data()
        
        # Clean data
        df = self.clean_video_data()
        
        # Feature engineering
        df = self.engineer_basic_features(df)
        df = self.engineer_time_features(df)
        
        if SENTIMENT_ANALYSIS_ENABLED:
            df = self.engineer_text_features(df)
        
        if include_snapshots and not self.snapshots.empty:
            df = self.engineer_performance_features(df)
        
        # Create targets
        df = self.create_target_variables(df)
        
        # Calculate statistics
        self.calculate_feature_statistics(df)
        
        self.processed_data = df
        logger.info(f"Processing completed. Final dataset: {len(df)} videos with {len(df.columns)} features")
        
        return df
    
    def save_processed_data(self, output_dir: str = DATA_PROCESSED_PATH, timestamp: bool = True):
        """Save processed data and feature statistics"""
        os.makedirs(output_dir, exist_ok=True)
        
        if self.processed_data.empty:
            logger.warning("No processed data to save")
            return
        
        # Generate timestamp for filenames
        ts = datetime.now().strftime("%Y%m%d_%H%M%S") if timestamp else ""
        
        # Save processed dataset
        filename = f"processed_videos_{ts}.csv" if ts else "processed_videos.csv"
        filepath = os.path.join(output_dir, filename)
        save_to_csv(self.processed_data.to_dict('records'), filepath)
        
        # Save feature statistics
        stats_filename = f"feature_stats_{ts}.json" if ts else "feature_stats.json"
        stats_filepath = os.path.join(output_dir, stats_filename)
        
        import json
        with open(stats_filepath, 'w') as f:
            json.dump(self.feature_stats, f, indent=2, default=str)
        
        logger.info(f"Saved processed data to {filepath}")
        logger.info(f"Saved feature statistics to {stats_filepath}")

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Process YouTube data and engineer features')
    
    parser.add_argument('--input-dir', type=str, default=DATA_RAW_PATH,
                       help='Input directory with raw data files')
    parser.add_argument('--output-dir', type=str, default=DATA_PROCESSED_PATH,
                       help='Output directory for processed data')
    parser.add_argument('--no-snapshots', action='store_true',
                       help='Skip loading snapshot data for performance features')
    parser.add_argument('--no-sentiment', action='store_true',
                       help='Skip sentiment analysis')
    parser.add_argument('--no-timestamp', action='store_true',
                       help='Do not add timestamp to output filenames')
    
    args = parser.parse_args()
    
    try:
        # Override config settings if specified
        if args.no_sentiment:
            import config
            config.SENTIMENT_ANALYSIS_ENABLED = False
        
        # Initialize processor
        processor = DataProcessor()
        
        # Process data
        processed_df = processor.process_all_data(include_snapshots=not args.no_snapshots)
        
        # Save results
        processor.save_processed_data(args.output_dir, timestamp=not args.no_timestamp)
        
        # Print summary
        logger.info("Processing Summary:")
        logger.info(f"  Total videos processed: {len(processed_df)}")
        logger.info(f"  Total features created: {len(processed_df.columns)}")
        logger.info(f"  Date range: {processor.feature_stats['date_range']['start']} to {processor.feature_stats['date_range']['end']}")
        
        # Feature breakdown
        numeric_features = len(processor.feature_stats['numeric_features'])
        categorical_features = len(processor.feature_stats.get('categorical_features', {}))
        logger.info(f"  Numeric features: {numeric_features}")
        logger.info(f"  Categorical features: {categorical_features}")
        
        logger.info("Data processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
