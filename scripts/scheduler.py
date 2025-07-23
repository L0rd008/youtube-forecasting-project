"""
Automated Scheduler for YouTube Data Collection System
Handles periodic data collection, processing, and maintenance tasks
"""

import os
import sys
import time
import schedule
import subprocess
from datetime import datetime, timedelta
from typing import Optional

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logging
from config import DATA_LOGS_PATH

logger = setup_logging()

class YouTubeDataScheduler:
    """Main scheduler class for automating data collection tasks"""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize the scheduler"""
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.scripts_dir = os.path.join(self.project_root, 'scripts')
        self.is_running = False
        
        # Ensure logs directory exists
        os.makedirs(DATA_LOGS_PATH, exist_ok=True)
        
        logger.info(f"Scheduler initialized with project root: {self.project_root}")
    
    def run_script(self, script_name: str, args: list = None) -> bool:
        """Run a Python script with optional arguments"""
        try:
            script_path = os.path.join(self.scripts_dir, script_name)
            
            if not os.path.exists(script_path):
                logger.error(f"Script not found: {script_path}")
                return False
            
            # Build command
            cmd = [sys.executable, script_path]
            if args:
                cmd.extend(args)
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            # Run the script
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {script_name} completed successfully")
                if result.stdout:
                    logger.debug(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"❌ {script_name} failed with return code {result.returncode}")
                if result.stderr:
                    logger.error(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {script_name} timed out after 1 hour")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to run {script_name}: {e}")
            return False
    
    def collect_videos_job(self):
        """Daily video collection job"""
        logger.info("🚀 Starting daily video collection...")
        success = self.run_script('collect_videos.py', ['--max-videos', '50'])
        
        if success:
            logger.info("✅ Daily video collection completed")
        else:
            logger.error("❌ Daily video collection failed")
    
    def track_performance_job(self):
        """Performance tracking job"""
        logger.info("📊 Starting performance tracking...")
        success = self.run_script('track_performance.py')
        
        if success:
            logger.info("✅ Performance tracking completed")
        else:
            logger.error("❌ Performance tracking failed")
    
    def process_data_job(self):
        """Data processing job"""
        logger.info("🔄 Starting data processing...")
        success = self.run_script('process_data.py')
        
        if success:
            logger.info("✅ Data processing completed")
        else:
            logger.error("❌ Data processing failed")
    
    def channel_discovery_job(self):
        """Weekly channel discovery job"""
        logger.info("🔍 Starting channel discovery...")
        success = self.run_script('collect_channels.py', ['--location-search', '--max-results', '50'])
        
        if success:
            logger.info("✅ Channel discovery completed")
        else:
            logger.error("❌ Channel discovery failed")
    
    def integration_test_job(self):
        """Weekly integration test job"""
        logger.info("🧪 Running integration tests...")
        success = self.run_script('test_integration.py')
        
        if success:
            logger.info("✅ Integration tests passed")
        else:
            logger.error("❌ Integration tests failed")
    
    def cleanup_job(self):
        """Monthly cleanup job"""
        logger.info("🧹 Starting cleanup tasks...")
        
        try:
            # Clean old log files (older than 30 days)
            logs_dir = os.path.join(self.project_root, 'data', 'logs')
            if os.path.exists(logs_dir):
                cutoff_date = datetime.now() - timedelta(days=30)
                
                for filename in os.listdir(logs_dir):
                    filepath = os.path.join(logs_dir, filename)
                    if os.path.isfile(filepath):
                        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        if file_time < cutoff_date:
                            os.remove(filepath)
                            logger.info(f"Removed old log file: {filename}")
            
            # Clean old raw data files (older than 90 days)
            raw_dir = os.path.join(self.project_root, 'data', 'raw')
            if os.path.exists(raw_dir):
                cutoff_date = datetime.now() - timedelta(days=90)
                
                for filename in os.listdir(raw_dir):
                    if filename.startswith('videos_') and filename.endswith('.csv'):
                        filepath = os.path.join(raw_dir, filename)
                        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        if file_time < cutoff_date:
                            os.remove(filepath)
                            logger.info(f"Removed old raw data file: {filename}")
            
            logger.info("✅ Cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
    
    def setup_schedule(self):
        """Set up the scheduled jobs"""
        logger.info("Setting up scheduled jobs...")
        
        # Daily jobs
        schedule.every().day.at("02:00").do(self.collect_videos_job)
        schedule.every().day.at("03:00").do(self.process_data_job)
        
        # Every 6 hours
        schedule.every(6).hours.do(self.track_performance_job)
        
        # Weekly jobs (Sundays)
        schedule.every().sunday.at("01:00").do(self.channel_discovery_job)
        schedule.every().sunday.at("04:00").do(self.integration_test_job)
        
        # Monthly jobs (1st of month)
        schedule.every().month.do(self.cleanup_job)
        
        logger.info("✅ Schedule configured:")
        logger.info("  - Daily video collection: 02:00")
        logger.info("  - Daily data processing: 03:00")
        logger.info("  - Performance tracking: Every 6 hours")
        logger.info("  - Channel discovery: Sundays 01:00")
        logger.info("  - Integration tests: Sundays 04:00")
        logger.info("  - Cleanup: Monthly")
    
    def run_scheduler(self):
        """Run the scheduler continuously"""
        logger.info("🚀 Starting YouTube Data Collection Scheduler...")
        self.is_running = True
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("⏹️ Scheduler stopped by user")
            self.is_running = False
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            self.is_running = False
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler...")
        self.is_running = False
    
    def run_job_now(self, job_name: str):
        """Run a specific job immediately"""
        jobs = {
            'collect_videos': self.collect_videos_job,
            'track_performance': self.track_performance_job,
            'process_data': self.process_data_job,
            'channel_discovery': self.channel_discovery_job,
            'integration_test': self.integration_test_job,
            'cleanup': self.cleanup_job
        }
        
        if job_name in jobs:
            logger.info(f"Running job immediately: {job_name}")
            jobs[job_name]()
        else:
            logger.error(f"Unknown job: {job_name}")
            logger.info(f"Available jobs: {', '.join(jobs.keys())}")
    
    def get_schedule_info(self):
        """Get information about scheduled jobs"""
        jobs_info = []
        for job in schedule.jobs:
            jobs_info.append({
                'job': str(job.job_func.__name__),
                'next_run': job.next_run.isoformat() if job.next_run else 'Not scheduled',
                'interval': str(job.interval),
                'unit': job.unit
            })
        
        return jobs_info

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube Data Collection Scheduler')
    parser.add_argument('--run-job', type=str, 
                       help='Run a specific job immediately',
                       choices=['collect_videos', 'track_performance', 'process_data', 
                               'channel_discovery', 'integration_test', 'cleanup'])
    parser.add_argument('--show-schedule', action='store_true',
                       help='Show scheduled jobs information')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon (continuous scheduling)')
    parser.add_argument('--project-root', type=str,
                       help='Project root directory path')
    
    args = parser.parse_args()
    
    try:
        scheduler = YouTubeDataScheduler(project_root=args.project_root)
        
        if args.show_schedule:
            scheduler.setup_schedule()
            jobs_info = scheduler.get_schedule_info()
            
            print("\n📅 SCHEDULED JOBS")
            print("=" * 50)
            for job_info in jobs_info:
                print(f"Job: {job_info['job']}")
                print(f"  Next run: {job_info['next_run']}")
                print(f"  Interval: {job_info['interval']} {job_info['unit']}")
                print()
        
        elif args.run_job:
            scheduler.run_job_now(args.run_job)
        
        elif args.daemon:
            scheduler.setup_schedule()
            scheduler.run_scheduler()
        
        else:
            print("YouTube Data Collection Scheduler")
            print("Use --help for available options")
            print("\nQuick start:")
            print("  python scheduler.py --daemon          # Run continuous scheduler")
            print("  python scheduler.py --show-schedule   # Show scheduled jobs")
            print("  python scheduler.py --run-job collect_videos  # Run job now")
        
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
