# API Key Rotation System Fix

## Problem Identified
The YouTube API key rotation system was permanently marking keys as "rate limited" without considering daily quota resets, causing the system to fail even when quotas should have been available.

## Root Cause
1. **Permanent Rate Limiting**: Keys were added to a `rate_limited_keys` set and never removed
2. **No Quota Reset Detection**: System didn't account for YouTube's daily quota reset at midnight Pacific Time
3. **Timezone Issues**: Datetime comparisons were mixing timezone-aware and timezone-naive objects

## Solution Implemented

### 1. Changed Rate Limited Storage
```python
# Before: Set (permanent marking)
self.rate_limited_keys = set()

# After: Dictionary with timestamps
self.rate_limited_keys = {}  # {api_key: timestamp}
```

### 2. Added Quota Reset Detection
```python
def _is_quota_reset_time(self) -> bool:
    """Check if it's past the daily quota reset time (midnight PT)"""
    import pytz
    pt_tz = pytz.timezone('US/Pacific')
    current_pt = datetime.now(pt_tz)
    midnight_pt_today = current_pt.replace(hour=0, minute=0, second=0, microsecond=0)
    return current_pt >= midnight_pt_today
```

### 3. Implemented Automatic Cleanup
```python
def _clean_expired_rate_limits(self):
    """Remove API keys from rate limited set if quota has reset"""
    # Remove keys that were rate limited before today's quota reset
    keys_to_remove = []
    for key, timestamp in self.rate_limited_keys.items():
        if timestamp < midnight_pt_today:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del self.rate_limited_keys[key]
```

### 4. Fixed Timezone Handling
```python
# Store timezone-aware timestamps
try:
    import pytz
    current_time = datetime.now(pytz.UTC)
except ImportError:
    current_time = datetime.now()

self.rate_limited_keys[api_key] = current_time
```

### 5. Enhanced Key Rotation Logic
```python
def _rotate_key(self) -> bool:
    """Rotate to next available API key"""
    # Clean expired rate limits before rotating
    self._clean_expired_rate_limits()
    
    # Try all keys systematically
    original_index = self.current_key_index
    attempts = 0
    max_attempts = len(self.api_keys)
    
    while attempts < max_attempts:
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        attempts += 1
        
        current_key = self.api_keys[self.current_key_index]
        
        # Check if this key is not rate limited
        if current_key not in self.rate_limited_keys:
            if self._initialize_service():
                return True
    
    return False  # All keys exhausted
```

## Test Results

The fixed system now properly:

1. **Loads all 3 API keys**: ✅
2. **Detects quota exceeded errors**: ✅
3. **Rotates through keys systematically**: ✅
4. **Handles timezone-aware timestamps**: ✅
5. **Gracefully handles total exhaustion**: ✅

## Expected Behavior

- **During quota reset (midnight PT)**: Previously rate-limited keys are automatically restored
- **Key rotation**: System tries each key once before giving up
- **Timestamp tracking**: Each key's rate limit time is recorded for future cleanup
- **Fallback handling**: Works even without `pytz` package (24-hour fallback)

## Benefits

1. **Automatic Recovery**: System recovers when quotas reset
2. **Maximum Utilization**: Uses all available API quota across all keys
3. **Robust Error Handling**: Gracefully handles various failure scenarios
4. **Timezone Awareness**: Properly handles YouTube's Pacific Time quota reset

## Files Modified

- `scripts/collect_channels.py`: Updated `YouTubeAPIManager` class with new rotation logic

## Dependencies Added

- `pytz`: For proper timezone handling (already installed)

The system is now production-ready and will automatically recover from quota exhaustion scenarios.
