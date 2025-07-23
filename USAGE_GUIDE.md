# YouTube Sri Lankan Content Analysis System - Usage Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Data Collection](#data-collection)
6. [Data Processing](#data-processing)
7. [Analysis & Visualization](#analysis--visualization)
8. [Automation & Scheduling](#automation--scheduling)
9. [Troubleshooting](#troubleshooting)
10. [API Usage & Quotas](#api-usage--quotas)

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/L0rd008/youtube-forecasting-project.git
cd youtube-forecasting-project

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env file with your YouTube API key
```

### 2. Get YouTube API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add the API key to your `.env` file

### 3. Test the System
```bash
# Run integration tests
python scripts/test_integration.py

# Collect sample data
python scripts/collect_videos.py --max-videos 10

# Process the data
python scripts/process_data.py

# Launch dashboard
streamlit run dashboard/app.py
```

## 💻 System Requirements

### Hardware Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 2GB free space for data and dependencies
- **CPU**: Any modern processor (multi-core recommended for large datasets)

### Software Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Internet Connection**: Required for API calls and data collection

### Python Dependencies
All dependencies are listed in `requirements.txt`:
- google-api-python-client
- pandas
- numpy
- streamlit
- plotly
- textblob
- python-dotenv
- tqdm
- schedule

## 🔧 Installation & Setup

### Step 1: Environment Setup
```bash
# Create virtual environment (recommended)
python -m venv youtube_env
source youtube_env/bin/activate  # On Windows: youtube_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: API Configuration
1. **Get YouTube Data API v3 Key**:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create/select project
   - Enable YouTube Data API v3
   - Create API key credentials

2. **Configure Environment**:
   ```bash
   cp .env.template .env
   ```
   
   Edit `.env` file:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

### Step 3: Verify Installation
```bash
python scripts/test_integration.py
```

## ⚙️ Configuration

### Main Configuration File: `scripts/config.py`

#### API Settings
```python
# API quotas and limits
MAX_RESULTS_PER_REQUEST = 50
DAILY_QUOTA_LIMIT = 10000
REQUEST_DELAY = 1.0  # seconds between requests
```

#### Channel Configuration
```python
# Add your target Sri Lankan channels
SRI_LANKAN_CHANNELS = {
    'news_media': {
        'CHANNEL_ID_1': 'Channel Name 1',
        'CHANNEL_ID_2': 'Channel Name 2',
    },
    'entertainment_music': {
        # Add entertainment channels
    }
}
```

#### Data Paths
```python
DATA_RAW_PATH = '../data/raw'
DATA_PROCESSED_PATH = '../data/processed'
DATA_SNAPSHOTS_PATH = '../data/snapshots'
```

## 📊 Data Collection

### 1. Basic Video Collection
```bash
# Collect videos from all configured channels
python scripts/collect_videos.py

# Collect with specific parameters
python scripts/collect_videos.py --max-videos 100 --days-back 30
```

### 2. Channel Discovery (Optional)
```bash
# Discover new Sri Lankan channels
python scripts/collect_channels.py --keywords "Sri Lanka news" "Sinhala music"

# Validate existing channels
python scripts/collect_channels.py --validate-existing

# Location-based search
python scripts/collect_channels.py --location-search
```

### 3. Performance Tracking
```bash
# Track video performance over time
python scripts/track_performance.py

# Track specific videos
python scripts/track_performance.py --video-ids VIDEO_ID_1 VIDEO_ID_2
```

### Command Line Options

#### collect_videos.py
- `--max-videos`: Maximum videos per channel (default: 50)
- `--days-back`: Days to look back for videos (default: 30)
- `--categories`: Specific channel categories to collect
- `--output-dir`: Custom output directory

#### collect_channels.py
- `--keywords`: Keywords for channel search
- `--validate-existing`: Validate channels from config
- `--location-search`: Search by location
- `--max-results`: Maximum results per search

#### track_performance.py
- `--video-ids`: Specific video IDs to track
- `--max-age-days`: Maximum age of videos to track
- `--batch-size`: Batch size for API requests

## 🔄 Data Processing

### 1. Basic Processing
```bash
# Process all raw data
python scripts/process_data.py

# Process specific files
python scripts/process_data.py --input-file data/raw/videos_2024-01-01.csv
```

### 2. Feature Engineering
The processing pipeline automatically creates:
- **Basic Features**: title_length, duration_minutes, engagement_ratio
- **Temporal Features**: publish_hour, publish_day_of_week, days_since_published
- **Text Features**: sentiment_score, title_sentiment
- **Performance Features**: viewership_category, growth_metrics

### 3. Data Quality Checks
- Duplicate removal
- Missing value handling
- Outlier detection
- Data validation

## 📈 Analysis & Visualization

### 1. Jupyter Notebook Analysis
```bash
# Launch Jupyter
jupyter notebook models/exploratory_analysis.ipynb
```

The notebook includes:
- Dataset overview and statistics
- Channel category analysis
- Temporal patterns
- Engagement analysis
- Content analysis
- Predictive insights

### 2. Interactive Dashboard
```bash
# Launch Streamlit dashboard
streamlit run dashboard/app.py
```

Dashboard features:
- **Overview Tab**: Dataset metrics and quality
- **Categories Tab**: Channel category analysis
- **Temporal Tab**: Publishing patterns and timing
- **Engagement Tab**: Views, likes, comments analysis
- **Content Tab**: Title and duration analysis
- **Insights Tab**: Correlations and predictions

### 3. Dashboard Filters
- Date range selection
- Channel category filtering
- View count range filtering
- Real-time data updates

## ⏰ Automation & Scheduling

### Windows Task Scheduler

1. **Create Batch Files**:
   ```batch
   @echo off
   cd /d "C:\path\to\youtube-forecasting-project"
   python scripts/collect_videos.py
   ```

2. **Schedule Tasks**:
   - Open Task Scheduler
   - Create Basic Task
   - Set trigger (daily/weekly)
   - Set action to run batch file

### Linux/macOS Cron Jobs

1. **Edit Crontab**:
   ```bash
   crontab -e
   ```

2. **Add Scheduled Tasks**:
   ```bash
   # Daily video collection at 2 AM
   0 2 * * * cd /path/to/project && python scripts/collect_videos.py
   
   # Performance tracking every 6 hours
   0 */6 * * * cd /path/to/project && python scripts/track_performance.py
   
   # Weekly data processing on Sundays at 3 AM
   0 3 * * 0 cd /path/to/project && python scripts/process_data.py
   ```

### Python Scheduler (Alternative)
```python
import schedule
import time

def collect_videos():
    os.system('python scripts/collect_videos.py')

def track_performance():
    os.system('python scripts/track_performance.py')

# Schedule jobs
schedule.every().day.at("02:00").do(collect_videos)
schedule.every(6).hours.do(track_performance)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 🔍 Troubleshooting

### Common Issues

#### 1. API Key Issues
**Problem**: "Invalid API key" error
**Solution**:
- Verify API key in `.env` file
- Check if YouTube Data API v3 is enabled
- Ensure no extra spaces in API key

#### 2. Quota Exceeded
**Problem**: "Quota exceeded" error
**Solution**:
- Wait for quota reset (daily)
- Reduce `MAX_RESULTS_PER_REQUEST` in config
- Implement request delays

#### 3. No Data Collected
**Problem**: Scripts run but no data saved
**Solution**:
- Check channel IDs in config
- Verify channels have recent videos
- Check file permissions in data directories

#### 4. Dashboard Not Loading Data
**Problem**: Dashboard shows "No data available"
**Solution**:
- Run data collection first
- Check processed data files exist
- Verify file paths in dashboard

### Debug Mode
```bash
# Run with debug logging
python scripts/collect_videos.py --debug

# Check log files
tail -f data/logs/youtube_collector.log
```

### Testing Individual Components
```bash
# Test API connection only
python -c "from scripts.utils import YouTubeAPIClient; client = YouTubeAPIClient(); print('API OK')"

# Test data processing only
python -c "from scripts.process_data import DataProcessor; processor = DataProcessor(); print('Processing OK')"
```

## 📊 API Usage & Quotas

### YouTube Data API v3 Quotas
- **Daily Quota**: 10,000 units (default)
- **Search Request**: 100 units
- **Videos Request**: 1 unit
- **Channels Request**: 1 unit

### Quota Management
```python
# Monitor quota usage
from scripts.utils import YouTubeAPIClient
client = YouTubeAPIClient()
print(f"Quota used: {client.quota_used}")
```

### Optimization Tips
1. **Batch Requests**: Use comma-separated IDs
2. **Selective Fields**: Only request needed data parts
3. **Caching**: Store channel info to avoid repeated requests
4. **Rate Limiting**: Add delays between requests

### Cost Estimation
- **50 videos/day**: ~150 quota units
- **Daily tracking**: ~50 quota units
- **Channel validation**: ~10 quota units
- **Total daily usage**: ~210 units (well within limits)

## 📁 File Structure Reference

```
youtube-forecasting-project/
├── data/
│   ├── raw/                    # Raw API responses
│   ├── processed/              # Cleaned and featured data
│   ├── snapshots/              # Performance tracking data
│   └── logs/                   # System logs
├── scripts/
│   ├── config.py              # Configuration settings
│   ├── utils.py               # Utility functions
│   ├── collect_videos.py      # Video data collection
│   ├── collect_channels.py    # Channel discovery
│   ├── track_performance.py   # Performance tracking
│   ├── process_data.py        # Data processing
│   └── test_integration.py    # Integration tests
├── models/
│   └── exploratory_analysis.ipynb  # Analysis notebook
├── dashboard/
│   └── app.py                 # Streamlit dashboard
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── README.md                  # Project overview
```

## 🆘 Support & Resources

### Documentation
- [YouTube Data API v3 Documentation](https://developers.google.com/youtube/v3)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

### Getting Help
1. Check the troubleshooting section
2. Review log files in `data/logs/`
3. Run integration tests
4. Check GitHub issues

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

---

**Last Updated**: July 23, 2025
**Version**: 1.0.0
