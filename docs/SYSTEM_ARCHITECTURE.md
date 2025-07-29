# 🏗️ YouTube Forecasting System Architecture

## Overview

The YouTube Forecasting Project is a comprehensive data collection and analysis system designed to predict video performance for Sri Lankan YouTube content. The system follows a modular architecture with clear separation of concerns and robust error handling.

## 🎯 System Components

### Core Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    YouTube Forecasting System                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   Data Sources  │    │  Configuration  │    │   Utilities  │ │
│  │                 │    │                 │    │              │ │
│  │ • YouTube API   │    │ • config.py     │    │ • utils.py   │ │
│  │ • Channel Lists │    │ • .env settings │    │ • API Client │ │
│  │ • Trend Data    │    │ • Parameters    │    │ • Helpers    │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                      │      │
│           └───────────────────────┼──────────────────────┘      │
│                                   │                             │
│  ┌─────────────────────────────────┼─────────────────────────────┐ │
│  │              Data Collection Layer                          │ │
│  │                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │ │
│  │  │ Channel         │  │ Video           │  │ Performance │ │ │
│  │  │ Discovery       │  │ Collection      │  │ Tracking    │ │ │
│  │  │                 │  │                 │  │             │ │ │
│  │  │ • collect_      │  │ • collect_      │  │ • track_    │ │ │
│  │  │   channels.py   │  │   videos.py     │  │   performance│ │ │
│  │  │ • Keyword       │  │ • Metadata      │  │ • Snapshots │ │ │
│  │  │   Expansion     │  │   Extraction    │  │ • Growth    │ │ │
│  │  │ • Multi-API     │  │ • Validation    │  │   Metrics   │ │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                   │                             │
│  ┌─────────────────────────────────┼─────────────────────────────┐ │
│  │                Data Storage Layer                           │ │
│  │                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │ │
│  │  │ Raw Data    │  │ Processed   │  │ Snapshots   │         │ │
│  │  │             │  │ Data        │  │             │         │ │
│  │  │ • JSON/CSV  │  │ • Features  │  │ • Time      │         │ │
│  │  │ • Metadata  │  │ • ML Ready  │  │   Series    │         │ │
│  │  │ • Logs      │  │ • Analytics │  │ • Growth    │         │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘         │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                   │                             │
│  ┌─────────────────────────────────┼─────────────────────────────┐ │
│  │              Processing Layer                               │ │
│  │                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │ │
│  │  │ Data            │  │ Feature         │  │ Analytics   │ │ │
│  │  │ Processing      │  │ Engineering     │  │ & Modeling  │ │ │
│  │  │                 │  │                 │  │             │ │ │
│  │  │ • process_      │  │ • 50+ Features  │  │ • Jupyter   │ │ │
│  │  │   data.py       │  │ • Text Analysis │  │   Notebooks │ │ │
│  │  │ • Cleaning      │  │ • Time Features │  │ • Reports   │ │ │
│  │  │ • Validation    │  │ • Targets       │  │ • Insights  │ │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                   │                             │
│  ┌─────────────────────────────────┼─────────────────────────────┐ │
│  │              Automation Layer                               │ │
│  │                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │ │
│  │  │ Task            │  │ Monitoring      │  │ Error       │ │ │
│  │  │ Scheduler       │  │ & Logging       │  │ Handling    │ │ │
│  │  │                 │  │                 │  │             │ │ │
│  │  │ • scheduler.py  │  │ • Log Files     │  │ • Retry     │ │ │
│  │  │ • Cron Jobs     │  │ • Status        │  │   Logic     │ │ │
│  │  │ • Workflows     │  │ • Alerts        │  │ • Recovery  │ │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Directory Structure

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
└── 📁 docs/                          # Documentation
    ├── API_KEY_ROTATION_FIX.md
    ├── API_QUOTA_MANAGEMENT.md
    ├── CHANNEL_DISCOVERY_GUIDE.md
    └── SYSTEM_ARCHITECTURE.md (this file)
```

## 🔄 Data Flow Architecture

### 1. **Data Collection Flow**

```
YouTube API → Raw Data → Validation → Storage
     ↓
Channel Discovery → Video Collection → Performance Tracking
     ↓
Feature Engineering → ML-Ready Dataset → Analytics
```

### 2. **Processing Pipeline**

```
Raw JSON/CSV → Data Cleaning → Feature Engineering → Target Creation
      ↓              ↓              ↓                    ↓
   Validation    Text Analysis   Time Features      Success Metrics
      ↓              ↓              ↓                    ↓
   Error Logs    Sentiment       Growth Rates       Classification
```

### 3. **Automation Workflow**

```
Scheduler → Task Queue → Script Execution → Result Logging
    ↓           ↓             ↓                ↓
  Cron Jobs   Priority    Error Handling   Status Updates
    ↓           ↓             ↓                ↓
  Monitoring  Retry Logic   Recovery       Notifications
```

## 🔧 Core Components Detail

### Configuration System (`config.py`)

**Purpose**: Centralized configuration management
**Key Features**:
- Environment variable integration
- 60+ pre-configured Sri Lankan channels
- API quota management settings
- Feature engineering parameters
- Validation rules

**Configuration Categories**:
```python
# API Configuration
YOUTUBE_API_KEY, DAILY_QUOTA_LIMIT, MAX_RESULTS_PER_REQUEST

# Channel Configuration  
SRI_LANKAN_CHANNELS = {
    'news_media': {...},
    'music': {...},
    'entertainment': {...},
    'education': {...},
    'vlogs_lifestyle': {...},
    'sports': {...}
}

# Processing Parameters
FEATURE_PARAMS, VALIDATION_RULES, DATABASE_CONFIG
```

### Utilities System (`utils.py`)

**Purpose**: Shared functionality and API management
**Key Components**:

1. **YouTubeAPIClient**: Robust API client with:
   - Rate limiting and retry logic
   - Multi-key rotation support
   - Error handling and logging
   - Quota tracking

2. **Data Processing Helpers**:
   - Metadata extraction functions
   - Time zone conversion utilities
   - Text cleaning and validation
   - File I/O operations

3. **Platform Compatibility**:
   - Windows Unicode support
   - Cross-platform logging
   - Console encoding detection

### Data Collection Layer

#### Channel Discovery (`collect_channels.py`)
- **Multi-strategy discovery**: Keyword-based, location-based, trending
- **Intelligent keyword expansion**: 20 base → 500+ validated keywords
- **Sri Lankan relevance scoring**: Geographic and cultural indicators
- **Automatic categorization**: Maps to YouTube categories

#### Video Collection (`collect_videos.py`)
- **Batch processing**: Efficient API usage
- **Metadata extraction**: 30+ video attributes
- **Data validation**: Quality checks and filtering
- **Category-based collection**: Organized by content type

#### Performance Tracking (`track_performance.py`)
- **Time-series snapshots**: Daily engagement tracking
- **Growth metrics**: 24h and 7-day growth rates
- **Historical comparison**: Trend analysis capabilities
- **Automated monitoring**: Scheduled performance updates

### Data Processing Layer (`process_data.py`)

**Feature Engineering Pipeline**:

1. **Basic Features** (15+ features):
   - Title/description length and word count
   - Duration categories and metrics
   - Tag analysis and counts
   - Engagement ratios

2. **Time Features** (10+ features):
   - Publication timing analysis
   - Seasonal patterns
   - Day-of-week effects
   - Time-since-publication metrics

3. **Text Features** (10+ features):
   - Sentiment analysis (polarity/subjectivity)
   - Keyword detection
   - Text complexity metrics
   - Language indicators

4. **Performance Features** (10+ features):
   - Growth rate calculations
   - Peak performance metrics
   - Consistency scores
   - Trend indicators

5. **Target Variables** (5+ targets):
   - Viewership categories (5-tier)
   - Viral classification (binary)
   - Engagement levels (3-tier)
   - Success scores (composite)

### Automation Layer (`scheduler.py`)

**Scheduled Tasks**:
- **Daily**: Video collection (02:00), Data processing (03:00)
- **Every 6 hours**: Performance tracking
- **Weekly**: Channel discovery, Integration tests
- **Monthly**: Cleanup and maintenance

**Features**:
- Subprocess management with timeouts
- Comprehensive logging and error handling
- Job status monitoring
- Automatic recovery mechanisms

## 🔐 Security & Error Handling

### API Security
- Environment variable configuration
- Multi-key rotation for quota management
- Rate limiting and respectful API usage
- Secure credential storage

### Error Handling Strategy
1. **Graceful Degradation**: System continues with partial failures
2. **Retry Logic**: Exponential backoff for transient errors
3. **Comprehensive Logging**: Detailed error tracking and debugging
4. **Recovery Mechanisms**: Automatic recovery from common failures
5. **Validation Gates**: Data quality checks at each stage

### Data Integrity
- Duplicate detection and removal
- Schema validation for all data
- Backup and versioning of critical data
- Audit trails for all operations

## 📊 Performance Characteristics

### Scalability Metrics
- **Channel Capacity**: 1000+ channels supported
- **Video Processing**: 10,000+ videos per run
- **API Efficiency**: 95%+ quota utilization
- **Processing Speed**: 1000 videos/minute feature engineering

### Resource Requirements
- **Memory**: 2-4GB for large datasets
- **Storage**: 1GB per 10,000 videos (raw + processed)
- **API Quota**: 2,000-10,000 units per full collection
- **Processing Time**: 30-60 minutes for complete pipeline

## 🔄 Integration Points

### External APIs
- **YouTube Data API v3**: Primary data source
- **Google Trends** (optional): Keyword expansion
- **TextBlob**: Sentiment analysis

### Data Formats
- **Input**: JSON (API responses), CSV (processed data)
- **Output**: CSV (analytics), JSON (metadata), Logs (monitoring)
- **Interchange**: Pandas DataFrames for processing

### Deployment Options
- **Local Development**: Direct script execution
- **Automated**: Cron/Task Scheduler integration
- **Containerized**: Docker deployment ready
- **Cloud**: Scalable cloud deployment supported

## 🚀 Future Architecture Considerations

### Planned Enhancements
1. **Real-time Dashboard**: Streamlit/Flask web interface
2. **Machine Learning Pipeline**: Automated model training
3. **API Service**: RESTful API for external access
4. **Database Integration**: PostgreSQL/MongoDB support
5. **Distributed Processing**: Multi-node processing capability

### Extensibility Points
- **Plugin Architecture**: Custom data sources
- **Feature Modules**: Pluggable feature engineering
- **Export Formats**: Multiple output formats
- **Notification Systems**: Alert and monitoring integration

This architecture provides a robust, scalable foundation for YouTube content analysis and forecasting, with clear separation of concerns and comprehensive error handling throughout the system.
