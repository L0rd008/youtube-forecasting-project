# 🔬 Feature Engineering Guide

## Overview

The YouTube Forecasting System implements a comprehensive feature engineering pipeline that transforms raw video metadata into 50+ machine learning-ready features. This guide documents all features, their calculations, and usage patterns.

## 📊 Feature Categories

### 1. **Basic Metadata Features** (15 features)

#### Text-Based Features
| Feature | Description | Calculation | Range |
|---------|-------------|-------------|-------|
| `title_length` | Character count in video title | `len(title)` | 0-100+ |
| `title_word_count` | Word count in video title | `len(title.split())` | 1-20+ |
| `description_length` | Character count in description | `len(description)` | 0-5000+ |
| `description_word_count` | Word count in description | `len(description.split())` | 0-1000+ |
| `tag_count` | Number of tags assigned | `len(tags)` | 0-50+ |

#### Duration Features
| Feature | Description | Calculation | Range |
|---------|-------------|-------------|-------|
| `duration_seconds` | Video length in seconds | From ISO 8601 duration | 10-14400 |
| `duration_minutes` | Video length in minutes | `duration_seconds / 60` | 0.17-240 |
| `duration_category` | Categorical duration | Binned duration | very_short, short, medium, long, very_long |

**Duration Categories**:
- `very_short`: 0-60 seconds
- `short`: 60-300 seconds (1-5 minutes)
- `medium`: 300-600 seconds (5-10 minutes)
- `long`: 600-1800 seconds (10-30 minutes)
- `very_long`: 1800+ seconds (30+ minutes)

#### Engagement Features
| Feature | Description | Calculation | Range |
|---------|-------------|-------------|-------|
| `like_ratio` | Likes per view | `like_count / (view_count + 1)` | 0-1 |
| `comment_ratio` | Comments per view | `comment_count / (view_count + 1)` | 0-1 |
| `engagement_ratio` | Total engagement per view | `(likes + comments) / (views + 1)` | 0-1 |

#### Channel Features
| Feature | Description | Calculation | Range |
|---------|-------------|-------------|-------|
| `subscriber_count` | Channel subscriber count | From channel metadata | 0-10M+ |
| `channel_video_count` | Total videos on channel | From channel metadata | 1-10000+ |
| `avg_views_per_video` | Channel average views | `total_views / video_count` | 0-1M+ |
| `channel_size` | Channel size category | Binned subscriber count | micro, small, medium, large, mega |

**Channel Size Categories**:
- `micro`: 0-1,000 subscribers
- `small`: 1,000-10,000 subscribers
- `medium`: 10,000-100,000 subscribers
- `large`: 100,000-1,000,000 subscribers
- `mega`: 1,000,000+ subscribers

### 2. **Time-Based Features** (12 features)

#### Publication Timing
| Feature | Description | Calculation | Range |
|---------|-------------|-------------|-------|
| `year` | Publication year | From `published_at` | 2020-2025+ |
| `month` | Publication month | From `published_at` | 1-12 |
| `day` | Publication day | From `published_at` | 1-31 |
| `hour` | Publication hour (local time) | From `published_at` in Asia/Colombo | 0-23 |
| `day_of_week` | Day of week (0=Monday) | From `published_at` | 0-6 |
| `is_weekend` | Weekend indicator | `day_of_week >= 5` | True/False |

#### Temporal Patterns
| Feature | Description | Calculation | Range |
|---------|-------------|-------------|-------|
| `day_of_year` | Day within year | From `published_at` | 1-366 |
| `week_of_year` | Week within year | From `published_at` | 1-53 |
| `quarter` | Quarter of year | `(month - 1) // 3 + 1` | 1-4 |
| `publish_time_category` | Time of day category | Binned hour | night, morning, afternoon, evening |

**Time Categories**:
- `night`: 0-6 hours
- `morning`: 6-12 hours
- `afternoon`: 12-18 hours
- `evening`: 18-24 hours

#### Age Features
| Feature | Description | Calculation | Range |
|---------|-------------|-------------|-------|
| `days_since_published` | Days since publication | `(now - published_at).days` | 0-1000+ |
| `weeks_since_published` | Weeks since publication | `days_since_published / 7` | 0-150+ |

### 3. **Text Analysis Features** (15 features)

#### Sentiment Analysis
| Feature | Description | Calculation | Range |
|---------|-------------|-------------|-------|
| `title_sentiment_polarity` | Title sentiment polarity | TextBlob sentiment | -1 to 1 |
| `title_sentiment_subjectivity` | Title sentiment subjectivity | TextBlob sentiment | 0 to 1 |

#### Text Complexity
| Feature | Description | Calculation | Range |
|---------|-------------|-------------|-------|
| `title_exclamation_count` | Exclamation marks in title | `title.count('!')` | 0-10+ |
| `title_question_count` | Question marks in title | `title.count('?')` | 0-5+ |
| `title_caps_ratio` | Ratio of uppercase characters | `uppercase_chars / total_chars` | 0-1 |

#### Keyword Detection (Boolean Features)
| Feature | Description | Detection Pattern |
|---------|-------------|-------------------|
| `title_has_tutorial` | Contains "tutorial" | Case-insensitive match |
| `title_has_review` | Contains "review" | Case-insensitive match |
| `title_has_unboxing` | Contains "unboxing" | Case-insensitive match |
| `title_has_vlog` | Contains "vlog" | Case-insensitive match |
| `title_has_challenge` | Contains "challenge" | Case-insensitive match |
| `title_has_reaction` | Contains "reaction" | Case-insensitive match |
| `title_has_how_to` | Contains "how to" | Case-insensitive match |
| `title_has_tips` | Contains "tips" | Case-insensitive match |
| `title_has_tricks` | Contains "tricks" | Case-insensitive match |

### 4. **Performance Features** (10 features)

#### Growth Metrics
| Feature | Description | Calculation | Range |
|---------|-------------|-------------|-------|
| `view_growth_rate` | Daily view growth rate | `(current_views - initial_views) / days` | 0-100000+ |
| `like_growth_rate` | Daily like growth rate | `(current_likes - initial_likes) / days` | 0-1000+ |
| `comment_growth_rate` | Daily comment growth rate | `(current_comments - initial_comments) / days` | 0-100+ |
| `view_growth_24h` | 24-hour view growth | From snapshots comparison | 0-1M+ |
| `like_growth_24h` | 24-hour like growth | From snapshots comparison | 0-10000+ |
| `comment_growth_24h` | 24-hour comment growth | From snapshots comparison | 0-1000+ |
| `view_growth_7d` | 7-day view growth | From snapshots comparison | 0-10M+ |
| `like_growth_7d` | 7-day like growth | From snapshots comparison | 0-100000+ |
| `comment_growth_7d` | 7-day comment growth | From snapshots comparison | 0-10000+ |

#### Performance Indicators
| Feature | Description | Calculation | Range |
|---------|-------------|-------------|-------|
| `peak_daily_views` | Highest single-day views | `max(daily_view_growth)` | 0-1M+ |
| `consistency_score` | Growth consistency | `mean_growth / std_growth` | 0-10+ |

### 5. **Category Features** (3 features)

| Feature | Description | Values |
|---------|-------------|--------|
| `category_id` | YouTube category ID | 1, 2, 10, 15, 17, 19, 20, 22, 23, 24, 25, 26, 27, 28, 29 |
| `category_name` | YouTube category name | Film & Animation, Autos & Vehicles, Music, etc. |
| `channel_category` | Custom channel category | news_media, music, entertainment, education, vlogs_lifestyle, sports |

## 🎯 Target Variables (5 targets)

### Classification Targets

#### 1. **Viewership Categories** (`viewership_category`)
5-tier classification based on view count percentiles:
- `low`: ≤ 25th percentile
- `medium_low`: 25th-50th percentile  
- `medium_high`: 50th-75th percentile
- `high`: 75th-90th percentile
- `viral`: > 90th percentile

#### 2. **Viral Classification** (`is_viral`)
Binary classification:
- `1`: Views ≥ 100,000 (configurable threshold)
- `0`: Views < 100,000

#### 3. **Engagement Level** (`engagement_level`)
3-tier classification based on engagement ratio:
- `low`: ≤ 33rd percentile
- `medium`: 33rd-67th percentile
- `high`: > 67th percentile

### Regression Targets

#### 4. **Success Score** (`success_score`)
Composite metric combining views and engagement:
```python
view_score = (views - min_views) / (max_views - min_views)
engagement_score = (engagement - min_engagement) / (max_engagement - min_engagement)
success_score = 0.7 * view_score + 0.3 * engagement_score
```

#### 5. **Component Scores**
- `view_score`: Normalized view count (0-1)
- `engagement_score`: Normalized engagement ratio (0-1)

## 🔧 Feature Engineering Pipeline

### Processing Steps

1. **Data Loading & Validation**
   ```python
   # Load raw video and channel data
   # Validate required fields
   # Remove duplicates
   ```

2. **Basic Feature Extraction**
   ```python
   # Text length calculations
   # Duration processing
   # Engagement ratios
   # Channel metadata integration
   ```

3. **Time Feature Engineering**
   ```python
   # Parse timestamps to local timezone
   # Extract temporal components
   # Calculate age metrics
   # Create time categories
   ```

4. **Text Analysis** (Optional)
   ```python
   # Sentiment analysis with TextBlob
   # Keyword detection
   # Text complexity metrics
   ```

5. **Performance Features** (If snapshots available)
   ```python
   # Load historical snapshots
   # Calculate growth rates
   # Compute performance indicators
   ```

6. **Target Variable Creation**
   ```python
   # Calculate percentiles
   # Create categorical targets
   # Normalize continuous targets
   ```

### Configuration Options

```python
# Enable/disable sentiment analysis
SENTIMENT_ANALYSIS_ENABLED = True

# Enable/disable advanced features
ADVANCED_FEATURES_ENABLED = True

# Viral threshold (views)
VIRAL_VIEW_THRESHOLD = 100000

# Feature parameters
FEATURE_PARAMS = {
    'title_max_length': 100,
    'description_max_length': 5000,
    'tags_max_count': 50,
    'engagement_ratio_threshold': 0.05
}
```

## 📈 Feature Statistics & Quality

### Data Quality Metrics

The system automatically calculates feature statistics:

```json
{
  "total_videos": 5000,
  "date_range": {
    "start": "2024-01-01T00:00:00",
    "end": "2025-01-15T23:59:59"
  },
  "numeric_features": {
    "view_count": {
      "mean": 15420.5,
      "std": 45230.2,
      "min": 0,
      "max": 2500000,
      "median": 3200,
      "missing_count": 0
    }
  },
  "categorical_features": {
    "viewership_category": {
      "low": 1250,
      "medium_low": 1250,
      "medium_high": 1250,
      "high": 750,
      "viral": 500
    }
  }
}
```

### Feature Importance Guidelines

**High Importance Features** (typically most predictive):
- `view_count`, `subscriber_count`, `engagement_ratio`
- `days_since_published`, `duration_minutes`
- `hour`, `is_weekend`, `channel_size`

**Medium Importance Features**:
- `title_length`, `title_word_count`, `tag_count`
- `like_ratio`, `comment_ratio`
- `category_name`, `channel_category`

**Low Importance Features** (useful for specific models):
- Sentiment scores, keyword flags
- Growth rates (for time-series models)
- Text complexity metrics

## 🚀 Usage Examples

### Basic Feature Engineering

```python
from scripts.process_data import DataProcessor

# Initialize processor
processor = DataProcessor()

# Process all data with full pipeline
processed_df = processor.process_all_data()

# Save results
processor.save_processed_data()
```

### Custom Feature Selection

```python
# Select specific feature categories
basic_features = [
    'title_length', 'duration_minutes', 'engagement_ratio',
    'subscriber_count', 'days_since_published'
]

time_features = [
    'hour', 'day_of_week', 'is_weekend', 'quarter'
]

# Combine for modeling
model_features = basic_features + time_features
X = processed_df[model_features]
y = processed_df['viewership_category']
```

### Feature Analysis

```python
# Analyze feature distributions
import pandas as pd
import matplotlib.pyplot as plt

# Load processed data
df = pd.read_csv('data/processed/processed_videos.csv')

# Feature correlation analysis
correlation_matrix = df.select_dtypes(include=[np.number]).corr()

# Target variable analysis
target_distribution = df['viewership_category'].value_counts()
```

## 🔍 Advanced Feature Engineering

### Custom Feature Creation

```python
# Add custom features to the pipeline
def create_custom_features(df):
    # Title complexity score
    df['title_complexity'] = (
        df['title_word_count'] * 0.3 +
        df['title_caps_ratio'] * 0.2 +
        df['title_exclamation_count'] * 0.5
    )
    
    # Channel performance score
    df['channel_performance'] = (
        df['avg_views_per_video'] / df['subscriber_count']
    ).fillna(0)
    
    # Optimal posting time indicator
    df['optimal_time'] = (
        (df['hour'].between(18, 22)) & 
        (df['day_of_week'].between(4, 6))
    ).astype(int)
    
    return df
```

### Feature Scaling & Normalization

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Standardize numerical features
scaler = StandardScaler()
numerical_features = df.select_dtypes(include=[np.number]).columns
df[numerical_features] = scaler.fit_transform(df[numerical_features])

# Normalize specific features to 0-1 range
minmax_scaler = MinMaxScaler()
engagement_features = ['like_ratio', 'comment_ratio', 'engagement_ratio']
df[engagement_features] = minmax_scaler.fit_transform(df[engagement_features])
```

This comprehensive feature engineering pipeline transforms raw YouTube metadata into a rich, ML-ready dataset optimized for predicting video performance in the Sri Lankan context.
