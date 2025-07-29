# YouTube Viewership Data Collection System for Sri Lankan Audience Forecasting

A comprehensive data collection and analysis system for YouTube videos targeting Sri Lankan audiences, designed to enable predictive modeling of video performance and trend analysis.

## 🎯 Project Overview

This system automates the collection of YouTube metadata from channels popular among Sri Lankan viewers, tracks video performance over time, and processes the data for machine learning applications. The goal is to build a high-quality dataset that can predict video viewership based on metadata, early engagement metrics, and channel characteristics.

## 🏗️ System Architecture

```
youtube-forecasting-project/
│
├── 📁 data/                          # Data storage layer
│   ├── raw/                          # Raw API responses
│   │   ├── videos_YYYYMMDD_HHMMSS.csv
│   │   ├── channels_YYYYMMDD_HHMMSS.csv
│   │   ├── detailed_channels/        # Channel discovery results
│   │   └── expanded_keywords/        # Keyword expansion data
│   ├── processed/                    # Feature-engineered data
│   │   ├── processed_videos_YYYYMMDD_HHMMSS.csv
│   │   └── feature_stats_YYYYMMDD_HHMMSS.json
│   ├── snapshots/                    # Performance tracking
│   │   └── snapshot_YYYY-MM-DD.csv
│   └── logs/                         # System logs
│       ├── youtube_collector.log
│       └── failed_*.json
│
├── 📁 scripts/                       # Core application logic
│   ├── config.py                     # System configuration
│   ├── utils.py                      # Shared utilities
│   ├── collect_channels.py           # Channel discovery
│   ├── collect_channels_unlimited.py # Advanced discovery
│   ├── collect_videos.py             # Video data collection
│   ├── track_performance.py          # Performance monitoring
│   ├── process_data.py               # Data processing pipeline
│   ├── scheduler.py                  # Task automation
│   └── quota_check.py                # API quota monitoring
│
├── 📁 models/                        # ML models and analysis
│   └── exploratory_analysis.ipynb    # Data exploration
│
├── 📁 dashboard/                     # Visualization (planned)
│
├── 📁 reports/                       # Generated reports
│
├── 📁 docs/                          # Comprehensive documentation
│   ├── SYSTEM_ARCHITECTURE.md       # Technical architecture guide
│   ├── FEATURE_ENGINEERING_GUIDE.md # 50+ features documentation
│   ├── AUTOMATION_GUIDE.md          # Production deployment guide
│   ├── API_KEY_ROTATION_FIX.md      # API management details
│   ├── API_QUOTA_MANAGEMENT.md      # Quota optimization guide
│   └── CHANNEL_DISCOVERY_GUIDE.md   # Advanced discovery system
│
├── 📄 requirements.txt               # Python packages
├── 📄 README.md                      # This file
├── 📄 .env.template                  # Environment variables template
└── 📄 .gitignore                     # Git ignore rules
```

> 📖 **For detailed technical documentation, see [docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)**

## 🚀 Quick Start

### 30-Second Setup

```bash
# Clone and setup
git clone https://github.com/L0rd008/youtube-forecasting-project.git
cd youtube-forecasting-project
pip install -r requirements.txt

# Configure API keys (supports multiple keys for higher quotas)
cp .env.template .env
# Edit .env file with your YouTube API key(s)

# Test the system
python scripts/collect_videos.py --max-videos 20
python scripts/process_data.py
streamlit run dashboard/app.py
```

### Get YouTube API Keys
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Create API key credentials
4. Add to `.env` file (supports multiple keys: `YOUTUBE_API_KEY`, `YOUTUBE_API_KEY_1`, `YOUTUBE_API_KEY_2`, etc.)

> 🔧 **Need help?** Check the [troubleshooting section](#-troubleshooting) below.

## 📊 Core Functionality

The system provides three main operations:

1. **Data Collection**: Automated video metadata collection from Sri Lankan YouTube channels
2. **Performance Tracking**: Monitor view/like/comment growth over time  
3. **Data Processing**: Feature engineering and ML-ready dataset creation

### Basic Commands
```bash
# Discover new Sri Lankan channels (Enhanced Discovery)
python scripts/collect_channels.py --expand-keywords --max-results 500

# Collect recent videos
python scripts/collect_videos.py --max-videos 50

# Track performance changes
python scripts/track_performance.py

# Process and engineer 50+ features
python scripts/process_data.py

# Run automated scheduler
python scripts/scheduler.py --daemon
```

### Advanced Discovery Commands
```bash
# Intelligent keyword expansion (20 → 500+ keywords)
python scripts/collect_channels.py --expand-keywords --max-results 1000

# Location-based comprehensive discovery
python scripts/collect_channels.py --location-search --max-results 500

# Validate existing channels
python scripts/collect_channels.py --validate-existing

# Check API quota status
python scripts/quota_check.py
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

The system features advanced API quota management with multiple key support:
- **Multiple API Key Support**: Use multiple keys for higher daily quotas (10,000 units per key)
- **Automatic Key Rotation**: Seamlessly switches between keys when quotas are exceeded
- **Quota Reset Detection**: Automatically recovers keys when quotas reset (midnight Pacific Time)
- **Rate Limiting**: Intelligent rate limiting between requests
- **Retry Logic**: Exponential backoff with automatic failover
- **Usage Tracking**: Real-time quota usage monitoring and reporting

> 📖 **For detailed API key setup and rotation information, see [docs/API_KEY_ROTATION_FIX.md](docs/API_KEY_ROTATION_FIX.md)**

## 📈 Features

### 🚀 Advanced Channel Discovery
- **Intelligent Keyword Expansion**: 20 base keywords → 500+ validated keywords
- **Multi-Strategy Discovery**: Keyword-based, location-based, trending content
- **Sri Lankan Relevance Scoring**: Geographic and cultural indicators
- **Automatic Categorization**: Maps channels to content categories
- **Unlimited Scalability**: Discover 1000+ channels across all categories

### 🔄 Automated Data Collection
- **Multi-API Key Support**: Automatic rotation for higher quotas (30,000+ units/day)
- **Robust Error Handling**: Exponential backoff with automatic failover
- **Performance Tracking**: Time-series snapshots with growth metrics
- **Scheduled Automation**: Production-ready task scheduling
- **Real-time Monitoring**: Comprehensive logging and health checks

### 🔬 Advanced Feature Engineering
- **50+ ML-Ready Features**: Comprehensive feature pipeline
- **Text Analysis**: Sentiment analysis, keyword detection, complexity metrics
- **Time-Based Features**: Publication timing, seasonal patterns, age metrics
- **Performance Features**: Growth rates, consistency scores, trend indicators
- **Channel Features**: Size categories, performance metrics, metadata

### 🎯 Target Variables & Analytics
- **Multi-Tier Classification**: 5-tier viewership categories
- **Binary Classification**: Viral vs non-viral prediction
- **Engagement Analysis**: 3-tier engagement level classification
- **Success Scoring**: Composite metrics combining views and engagement
- **Growth Prediction**: Time-series forecasting capabilities

### 🤖 Production Automation
- **Task Scheduler**: Automated daily/weekly/monthly operations
- **Health Monitoring**: System status checks and alerts
- **Error Recovery**: Automatic recovery from common failures
- **Cross-Platform**: Windows, Linux, Mac, Docker, Cloud deployment
- **Scalable Architecture**: Supports enterprise-level deployments

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

### Built-in Task Scheduler

The system includes a comprehensive automation framework:

```bash
# Start automated scheduler (recommended)
python scripts/scheduler.py --daemon

# View scheduled tasks
python scripts/scheduler.py --show-schedule

# Run specific job immediately
python scripts/scheduler.py --run-job collect_videos
```

### Default Schedule
- **Daily (02:00)**: Video collection from all channels
- **Daily (03:00)**: Data processing and feature engineering
- **Every 6 hours**: Performance tracking and growth metrics
- **Weekly (Sunday 01:00)**: Channel discovery and expansion
- **Weekly (Sunday 04:00)**: System health checks and validation
- **Monthly**: Cleanup old logs and optimize storage

### Production Deployment Options

**Windows Task Scheduler**
```bash
# Create automated startup task
schtasks /create /tn "YouTube Scheduler" /tr "python C:\path\to\scripts\scheduler.py --daemon" /sc onstart /ru SYSTEM
```

**Linux/Mac Systemd Service**
```bash
# Install as system service
sudo cp deployment/youtube-scheduler.service /etc/systemd/system/
sudo systemctl enable youtube-scheduler
sudo systemctl start youtube-scheduler
```

**Docker Deployment**
```bash
# Run in container
docker-compose up -d youtube-scheduler
```

> 📖 **For complete deployment guide, see [docs/AUTOMATION_GUIDE.md](docs/AUTOMATION_GUIDE.md)**

## 📊 Usage Examples

### Complete Data Pipeline

```python
from scripts.collect_channels import ChannelDiscoverer
from scripts.collect_videos import VideoCollector
from scripts.track_performance import PerformanceTracker
from scripts.process_data import DataProcessor

# 1. Discover new channels (Enhanced Discovery)
discoverer = ChannelDiscoverer()
channels = discoverer.discover_channels_unlimited(max_results=1000)
discoverer.save_discovered_channels()

# 2. Collect video data
collector = VideoCollector()
videos = collector.collect_all_videos(max_videos_per_channel=100)
collector.save_data()

# 3. Track performance over time
tracker = PerformanceTracker()
snapshots = tracker.track_video_performance(video_ids)
tracker.save_snapshots()

# 4. Process and engineer 50+ features
processor = DataProcessor()
processed_data = processor.process_all_data()
processor.save_processed_data()
```

### Advanced Analytics

```python
import pandas as pd
import numpy as np
from scripts.utils import load_from_csv

# Load processed data with 50+ features
df = pd.read_csv('data/processed/processed_videos.csv')

# Advanced feature analysis
feature_importance = df.corr()['viewership_category'].abs().sort_values(ascending=False)

# Time-series analysis
growth_analysis = df.groupby(['channel_category', 'publish_time_category']).agg({
    'view_growth_24h': ['mean', 'std'],
    'engagement_ratio': ['mean', 'median'],
    'success_score': ['mean', 'std']
})

# Predictive modeling preparation
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Select features for modeling
feature_cols = [col for col in df.columns if col not in ['video_id', 'title', 'description']]
X = df[feature_cols].select_dtypes(include=[np.number])
y = df['viewership_category']

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
```

### Channel Discovery Analysis

```python
# Analyze discovered channels
channels_df = pd.read_csv('data/raw/detailed_channels_latest.csv')

# Sri Lankan relevance scoring analysis
relevance_analysis = channels_df.groupby('category').agg({
    'sri_lankan_score': ['mean', 'std', 'count'],
    'subscriber_count': ['mean', 'median'],
    'video_count': ['mean', 'median']
})

# Keyword expansion effectiveness
keywords_data = pd.read_json('data/raw/expanded_keywords_latest.json')
expansion_ratio = len(keywords_data['validated_keywords']) / len(keywords_data['base_keywords'])
print(f"Keyword expansion ratio: {expansion_ratio:.1f}x")
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

**API Quota Exceeded (All Keys)**
```
Error: All API keys exhausted
```
- System automatically rotates through all available API keys
- Wait for quota reset (daily at midnight Pacific Time)
- Add more API keys: `YOUTUBE_API_KEY_1`, `YOUTUBE_API_KEY_2`, etc.
- Check quota status: `python scripts/quota_check.py`

**Channel Discovery Issues**
```
Warning: No channels found with current keywords
```
- Try keyword expansion: `python scripts/collect_channels.py --expand-keywords`
- Use location-based search: `python scripts/collect_channels.py --location-search`
- Check API key permissions and quota availability

**Windows Unicode Issues**
```
UnicodeEncodeError: 'charmap' codec can't encode character
```
- System automatically detects and handles Unicode support
- Uses safe ASCII alternatives on incompatible consoles
- All file outputs use UTF-8 encoding

**Scheduler Not Running**
```
Error: Scheduler stopped unexpectedly
```
- Check system logs: `tail -f data/logs/youtube_collector.log`
- Restart scheduler: `python scripts/scheduler.py --daemon`
- Verify system resources and permissions

**Data Processing Failures**
```
Error: Failed to process data
```
- Check raw data availability: `ls data/raw/videos_*.csv`
- Skip sentiment analysis: `python scripts/process_data.py --no-sentiment`
- Process in smaller batches or increase memory allocation

### Performance Optimization

**For Large-Scale Operations**:
- Use multiple API keys (up to 5 recommended)
- Enable batch processing: `--max-results 1000`
- Schedule during off-peak hours
- Monitor disk space and memory usage

**For Development/Testing**:
- Use smaller datasets: `--max-videos 20`
- Skip advanced features: `--no-sentiment`
- Test individual components before full pipeline

### System Health Monitoring

```bash
# Check system status
python scripts/health_check.py

# Monitor real-time logs
tail -f data/logs/youtube_collector.log

# Check API quota usage
python scripts/quota_check.py --status

# Validate data integrity
python scripts/process_data.py --validate-only
```

> 📖 **For comprehensive troubleshooting, see [docs/AUTOMATION_GUIDE.md#error-handling--recovery](docs/AUTOMATION_GUIDE.md#error-handling--recovery)**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Documentation

### Complete Documentation Suite

- **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)**: Technical architecture and component overview
- **[Feature Engineering Guide](docs/FEATURE_ENGINEERING_GUIDE.md)**: Complete documentation of 50+ features
- **[Automation Guide](docs/AUTOMATION_GUIDE.md)**: Production deployment and scheduling
- **[API Key Management](docs/API_KEY_ROTATION_FIX.md)**: Multi-key rotation system details
- **[Quota Management](docs/API_QUOTA_MANAGEMENT.md)**: API optimization strategies
- **[Channel Discovery](docs/CHANNEL_DISCOVERY_GUIDE.md)**: Advanced discovery system guide

### Quick Reference

| Task | Command | Documentation |
|------|---------|---------------|
| **Channel Discovery** | `python scripts/collect_channels.py --expand-keywords` | [Channel Discovery Guide](docs/CHANNEL_DISCOVERY_GUIDE.md) |
| **Video Collection** | `python scripts/collect_videos.py --max-videos 100` | [System Architecture](docs/SYSTEM_ARCHITECTURE.md) |
| **Feature Engineering** | `python scripts/process_data.py` | [Feature Engineering Guide](docs/FEATURE_ENGINEERING_GUIDE.md) |
| **Automation** | `python scripts/scheduler.py --daemon` | [Automation Guide](docs/AUTOMATION_GUIDE.md) |
| **API Management** | `python scripts/quota_check.py` | [API Quota Management](docs/API_QUOTA_MANAGEMENT.md) |

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- YouTube Data API v3 for providing access to video metadata
- Sri Lankan YouTube community for creating diverse content
- Open source libraries that make this project possible
- Contributors to the advanced channel discovery and automation systems

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the comprehensive documentation in `docs/`
- Review troubleshooting guides
- Monitor system logs in `data/logs/`

---

**Note**: This system is designed for research and educational purposes. Please respect YouTube's Terms of Service and API usage policies. The system includes built-in rate limiting and quota management to ensure responsible API usage.
