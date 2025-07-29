# 👨‍💻 Development Guide

## Overview

This guide provides comprehensive information for developers who want to contribute to, extend, or customize the YouTube Forecasting System. It covers code structure, development practices, testing procedures, and contribution guidelines.

## 🏗️ Development Environment Setup

### Prerequisites

```bash
# Required software
- Python 3.8+ (3.9+ recommended)
- Git
- Text editor/IDE (VS Code recommended)
- YouTube Data API v3 access

# Optional but recommended
- Docker (for containerized development)
- Virtual environment manager (venv, conda, or pipenv)
```

### Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/L0rd008/youtube-forecasting-project.git
cd youtube-forecasting-project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install -r requirements-dev.txt  # If exists

# 5. Setup environment variables
cp .env.template .env
# Edit .env with your API keys and settings

# 6. Create data directories
mkdir -p data/{raw,processed,snapshots,logs}

# 7. Run initial tests
python scripts/collect_videos.py --max-videos 5
python scripts/process_data.py --no-sentiment
```

### Development Dependencies

```bash
# Core development tools
pip install pytest pytest-cov black flake8 mypy

# Optional analysis tools
pip install jupyter pandas matplotlib seaborn plotly

# Documentation tools
pip install sphinx sphinx-rtd-theme
```

## 📁 Code Structure & Architecture

### Core Modules

```
scripts/
├── config.py              # Configuration management
├── utils.py               # Shared utilities and API client
├── collect_channels.py    # Channel discovery system
├── collect_videos.py      # Video data collection
├── track_performance.py   # Performance monitoring
├── process_data.py        # Feature engineering pipeline
└── scheduler.py           # Task automation
```

### Module Responsibilities

#### `config.py` - Configuration Management
```python
# Centralized configuration
- Environment variables
- Channel definitions
- API parameters
- Feature engineering settings
- Validation rules

# Key functions:
- get_channel_ids_by_category()
- validate_api_key()
- get_quota_cost()
```

#### `utils.py` - Core Utilities
```python
# API Management
class YouTubeAPIClient:
    - Rate limiting and retry logic
    - Multi-key rotation
    - Error handling
    - Quota tracking

# Data Processing Helpers
- extract_video_metadata()
- extract_channel_metadata()
- parse_iso_duration()
- convert_to_local_time()

# File I/O Operations
- save_to_csv(), save_to_json()
- load_from_csv(), load_from_json()
```

#### `collect_channels.py` - Channel Discovery
```python
# Advanced Discovery System
class ChannelDiscoverer:
    - Keyword expansion engine
    - Multi-strategy discovery
    - Sri Lankan relevance scoring
    - Automatic categorization

# Key methods:
- discover_channels_unlimited()
- expand_keywords()
- score_sri_lankan_relevance()
```

#### `collect_videos.py` - Video Collection
```python
# Video Data Collection
class VideoCollector:
    - Batch processing
    - Category-based collection
    - Data validation
    - Error tracking

# Key methods:
- collect_all_videos()
- collect_videos_by_category()
- collect_recent_videos()
```

#### `process_data.py` - Feature Engineering
```python
# Data Processing Pipeline
class DataProcessor:
    - 50+ feature engineering
    - Text analysis
    - Time-based features
    - Target variable creation

# Key methods:
- process_all_data()
- engineer_basic_features()
- engineer_text_features()
- create_target_variables()
```

## 🔧 Development Patterns

### Error Handling Pattern

```python
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

def robust_function(param: str) -> Optional[Dict]:
    """
    Template for robust function implementation
    """
    try:
        # Main logic here
        result = perform_operation(param)
        logger.info(f"Operation successful: {param}")
        return result
        
    except SpecificException as e:
        logger.error(f"Specific error in {param}: {e}")
        # Handle specific case
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error in {param}: {e}")
        # Handle general case
        return None
```

### API Client Pattern

```python
class APIClient:
    """Template for API client implementation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.quota_used = 0
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting"""
        # Rate limiting logic
        pass
    
    def _make_request(self, request, quota_cost: int = 1):
        """Make API request with error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                response = request.execute()
                self.quota_used += quota_cost
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
```

### Data Processing Pattern

```python
class DataProcessor:
    """Template for data processing classes"""
    
    def __init__(self):
        self.data = pd.DataFrame()
        self.processed_data = pd.DataFrame()
        self.stats = {}
    
    def load_data(self, source: str) -> bool:
        """Load data with validation"""
        try:
            self.data = pd.read_csv(source)
            return self._validate_data()
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False
    
    def _validate_data(self) -> bool:
        """Validate loaded data"""
        required_columns = ['id', 'timestamp']
        return all(col in self.data.columns for col in required_columns)
    
    def process(self) -> pd.DataFrame:
        """Main processing pipeline"""
        if self.data.empty:
            raise ValueError("No data loaded")
        
        # Processing steps
        self.processed_data = self.data.copy()
        self._clean_data()
        self._engineer_features()
        self._calculate_stats()
        
        return self.processed_data
```

## 🧪 Testing Framework

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration
├── test_config.py           # Configuration tests
├── test_utils.py            # Utility function tests
├── test_collect_channels.py # Channel discovery tests
├── test_collect_videos.py   # Video collection tests
├── test_process_data.py     # Data processing tests
└── integration/
    ├── test_full_pipeline.py
    └── test_api_integration.py
```

### Unit Test Examples

```python
# tests/test_utils.py
import pytest
from unittest.mock import Mock, patch
from scripts.utils import YouTubeAPIClient, parse_iso_duration

class TestYouTubeAPIClient:
    
    def test_initialization(self):
        """Test API client initialization"""
        client = YouTubeAPIClient("test_key")
        assert client.api_key == "test_key"
        assert client.quota_used == 0
    
    @patch('scripts.utils.build')
    def test_service_initialization(self, mock_build):
        """Test YouTube service initialization"""
        mock_build.return_value = Mock()
        client = YouTubeAPIClient("test_key")
        client._initialize_service()
        mock_build.assert_called_once()

def test_parse_iso_duration():
    """Test ISO duration parsing"""
    assert parse_iso_duration("PT1M30S") == 90
    assert parse_iso_duration("PT1H") == 3600
    assert parse_iso_duration("PT0S") == 0
    assert parse_iso_duration("invalid") == 0

# tests/test_process_data.py
import pandas as pd
from scripts.process_data import DataProcessor

class TestDataProcessor:
    
    def test_basic_feature_engineering(self):
        """Test basic feature creation"""
        # Sample data
        data = pd.DataFrame({
            'title': ['Test Video', 'Another Video'],
            'duration_seconds': [120, 300],
            'view_count': [1000, 5000],
            'like_count': [50, 200]
        })
        
        processor = DataProcessor()
        processor.raw_videos = data
        result = processor.engineer_basic_features(data)
        
        # Check engineered features
        assert 'title_length' in result.columns
        assert 'duration_minutes' in result.columns
        assert 'like_ratio' in result.columns
        assert result['title_length'].iloc[0] == 10  # len('Test Video')
```

### Integration Tests

```python
# tests/integration/test_full_pipeline.py
import pytest
from scripts.collect_videos import VideoCollector
from scripts.process_data import DataProcessor

@pytest.mark.integration
def test_full_pipeline():
    """Test complete data pipeline"""
    # This test requires valid API keys
    if not os.getenv('YOUTUBE_API_KEY'):
        pytest.skip("No API key available")
    
    # Collect small dataset
    collector = VideoCollector()
    videos = collector.collect_videos_by_category('music', max_videos=5)
    
    assert len(videos) > 0
    assert all('video_id' in video for video in videos)
    
    # Process data
    processor = DataProcessor()
    processor.raw_videos = pd.DataFrame(videos)
    processed = processor.process_all_data()
    
    assert len(processed) > 0
    assert 'title_length' in processed.columns
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scripts --cov-report=html

# Run specific test file
pytest tests/test_utils.py

# Run integration tests only
pytest -m integration

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

## 🔍 Code Quality & Standards

### Code Formatting

```bash
# Black - Code formatter
black scripts/ tests/

# Check formatting without changes
black --check scripts/

# Format specific file
black scripts/utils.py
```

### Linting

```bash
# Flake8 - Style guide enforcement
flake8 scripts/ tests/

# Configuration in setup.cfg or .flake8
[flake8]
max-line-length = 88
ignore = E203, W503
exclude = venv/, .git/, __pycache__/
```

### Type Checking

```bash
# MyPy - Static type checking
mypy scripts/

# Configuration in mypy.ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
```

## 🚀 Adding New Features

### Adding a New Data Source

1. **Create Data Source Module**
```python
# scripts/collect_new_source.py
from utils import YouTubeAPIClient, setup_logging

logger = setup_logging()

class NewSourceCollector:
    def __init__(self, api_key: str = None):
        self.client = YouTubeAPIClient(api_key)
        self.collected_data = []
    
    def collect_data(self, params: dict) -> list:
        """Collect data from new source"""
        # Implementation here
        pass
```

2. **Add Configuration**
```python
# In config.py
NEW_SOURCE_PARAMS = {
    'endpoint': 'new_endpoint',
    'max_results': 100,
    'rate_limit': 1.0
}
```

3. **Add Tests**
```python
# tests/test_collect_new_source.py
def test_new_source_collector():
    collector = NewSourceCollector()
    # Test implementation
```

4. **Update Documentation**
```markdown
# In relevant docs
## New Source Collection
- Description of new feature
- Usage examples
- Configuration options
```

### Adding New Features to Processing Pipeline

1. **Extend DataProcessor**
```python
# In process_data.py
def engineer_new_features(self, df: pd.DataFrame) -> pd.DataFrame:
    """Engineer new feature category"""
    logger.info("Engineering new features...")
    
    # Feature calculations
    df['new_feature_1'] = df['existing_col'].apply(lambda x: calculate_feature(x))
    df['new_feature_2'] = df.groupby('category')['metric'].transform('mean')
    
    return df

# Add to main pipeline
def process_all_data(self):
    # ... existing code ...
    df = self.engineer_new_features(df)
    # ... rest of pipeline ...
```

2. **Add Feature Documentation**
```python
# Update FEATURE_ENGINEERING_GUIDE.md
### New Feature Category (X features)
| Feature | Description | Calculation | Range |
|---------|-------------|-------------|-------|
| new_feature_1 | Description | Formula | 0-100 |
```

### Adding New Automation Tasks

1. **Create Task Function**
```python
# In scheduler.py
def new_task_job(self):
    """New automated task"""
    logger.info("🔄 Starting new task...")
    success = self.run_script('new_task_script.py')
    
    if success:
        logger.info("✅ New task completed")
    else:
        logger.error("❌ New task failed")
```

2. **Add to Schedule**
```python
# In setup_schedule()
schedule.every().day.at("04:00").do(self.new_task_job)
```

## 🐛 Debugging & Troubleshooting

### Logging Best Practices

```python
import logging

# Use module-level logger
logger = logging.getLogger(__name__)

# Log levels usage
logger.debug("Detailed debugging information")
logger.info("General information about program execution")
logger.warning("Something unexpected happened")
logger.error("A serious error occurred")
logger.critical("A very serious error occurred")

# Structured logging
logger.info(f"Processing {len(items)} items", extra={
    'item_count': len(items),
    'processing_type': 'batch'
})
```

### Debug Mode Setup

```python
# Enable debug mode
import os
os.environ['DEBUG'] = '1'

# In your code
DEBUG = os.getenv('DEBUG', '').lower() == '1'

if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
    # Enable additional debug features
```

### Common Debugging Scenarios

```python
# API debugging
def debug_api_request(self, request):
    if DEBUG:
        print(f"API Request: {request}")
        print(f"Current quota: {self.quota_used}")
    
    response = self._make_request(request)
    
    if DEBUG:
        print(f"API Response: {response}")
    
    return response

# Data processing debugging
def debug_dataframe(df: pd.DataFrame, name: str):
    if DEBUG:
        print(f"\n=== {name} ===")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Memory usage: {df.memory_usage().sum() / 1024**2:.2f} MB")
        print(df.head())
```

## 📦 Packaging & Distribution

### Setup.py Configuration

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="youtube-forecasting-system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "google-api-python-client>=2.0.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "python-dotenv>=0.19.0",
        "textblob>=0.17.0",
        "schedule>=1.1.0",
        "tqdm>=4.62.0",
        "pytz>=2021.3"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910"
        ]
    },
    entry_points={
        "console_scripts": [
            "youtube-collect=scripts.collect_videos:main",
            "youtube-process=scripts.process_data:main",
            "youtube-schedule=scripts.scheduler:main"
        ]
    }
)
```

### Docker Development

```dockerfile
# Dockerfile.dev
FROM python:3.9-slim

WORKDIR /app

# Install development dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements.txt -r requirements-dev.txt

# Copy source code
COPY . .

# Development server
CMD ["python", "-m", "pytest", "--cov=scripts"]
```

## 🤝 Contributing Guidelines

### Pull Request Process

1. **Fork and Clone**
```bash
git clone https://github.com/your-username/youtube-forecasting-project.git
cd youtube-forecasting-project
git remote add upstream https://github.com/L0rd008/youtube-forecasting-project.git
```

2. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Development Workflow**
```bash
# Make changes
# Add tests
# Run tests
pytest

# Format code
black scripts/ tests/

# Check linting
flake8 scripts/ tests/

# Type checking
mypy scripts/
```

4. **Commit and Push**
```bash
git add .
git commit -m "feat: add new feature description"
git push origin feature/your-feature-name
```

5. **Create Pull Request**
- Provide clear description
- Reference related issues
- Include test results
- Update documentation

### Commit Message Convention

```
feat: add new feature
fix: bug fix
docs: documentation changes
style: formatting changes
refactor: code refactoring
test: add or update tests
chore: maintenance tasks
```

### Code Review Checklist

- [ ] Code follows project style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

This development guide provides the foundation for contributing to and extending the YouTube Forecasting System. Follow these patterns and practices to maintain code quality and system reliability.
