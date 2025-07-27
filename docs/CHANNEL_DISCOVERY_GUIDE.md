# 🚀 Enhanced YouTube Channel Discovery System Guide

## Overview

The Enhanced YouTube Channel Discovery System is a powerful tool that can discover unlimited Sri Lankan YouTube channels using multiple intelligent strategies. This system has been designed to scale from discovering a few dozen channels to potentially thousands of channels across all content categories.

## 🎯 Key Features

### 1. **Intelligent Keyword Expansion Engine**
- **Base Keywords**: Starts with 20 core Sri Lankan keywords
- **Expansion Methods**:
  - **YouTube Autocomplete**: Real search suggestions from YouTube
  - **Geographic Expansion**: All Sri Lankan locations and landmarks
  - **Trending Terms**: Integration with Google Trends for Sri Lanka
  - **Template Patterns**: Smart keyword combinations
- **Validation**: Tests keywords against YouTube API for actual results

### 2. **Multi-Strategy Discovery System**
- **Keyword-based Search**: Uses expanded keyword database
- **Popular Videos Discovery**: Finds channels from trending Sri Lankan content
- **Related Channel Discovery**: Analyzes comments and interactions
- **Location-based Search**: Targets Sri Lankan region specifically

### 3. **Advanced Channel Scoring & Filtering**
- **Sri Lankan Relevance Score**: Intelligent scoring based on multiple indicators
- **Automatic Categorization**: Maps channels to YouTube categories
- **Duplicate Prevention**: Avoids re-discovering existing channels

### 4. **API Management & Scalability**
- **Multiple API Key Support**: Automatic rotation when quotas are reached
- **Rate Limiting Protection**: Smart delays and error handling
- **Quota Tracking**: Monitors usage across all API keys

## 📋 Prerequisites

### Required Packages
```bash
pip install google-api-python-client python-dotenv requests pytrends
```

### API Keys Setup
1. **Primary API Key**: Set `YOUTUBE_API_KEY` in your `.env` file
2. **Additional Keys** (optional): Set `YOUTUBE_API_KEY_1`, `YOUTUBE_API_KEY_2`, etc.

Example `.env` file:
```env
YOUTUBE_API_KEY=your_primary_api_key_here
YOUTUBE_API_KEY_1=your_second_api_key_here
YOUTUBE_API_KEY_2=your_third_api_key_here
```

## 🛠️ Usage Examples

### 1. **Intelligent Keyword Expansion** (Recommended)
```bash
python scripts/collect_channels.py --expand-keywords --max-results 1000
```
This will:
- Expand from 20 base keywords to 500+ keywords
- Validate keywords against YouTube API
- Search for channels using validated keywords
- Save results with detailed metadata

### 2. **Basic Keyword Search**
```bash
python scripts/collect_channels.py --keywords "sri lanka" "sinhala" "tamil" --max-results 100
```

### 3. **Location-based Comprehensive Discovery**
```bash
python scripts/collect_channels.py --location-search --max-results 500
```

### 4. **Validate Existing Channels**
```bash
python scripts/collect_channels.py --validate-existing
```

### 5. **Custom Output Directory**
```bash
python scripts/collect_channels.py --expand-keywords --output-dir "custom/path" --max-results 200
```

## 📊 Output Files

The system generates several output files:

### 1. **discovered_channels.json**
```json
{
  "News & Politics": {
    "Channel Name 1": "UCxxxxxxxxx",
    "Channel Name 2": "UCyyyyyyyyy"
  },
  "Music": {
    "Music Channel 1": "UCzzzzzzzzz"
  }
}
```

### 2. **detailed_channels_[timestamp].json**
```json
[
  {
    "channel_id": "UCxxxxxxxxx",
    "title": "Channel Name",
    "description": "Channel description...",
    "subscriber_count": 50000,
    "video_count": 200,
    "view_count": 1000000,
    "country": "LK",
    "sri_lankan_score": 8.5,
    "category": "News & Politics",
    "discovered_at": "2025-01-15T10:30:00"
  }
]
```

### 3. **expanded_keywords_[timestamp].json**
```json
{
  "base_keywords": ["sri lanka", "sinhala", ...],
  "expanded_keywords": ["colombo vlog", "kandy travel", ...],
  "validated_keywords": ["sri lanka news", "sinhala songs", ...],
  "total_count": 566
}
```

## 🚨 API Quota Management

### Understanding YouTube API Quotas
- **Daily Limit**: 10,000 units per API key per day
- **Search Operation**: 100 units per request
- **Channel Details**: 1 unit per request
- **Video Details**: 1 unit per request

### When API Quotas Are Exhausted

#### **Immediate Solutions:**
1. **Wait for Reset**: Quotas reset at midnight Pacific Time
2. **Use Additional API Keys**: Add more keys to your `.env` file
3. **Use Offline Mode**: Work with previously generated keyword files

#### **Working with Existing Data:**
```bash
# Use previously expanded keywords without API validation
python scripts/collect_channels.py --keywords $(cat data/raw/expanded_keywords_*.json | jq -r '.validated_keywords[]' | head -20)
```

#### **Optimize API Usage:**
```bash
# Use smaller batch sizes to conserve quota
python scripts/collect_channels.py --expand-keywords --max-results 50
```

### **Getting Additional API Keys:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or use existing
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add to your `.env` file as `YOUTUBE_API_KEY_1`, `YOUTUBE_API_KEY_2`, etc.

## 📈 Performance Optimization

### **Recommended Workflow:**

#### **Phase 1: Keyword Expansion** (Low API Usage)
```bash
python scripts/collect_channels.py --expand-keywords --max-results 100
```
- Generates 500+ keywords
- Uses ~100 API units for validation
- Creates reusable keyword database

#### **Phase 2: Channel Discovery** (High API Usage)
```bash
python scripts/collect_channels.py --location-search --max-results 1000
```
- Uses expanded keywords from Phase 1
- Discovers channels using multiple methods
- Uses ~500-1000 API units

#### **Phase 3: Validation & Categorization** (Medium API Usage)
```bash
python scripts/collect_channels.py --validate-existing
```
- Validates discovered channels
- Categorizes channels by content type
- Uses ~200-500 API units

### **Batch Processing Strategy:**
```bash
# Day 1: Keyword expansion
python scripts/collect_channels.py --expand-keywords --max-results 200

# Day 2: Channel discovery
python scripts/collect_channels.py --location-search --max-results 500

# Day 3: Validation and cleanup
python scripts/collect_channels.py --validate-existing
```

## 🔍 Advanced Features

### **Sri Lankan Relevance Scoring**
The system uses intelligent scoring based on:
- **High-value indicators** (3.0 points): "sri lanka", "srilanka", "ceylon", "lanka"
- **Geographic markers** (2.0 points): "colombo", "kandy", "galle", etc.
- **Language indicators** (2.5 points): "sinhala", "tamil"
- **Cultural terms** (1.5 points): "ape amma", "lankan", etc.
- **Country code** (5.0 points): Channel country = "LK"

### **Automatic Categorization**
Channels are automatically categorized into:
- News & Politics
- Music
- Entertainment
- Education
- Sports
- Gaming
- Travel & Events
- Howto & Style
- Science & Technology
- People & Blogs (default)

### **Discovery Methods**
1. **Keyword Search**: Direct search using expanded keywords
2. **Popular Videos**: Channels from trending Sri Lankan content
3. **Related Channels**: Found through comment analysis
4. **Trending Search**: Recent viral content creators

## 🐛 Troubleshooting

### **Common Issues:**

#### **"All API keys exhausted" Error**
```bash
# Solution 1: Add more API keys to .env
YOUTUBE_API_KEY_3=your_new_api_key

# Solution 2: Wait for quota reset (midnight PT)
# Solution 3: Use smaller batch sizes
python scripts/collect_channels.py --keywords "sri lanka" --max-results 10
```

#### **"No channels found" Result**
```bash
# Check if keywords are too specific
python scripts/collect_channels.py --keywords "lanka" "colombo" --max-results 50

# Try location-based search instead
python scripts/collect_channels.py --location-search --max-results 100
```

#### **"Optional packages not installed" Warning**
```bash
pip install requests pytrends
```

### **Debugging Mode**
```bash
# Enable detailed logging
export PYTHONPATH=./scripts
python scripts/collect_channels.py --expand-keywords --max-results 10 -v
```

## 📊 Expected Results

### **Keyword Expansion Results:**
- **Base Keywords**: 20
- **Expanded Keywords**: 500-600
- **Validated Keywords**: 100-200
- **Expansion Ratio**: 2,800% increase

### **Channel Discovery Results:**
- **Small Run** (100 max): 20-50 channels
- **Medium Run** (500 max): 100-300 channels  
- **Large Run** (1000+ max): 300-1000+ channels

### **API Usage Estimates:**
- **Keyword Expansion**: 100-200 units
- **Channel Discovery**: 500-1500 units
- **Channel Validation**: 200-500 units
- **Total for Full Run**: 800-2200 units

## 🎯 Best Practices

1. **Start Small**: Begin with `--max-results 50` to test
2. **Use Multiple Keys**: Set up 3-5 API keys for continuous operation
3. **Monitor Quotas**: Check API usage in Google Cloud Console
4. **Save Results**: Always backup generated keyword and channel files
5. **Incremental Discovery**: Run discovery in phases over multiple days
6. **Validate Results**: Review discovered channels for quality

## 📞 Support

If you encounter issues:
1. Check the logs in `data/logs/` directory
2. Verify API keys are valid and have quota remaining
3. Ensure all required packages are installed
4. Review the troubleshooting section above

The Enhanced Channel Discovery System transforms the project from discovering dozens of channels to potentially thousands, providing a comprehensive foundation for building accurate viewership forecasting models specific to Sri Lankan audiences.
