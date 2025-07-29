# 🤖 Automation Guide

## Overview

The YouTube Forecasting System includes a comprehensive automation framework that handles scheduled data collection, processing, and maintenance tasks. This guide covers setup, configuration, and production deployment of the automated system.

## 🚀 Quick Start

### Basic Automation Setup

```bash
# 1. Test individual components
python scripts/collect_videos.py --max-videos 10
python scripts/track_performance.py
python scripts/process_data.py

# 2. Run scheduler in test mode
python scripts/scheduler.py --show-schedule

# 3. Run a single job immediately
python scripts/scheduler.py --run-job collect_videos

# 4. Start continuous automation
python scripts/scheduler.py --daemon
```

## 📅 Scheduled Tasks Overview

### Default Schedule

| Task | Frequency | Time | Purpose |
|------|-----------|------|---------|
| **Video Collection** | Daily | 02:00 | Collect new videos from channels |
| **Data Processing** | Daily | 03:00 | Process and engineer features |
| **Performance Tracking** | Every 6 hours | 00:00, 06:00, 12:00, 18:00 | Track engagement metrics |
| **Channel Discovery** | Weekly | Sunday 01:00 | Discover new Sri Lankan channels |
| **Integration Tests** | Weekly | Sunday 04:00 | Validate system health |
| **Cleanup Tasks** | Monthly | 1st of month | Clean old logs and data |

### Task Dependencies

```
Channel Discovery → Video Collection → Data Processing
                                    ↓
Performance Tracking ←→ Data Processing
                                    ↓
                            Integration Tests
```

## 🔧 Scheduler Configuration

### Core Scheduler (`scheduler.py`)

The scheduler is built using the `schedule` library and provides:

- **Subprocess Management**: Isolated execution of each task
- **Timeout Protection**: 1-hour timeout per task
- **Error Handling**: Comprehensive error logging and recovery
- **Status Monitoring**: Real-time job status tracking

### Configuration Options

```python
# In scripts/scheduler.py
class YouTubeDataScheduler:
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.scripts_dir = os.path.join(self.project_root, 'scripts')
        self.is_running = False
```

### Custom Schedule Setup

```python
# Modify setup_schedule() method for custom timing
def setup_schedule(self):
    # Custom daily collection time
    schedule.every().day.at("01:30").do(self.collect_videos_job)
    
    # Custom processing interval
    schedule.every(4).hours.do(self.track_performance_job)
    
    # Custom weekly tasks
    schedule.every().monday.at("02:00").do(self.channel_discovery_job)
```

## 🖥️ Production Deployment

### Option 1: Windows Task Scheduler

#### Setup Steps

1. **Create Batch Script** (`run_scheduler.bat`):
```batch
@echo off
cd /d "C:\path\to\youtube-forecasting-project"
python scripts\scheduler.py --daemon
pause
```

2. **Create Task in Task Scheduler**:
```powershell
# Open Task Scheduler
taskschd.msc

# Create Basic Task
# - Name: "YouTube Data Scheduler"
# - Trigger: "When the computer starts"
# - Action: "Start a program"
# - Program: "C:\path\to\run_scheduler.bat"
# - Start in: "C:\path\to\youtube-forecasting-project"
```

3. **Advanced Settings**:
- Run whether user is logged on or not
- Run with highest privileges
- Configure for Windows 10/11
- Allow task to be run on demand

#### Alternative: Direct Python Execution
```powershell
# Create scheduled task directly
schtasks /create /tn "YouTube Scheduler" /tr "python C:\path\to\scripts\scheduler.py --daemon" /sc onstart /ru SYSTEM
```

### Option 2: Linux/Mac Cron Jobs

#### Setup Steps

1. **Create Wrapper Script** (`run_scheduler.sh`):
```bash
#!/bin/bash
cd /path/to/youtube-forecasting-project
source venv/bin/activate  # If using virtual environment
python scripts/scheduler.py --daemon >> data/logs/scheduler.log 2>&1
```

2. **Make Executable**:
```bash
chmod +x run_scheduler.sh
```

3. **Add to Crontab**:
```bash
# Edit crontab
crontab -e

# Add entry to start scheduler on reboot
@reboot /path/to/youtube-forecasting-project/run_scheduler.sh

# Alternative: Individual task scheduling
0 2 * * * cd /path/to/project && python scripts/collect_videos.py --max-videos 50
0 3 * * * cd /path/to/project && python scripts/process_data.py
0 */6 * * * cd /path/to/project && python scripts/track_performance.py
0 1 * * 0 cd /path/to/project && python scripts/collect_channels.py --location-search --max-results 50
```

### Option 3: Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/logs data/raw data/processed data/snapshots

# Set environment variables
ENV PYTHONPATH=/app/scripts

# Start scheduler
CMD ["python", "scripts/scheduler.py", "--daemon"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  youtube-scheduler:
    build: .
    container_name: youtube-scheduler
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/data/logs
    environment:
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - YOUTUBE_API_KEY_1=${YOUTUBE_API_KEY_1}
      - YOUTUBE_API_KEY_2=${YOUTUBE_API_KEY_2}
    env_file:
      - .env
```

#### Deployment Commands
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f youtube-scheduler

# Stop
docker-compose down
```

### Option 4: Cloud Deployment

#### AWS EC2 Setup
```bash
# 1. Launch EC2 instance (t3.medium recommended)
# 2. Install dependencies
sudo yum update -y
sudo yum install python3 python3-pip git -y

# 3. Clone repository
git clone https://github.com/your-repo/youtube-forecasting-project.git
cd youtube-forecasting-project

# 4. Install Python dependencies
pip3 install -r requirements.txt

# 5. Configure environment
cp .env.template .env
# Edit .env with your API keys

# 6. Setup systemd service
sudo cp deployment/youtube-scheduler.service /etc/systemd/system/
sudo systemctl enable youtube-scheduler
sudo systemctl start youtube-scheduler
```

#### Systemd Service File (`youtube-scheduler.service`)
```ini
[Unit]
Description=YouTube Data Collection Scheduler
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/youtube-forecasting-project
ExecStart=/usr/bin/python3 scripts/scheduler.py --daemon
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home/ec2-user/youtube-forecasting-project/scripts

[Install]
WantedBy=multi-user.target
```

## 📊 Monitoring & Logging

### Log Files Structure

```
data/logs/
├── youtube_collector.log          # Main application logs
├── scheduler.log                  # Scheduler-specific logs
├── failed_channels_YYYYMMDD.json  # Failed channel operations
├── failed_tracking_YYYYMMDD.json  # Failed performance tracking
└── integration_test_results.json  # Test results
```

### Log Monitoring Commands

```bash
# Monitor real-time logs
tail -f data/logs/youtube_collector.log

# Check scheduler status
grep "Scheduler" data/logs/youtube_collector.log | tail -20

# Monitor errors
grep "ERROR" data/logs/youtube_collector.log | tail -10

# Check API quota usage
grep "quota" data/logs/youtube_collector.log | tail -5
```

### Health Check Script

Create `scripts/health_check.py`:
```python
#!/usr/bin/env python3
"""
Health check script for monitoring system status
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

def check_recent_data():
    """Check if data was collected recently"""
    raw_dir = Path("data/raw")
    if not raw_dir.exists():
        return False, "Raw data directory not found"
    
    # Check for recent video files
    video_files = list(raw_dir.glob("videos_*.csv"))
    if not video_files:
        return False, "No video data files found"
    
    # Check if most recent file is within last 2 days
    latest_file = max(video_files, key=os.path.getmtime)
    file_age = datetime.now() - datetime.fromtimestamp(latest_file.stat().st_mtime)
    
    if file_age > timedelta(days=2):
        return False, f"Latest data is {file_age.days} days old"
    
    return True, f"Latest data: {file_age.seconds // 3600} hours old"

def check_scheduler_status():
    """Check if scheduler is running"""
    log_file = Path("data/logs/youtube_collector.log")
    if not log_file.exists():
        return False, "Log file not found"
    
    # Check for recent scheduler activity
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    recent_lines = [line for line in lines[-100:] if "Scheduler" in line]
    if not recent_lines:
        return False, "No recent scheduler activity"
    
    return True, "Scheduler active"

def main():
    """Run health checks"""
    checks = [
        ("Data Collection", check_recent_data),
        ("Scheduler Status", check_scheduler_status),
    ]
    
    results = {}
    all_healthy = True
    
    for check_name, check_func in checks:
        try:
            status, message = check_func()
            results[check_name] = {"status": "OK" if status else "ERROR", "message": message}
            if not status:
                all_healthy = False
        except Exception as e:
            results[check_name] = {"status": "ERROR", "message": str(e)}
            all_healthy = False
    
    # Output results
    print(json.dumps(results, indent=2))
    
    # Exit with appropriate code
    exit(0 if all_healthy else 1)

if __name__ == "__main__":
    main()
```

### Monitoring Setup

```bash
# Add health check to cron (every 30 minutes)
*/30 * * * * cd /path/to/project && python scripts/health_check.py >> data/logs/health_check.log 2>&1

# Email alerts on failure (requires mail setup)
*/30 * * * * cd /path/to/project && python scripts/health_check.py || echo "YouTube Scheduler Health Check Failed" | mail -s "Alert" admin@example.com
```

## 🔧 Advanced Configuration

### Environment Variables

```bash
# Core settings
YOUTUBE_API_KEY=your_primary_key
YOUTUBE_API_KEY_1=your_secondary_key
YOUTUBE_API_KEY_2=your_tertiary_key

# Scheduler settings
SCHEDULER_CHECK_INTERVAL=60  # seconds
TASK_TIMEOUT=3600           # 1 hour
MAX_RETRIES=3

# Data collection settings
MAX_VIDEOS_PER_CHANNEL=100
COLLECTION_INTERVAL_HOURS=24
PERFORMANCE_TRACKING_INTERVAL_HOURS=6

# Feature engineering settings
SENTIMENT_ANALYSIS_ENABLED=true
ADVANCED_FEATURES_ENABLED=true

# Logging settings
LOG_LEVEL=INFO
LOG_FILE_PATH=data/logs/youtube_collector.log
```

### Custom Job Configuration

```python
# Add custom jobs to scheduler
def custom_analytics_job(self):
    """Custom analytics job"""
    logger.info("🔍 Starting custom analytics...")
    success = self.run_script('custom_analytics.py')
    
    if success:
        logger.info("✅ Custom analytics completed")
    else:
        logger.error("❌ Custom analytics failed")

# Add to schedule
schedule.every().day.at("05:00").do(self.custom_analytics_job)
```

### Performance Optimization

```python
# Optimize for production
COLLECTION_PARAMS = {
    'max_retries': 5,
    'retry_delay': 2,
    'rate_limit_delay': 0.5,  # Faster for production
    'batch_size': 50,         # Larger batches
    'concurrent_requests': 3   # Parallel processing
}
```

## 🚨 Error Handling & Recovery

### Automatic Recovery Mechanisms

1. **API Quota Exhaustion**: Automatic key rotation
2. **Network Failures**: Exponential backoff retry
3. **Data Corruption**: Validation and rollback
4. **Disk Space**: Automatic cleanup of old files
5. **Process Crashes**: Systemd/supervisor restart

### Manual Recovery Procedures

```bash
# Restart scheduler
sudo systemctl restart youtube-scheduler

# Clear failed jobs
rm data/logs/failed_*.json

# Reset API key rotation
python scripts/quota_check.py --reset-keys

# Rebuild processed data
python scripts/process_data.py --rebuild

# Validate data integrity
python scripts/validate_data.py --full-check
```

### Backup Strategy

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/youtube-data-$DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup critical data
cp -r data/processed $BACKUP_DIR/
cp -r data/raw $BACKUP_DIR/
cp .env $BACKUP_DIR/
cp -r scripts $BACKUP_DIR/

# Compress backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Keep only last 30 days of backups
find /backup -name "youtube-data-*.tar.gz" -mtime +30 -delete
```

## 📈 Performance Monitoring

### Key Metrics to Monitor

1. **Data Collection Rate**: Videos collected per hour
2. **API Quota Usage**: Percentage of daily quota used
3. **Processing Time**: Time to complete each pipeline stage
4. **Error Rate**: Percentage of failed operations
5. **Disk Usage**: Storage consumption growth
6. **Memory Usage**: Peak memory consumption

### Monitoring Dashboard Setup

```python
# Simple monitoring script
import psutil
import json
from datetime import datetime

def get_system_metrics():
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "disk_free_gb": psutil.disk_usage('/').free / (1024**3)
    }

# Log metrics every 5 minutes
with open('data/logs/system_metrics.jsonl', 'a') as f:
    f.write(json.dumps(get_system_metrics()) + '\n')
```

This automation framework provides a robust, production-ready solution for continuous YouTube data collection and analysis, with comprehensive monitoring and error recovery capabilities.
