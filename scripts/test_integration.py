"""
Integration Test Script for YouTube Data Collection System
Tests API integration and validates the data collection pipeline
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import validate_api_key, SRI_LANKAN_CHANNELS
from utils import YouTubeAPIClient, setup_logging
from collect_videos import VideoCollector
from track_performance import PerformanceTracker
from process_data import DataProcessor

logger = setup_logging()

class IntegrationTester:
    """Main class for testing system integration"""
    
    def __init__(self):
        """Initialize the integration tester"""
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_status': 'PENDING'
        }
    
    def test_api_connection(self) -> bool:
        """Test YouTube API connection and authentication"""
        logger.info("Testing API connection...")
        
        try:
            # Validate API key
            if not validate_api_key():
                self.test_results['tests']['api_key'] = {
                    'status': 'FAILED',
                    'error': 'API key validation failed'
                }
                return False
            
            # Test API client initialization
            client = YouTubeAPIClient()
            
            # Test a simple API call
            response = client.service.search().list(
                part='snippet',
                q='test',
                type='video',
                maxResults=1
            ).execute()
            
            if 'items' in response:
                self.test_results['tests']['api_connection'] = {
                    'status': 'PASSED',
                    'quota_used': client.quota_used,
                    'response_items': len(response['items'])
                }
                logger.info("✅ API connection test passed")
                return True
            else:
                self.test_results['tests']['api_connection'] = {
                    'status': 'FAILED',
                    'error': 'No items in API response'
                }
                return False
                
        except Exception as e:
            self.test_results['tests']['api_connection'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            logger.error(f"❌ API connection test failed: {e}")
            return False
    
    def test_channel_data_collection(self) -> bool:
        """Test channel data collection functionality"""
        logger.info("Testing channel data collection...")
        
        try:
            # Get a test channel ID
            test_channel_ids = []
            for category_channels in SRI_LANKAN_CHANNELS.values():
                test_channel_ids.extend(list(category_channels.keys())[:2])
                if len(test_channel_ids) >= 3:
                    break
            
            if not test_channel_ids:
                self.test_results['tests']['channel_collection'] = {
                    'status': 'FAILED',
                    'error': 'No test channel IDs available'
                }
                return False
            
            # Test video collection
            collector = VideoCollector()
            videos = collector.collect_videos_from_channels(test_channel_ids[:2], max_videos=5)
            
            if videos:
                self.test_results['tests']['channel_collection'] = {
                    'status': 'PASSED',
                    'channels_tested': len(test_channel_ids[:2]),
                    'videos_collected': len(videos),
                    'quota_used': collector.client.quota_used
                }
                logger.info(f"✅ Channel collection test passed - collected {len(videos)} videos")
                return True
            else:
                self.test_results['tests']['channel_collection'] = {
                    'status': 'FAILED',
                    'error': 'No videos collected'
                }
                return False
                
        except Exception as e:
            self.test_results['tests']['channel_collection'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            logger.error(f"❌ Channel collection test failed: {e}")
            return False
    
    def test_video_metadata_extraction(self) -> bool:
        """Test video metadata extraction"""
        logger.info("Testing video metadata extraction...")
        
        try:
            # Use a known YouTube video ID for testing
            test_video_id = 'dQw4w9WgXcQ'  # Rick Astley - Never Gonna Give You Up
            
            client = YouTubeAPIClient()
            
            # Get video details
            response = client.service.videos().list(
                part='snippet,statistics,contentDetails',
                id=test_video_id
            ).execute()
            
            if response.get('items'):
                video = response['items'][0]
                
                # Check required fields
                required_fields = ['snippet', 'statistics', 'contentDetails']
                missing_fields = [field for field in required_fields if field not in video]
                
                if not missing_fields:
                    self.test_results['tests']['metadata_extraction'] = {
                        'status': 'PASSED',
                        'video_id': test_video_id,
                        'title': video['snippet']['title'],
                        'view_count': video['statistics'].get('viewCount', 0),
                        'quota_used': client.quota_used
                    }
                    logger.info("✅ Metadata extraction test passed")
                    return True
                else:
                    self.test_results['tests']['metadata_extraction'] = {
                        'status': 'FAILED',
                        'error': f'Missing fields: {missing_fields}'
                    }
                    return False
            else:
                self.test_results['tests']['metadata_extraction'] = {
                    'status': 'FAILED',
                    'error': 'No video data returned'
                }
                return False
                
        except Exception as e:
            self.test_results['tests']['metadata_extraction'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            logger.error(f"❌ Metadata extraction test failed: {e}")
            return False
    
    def test_data_processing(self) -> bool:
        """Test data processing and feature engineering"""
        logger.info("Testing data processing...")
        
        try:
            # Create sample data for testing
            sample_data = [
                {
                    'video_id': 'test_1',
                    'title': 'Test Video 1',
                    'description': 'This is a test video description',
                    'published_at': '2024-01-01T12:00:00Z',
                    'view_count': 1000,
                    'like_count': 50,
                    'comment_count': 10,
                    'duration_seconds': 300,
                    'channel_id': 'test_channel_1',
                    'channel_title': 'Test Channel',
                    'category_id': '22'
                },
                {
                    'video_id': 'test_2',
                    'title': 'Another Test Video',
                    'description': 'Another test description',
                    'published_at': '2024-01-02T15:30:00Z',
                    'view_count': 2000,
                    'like_count': 100,
                    'comment_count': 25,
                    'duration_seconds': 600,
                    'channel_id': 'test_channel_2',
                    'channel_title': 'Another Test Channel',
                    'category_id': '24'
                }
            ]
            
            # Save sample data temporarily
            import pandas as pd
            from utils import save_to_csv
            
            temp_file = '../data/raw/test_videos.csv'
            os.makedirs('../data/raw', exist_ok=True)
            save_to_csv(sample_data, temp_file)
            
            # Test data processing
            processor = DataProcessor()
            processor.raw_videos = pd.DataFrame(sample_data)
            
            # Test basic feature engineering
            df = processor.engineer_basic_features(processor.raw_videos.copy())
            
            # Check if features were created
            expected_features = ['title_length', 'engagement_ratio', 'duration_minutes']
            missing_features = [f for f in expected_features if f not in df.columns]
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if not missing_features:
                self.test_results['tests']['data_processing'] = {
                    'status': 'PASSED',
                    'features_created': len(df.columns) - len(sample_data[0]),
                    'sample_features': list(df.columns)[:10]
                }
                logger.info("✅ Data processing test passed")
                return True
            else:
                self.test_results['tests']['data_processing'] = {
                    'status': 'FAILED',
                    'error': f'Missing features: {missing_features}'
                }
                return False
                
        except Exception as e:
            self.test_results['tests']['data_processing'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            logger.error(f"❌ Data processing test failed: {e}")
            return False
    
    def test_file_operations(self) -> bool:
        """Test file I/O operations"""
        logger.info("Testing file operations...")
        
        try:
            from utils import save_to_csv, load_from_csv
            
            # Test data
            test_data = [
                {'id': 1, 'name': 'Test 1', 'value': 100},
                {'id': 2, 'name': 'Test 2', 'value': 200}
            ]
            
            # Test file paths
            test_file = '../data/raw/test_file_ops.csv'
            os.makedirs('../data/raw', exist_ok=True)
            
            # Test save
            save_to_csv(test_data, test_file)
            
            if not os.path.exists(test_file):
                self.test_results['tests']['file_operations'] = {
                    'status': 'FAILED',
                    'error': 'File was not created'
                }
                return False
            
            # Test load
            loaded_data = load_from_csv(test_file)
            
            # Clean up
            os.remove(test_file)
            
            if len(loaded_data) == len(test_data):
                self.test_results['tests']['file_operations'] = {
                    'status': 'PASSED',
                    'records_saved': len(test_data),
                    'records_loaded': len(loaded_data)
                }
                logger.info("✅ File operations test passed")
                return True
            else:
                self.test_results['tests']['file_operations'] = {
                    'status': 'FAILED',
                    'error': 'Data mismatch after load'
                }
                return False
                
        except Exception as e:
            self.test_results['tests']['file_operations'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            logger.error(f"❌ File operations test failed: {e}")
            return False
    
    def test_directory_structure(self) -> bool:
        """Test that required directories exist or can be created"""
        logger.info("Testing directory structure...")
        
        try:
            required_dirs = [
                '../data',
                '../data/raw',
                '../data/processed',
                '../data/snapshots',
                '../data/logs'
            ]
            
            created_dirs = []
            for directory in required_dirs:
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                    created_dirs.append(directory)
            
            # Verify all directories exist
            missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
            
            if not missing_dirs:
                self.test_results['tests']['directory_structure'] = {
                    'status': 'PASSED',
                    'required_dirs': len(required_dirs),
                    'created_dirs': created_dirs
                }
                logger.info("✅ Directory structure test passed")
                return True
            else:
                self.test_results['tests']['directory_structure'] = {
                    'status': 'FAILED',
                    'error': f'Missing directories: {missing_dirs}'
                }
                return False
                
        except Exception as e:
            self.test_results['tests']['directory_structure'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            logger.error(f"❌ Directory structure test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all integration tests"""
        logger.info("🚀 Starting integration tests...")
        
        tests = [
            ('Directory Structure', self.test_directory_structure),
            ('File Operations', self.test_file_operations),
            ('API Connection', self.test_api_connection),
            ('Video Metadata Extraction', self.test_video_metadata_extraction),
            ('Data Processing', self.test_data_processing),
            ('Channel Data Collection', self.test_channel_data_collection)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"Running test: {test_name}")
            try:
                if test_func():
                    passed_tests += 1
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
        
        # Calculate overall status
        success_rate = passed_tests / total_tests
        if success_rate == 1.0:
            self.test_results['overall_status'] = 'ALL_PASSED'
        elif success_rate >= 0.8:
            self.test_results['overall_status'] = 'MOSTLY_PASSED'
        elif success_rate >= 0.5:
            self.test_results['overall_status'] = 'PARTIALLY_PASSED'
        else:
            self.test_results['overall_status'] = 'MOSTLY_FAILED'
        
        self.test_results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': success_rate
        }
        
        return self.test_results
    
    def save_test_results(self, output_file: str = '../data/logs/integration_test_results.json'):
        """Save test results to file"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Test results saved to {output_file}")
    
    def print_summary(self):
        """Print test summary"""
        summary = self.test_results.get('summary', {})
        
        print("\n" + "="*60)
        print("🧪 INTEGRATION TEST SUMMARY")
        print("="*60)
        print(f"Overall Status: {self.test_results['overall_status']}")
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Passed: {summary.get('passed_tests', 0)}")
        print(f"Failed: {summary.get('failed_tests', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1%}")
        print("="*60)
        
        # Print individual test results
        for test_name, result in self.test_results['tests'].items():
            status_icon = "✅" if result['status'] == 'PASSED' else "❌"
            print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result['status']}")
            if result['status'] == 'FAILED' and 'error' in result:
                print(f"   Error: {result['error']}")
        
        print("="*60)

def main():
    """Main function for running integration tests"""
    logger.info("Starting YouTube Data Collection System Integration Tests")
    
    try:
        tester = IntegrationTester()
        results = tester.run_all_tests()
        
        # Save results
        tester.save_test_results()
        
        # Print summary
        tester.print_summary()
        
        # Exit with appropriate code
        if results['overall_status'] in ['ALL_PASSED', 'MOSTLY_PASSED']:
            logger.info("🎉 Integration tests completed successfully!")
            sys.exit(0)
        else:
            logger.error("⚠️ Some integration tests failed. Please check the results.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Integration test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
