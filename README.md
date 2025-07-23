# YouTube Viewership Data Collection System for Sri Lankan Audience Forecasting

A comprehensive data collection and analysis system for YouTube videos targeting Sri Lankan audiences, designed to enable predictive modeling of video performance and trend analysis.

## 🎯 Project Overview

This system automates the collection of YouTube metadata from channels popular among Sri Lankan viewers, tracks video performance over time, and processes the data for machine learning applications. The goal is to build a high-quality dataset that can predict video viewership based on metadata, early engagement metrics, and channel characteristics.

## 🏗️ System Architecture

```
youtube-forecasting-project/
│
├── 📁 data/
│   ├── raw/                       # Unprocessed raw JSON/CSV from API
│   ├── processed/                 # Cleaned and feature-engineered data
│   ├── snapshots/                 # Time-based view/like tracking snapshots
│   └── logs/                      # Logs for data collection runs and errors
│
├── 📁 scripts/
│   ├── config.py                  # API keys, constants, parameters
│   ├── collect_videos.py         # Gets video metadata and stats per channel
│   ├── track_performance.py      # Daily/periodic engagement updates
│   ├── process_data.py           # Preprocessing, cleaning, feature engineering
│   └── utils.py                  # Common functions (e.g., ISO parser, API wrappers)
│
├── 📁 models/                     # Future ML models and notebooks
├── 📁 dashboard/                  # Future Streamlit/Flask visualization app
├── 📁 reports/                    # Analysis reports and documentation
│
├── 📄 requirements.txt           # Python packages
├── 📄 README.md                  # This file
├── 📄 .env.template              # Environment variables template
└── 📄 .gitignore                 # Git ignore rules
```

## 🚀 Quick Start

> 📖 **For detailed installation and usage instructions, see [USAGE_GUIDE.md](USAGE_GUIDE.md)**

### 30-Second Setup

```bash
# Clone and setup
git clone https://github.com/L0rd008/youtube-forecasting-project.git
cd youtube-forecasting-project
pip install -r requirements.txt

# Configure API key
cp .env.template .env
# Edit .env file with your YouTube API key

# Test the system
python scripts/collect_videos.py --max-videos 20
python scripts/process_data.py
streamlit run dashboard/app.py
```

### Get YouTube API Key
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Create API key credentials
4. Add to `.env` file

> 🔧 **Need help?** Check the [troubleshooting section](USAGE_GUIDE.md#troubleshooting) in the usage guide.

## 📊 Core Functionality

The system provides three main operations:

1. **Data Collection**: Automated video metadata collection from Sri Lankan YouTube channels
2. **Performance Tracking**: Monitor view/like/comment growth over time  
3. **Data Processing**: Feature engineering and ML-ready dataset creation

> 📖 **For detailed command options and usage examples, see [USAGE_GUIDE.md](USAGE_GUIDE.md#data-collection)**

### Basic Commands
```bash
# Collect recent videos
python scripts/collect_videos.py --max-videos 25

# Track performance changes
python scripts/track_performance.py

# Process and engineer features
python scripts/process_data.py
```

## 🔧 Configuration

### Channel Configuration

The system comes pre-configured with Sri Lankan YouTube channels across multiple categories:

- **News & Media**: Ada Derana, Hiru News, Sirasa TV, TV Derana, ITN, etc.
- **Entertainment & Music**: Wasthi Productions, Siyatha TV, etc.
- **Education**: Tech Sinhala, Learn IT Sinhala, etc.
- **Vlogs & Lifestyle**: Travel vlogs, cooking channels, etc.
- **Sports**: Sri Lanka Cricket, Sports Hub LK, etc.

You can modify the channel list in `scripts/config.py`.

### API Quota Management

The system automatically manages YouTube API quotas:
- Default daily limit: 10,000 units
- Automatic rate limiting between requests
- Retry logic with exponential backoff
- Quota usage tracking and reporting

## 📈 Features

### Data Collection Features

- **Automated Video Collection**: Bulk collection from multiple channels
- **Performance Tracking**: Daily snapshots of view/like/comment counts
- **Growth Metrics**: Calculate 24h and 7-day growth rates
- **Error Handling**: Robust error handling and failed request logging
- **Rate Limiting**: Respects API quotas and rate limits

### Data Processing Features

- **Data Cleaning**: Remove duplicates, handle missing values, validate data
- **Feature Engineering**: 50+ features including:
  - Basic metadata (title length, duration, tags)
  - Time-based features (publish hour, day of week, seasonality)
  - Engagement metrics (like ratio, comment ratio, engagement ratio)
  - Text features (sentiment analysis, keyword detection)
  - Channel features (subscriber count, channel size category)
  - Performance features (growth rates, consistency scores)

### Target Variables

- **Viewership Categories**: Low, Medium-Low, Medium-High, High, Viral
- **Binary Classification**: Viral vs Non-viral
- **Engagement Levels**: Low, Medium, High engagement
- **Success Score**: Composite metric combining views and engagement

## 📋 Dataset Schema

### Video Metadata
- `video_id`, `title`, `description`, `published_at`
- `category_id`, `tags`, `duration_seconds`, `thumbnail_url`
- `channel_id`, `channel_title`, `channel_category`

### Engagement Metrics
- `view_count`, `like_count`, `comment_count`
- `like_ratio`, `comment_ratio`, `engagement_ratio`

### Engineered Features
- `title_length`, `title_word_count`, `title_sentiment_polarity`
- `duration_minutes`, `duration_category`
- `publish_hour`, `day_of_week`, `is_weekend`
- `days_since_published`, `weeks_since_published`
- `view_growth_rate`, `peak_daily_views`, `consistency_score`

### Target Variables
- `viewership_category`, `is_viral`, `engagement_level`
- `success_score`, `view_score`, `engagement_score`

## 🔄 Automation

### Scheduled Data Collection

Set up automated data collection using system schedulers:

**Windows (Task Scheduler)**
```bash
# Daily video collection
schtasks /create /tn "YouTube Data Collection" /tr "python C:\path\to\scripts\collect_videos.py --recent 1" /sc daily /st 09:00

# Hourly performance tracking
schtasks /create /tn "YouTube Performance Tracking" /tr "python C:\path\to\scripts\track_performance.py" /sc hourly
```

**Linux/Mac (Cron)**
```bash
# Edit crontab
crontab -e

# Add these lines:
# Daily video collection at 9 AM
0 9 * * * /path/to/venv/bin/python /path/to/scripts/collect_videos.py --recent 1

# Performance tracking every 6 hours
0 */6 * * * /path/to/venv/bin/python /path/to/scripts/track_performance.py
```

## 📊 Usage Examples

### Basic Data Collection Workflow

```python
from scripts.collect_videos import VideoCollector
from scripts.track_performance import PerformanceTracker
from scripts.process_data import DataProcessor

# 1. Collect video data
collector = VideoCollector()
videos = collector.collect_recent_videos(days_back=7)
collector.save_data()

# 2. Track performance
tracker = PerformanceTracker()
snapshots = tracker.track_video_performance(video_ids)
tracker.save_snapshots()

# 3. Process and engineer features
processor = DataProcessor()
processed_data = processor.process_all_data()
processor.save_processed_data()
```

### Custom Analysis

```python
import pandas as pd
from scripts.utils import load_from_csv

# Load processed data
df = load_from_csv('data/processed/processed_videos.csv')

# Analyze by category
category_stats = df.groupby('channel_category').agg({
    'view_count': ['mean', 'median', 'std'],
    'engagement_ratio': ['mean', 'median'],
    'is_viral': 'sum'
})

# Time-based analysis
hourly_performance = df.groupby('hour')['view_count'].mean()
weekend_vs_weekday = df.groupby('is_weekend')['engagement_ratio'].mean()
```

## 🔍 Monitoring and Logging

### Log Files
- `data/logs/youtube_collector.log`: Main application logs
- `data/logs/failed_*.json`: Failed API requests and errors

### Monitoring Metrics
- API quota usage
- Collection success rates
- Data quality metrics
- Processing pipeline performance

## 🚨 Troubleshooting

### Common Issues

**API Quota Exceeded**
```
Error: API quota exceeded. Please try again tomorrow.
```
- Wait for quota reset (daily at midnight Pacific Time)
- Reduce collection frequency
- Optimize API calls

**Missing API Key**
```
Error: Invalid or missing YouTube API key
```
- Check `.env` file exists and contains valid API key
- Verify API key has YouTube Data API v3 enabled

**No Data Files Found**
```
Warning: No video data files found in raw data directory
```
- Run `collect_videos.py` first to collect initial data
- Check file permissions in data directories

### Performance Optimization

- Use `--max-videos` parameter to limit collection size
- Skip sentiment analysis with `--no-sentiment` for faster processing
- Process data in smaller batches for large datasets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- YouTube Data API v3 for providing access to video metadata
- Sri Lankan YouTube community for creating diverse content
- Open source libraries that make this project possible

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs in `data/logs/`

---

**Note**: This system is designed for research and educational purposes. Please respect YouTube's Terms of Service and API usage policies.
