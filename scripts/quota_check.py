import os
import sys
import requests
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load .env using relative path
script_dir = Path(__file__).parent
env_path = (script_dir / ".." / ".env").resolve()
load_dotenv(dotenv_path=env_path)

def load_api_keys():
    """Load all API keys from environment variables."""
    keys = []
    base_key = os.getenv("YOUTUBE_API_KEY")
    if base_key:
        keys.append(base_key)

    i = 1
    while True:
        key = os.getenv(f"YOUTUBE_API_KEY_{i}")
        if key:
            keys.append(key)
            i += 1
        else:
            break

    return keys

def check_lightweight_quota(api_key, index):
    """Check 1-unit quota (videos.list)."""
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "id",
        "id": "dQw4w9WgXcQ",
        "key": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            print(f"[LIGHT ✅] API Key {index} ({api_key[:10]}...) has 1-unit quota.")
            return True
        else:
            reason = response.json().get("error", {}).get("errors", [{}])[0].get("reason", "Unknown error")
            print(f"[LIGHT ❌] API Key {index} ({api_key[:10]}...) error: {reason}")
            return False
    except Exception as e:
        print(f"[LIGHT ⚠️] API Key {index} ({api_key[:10]}...) exception: {e}")
        return False

def check_search_quota(api_key, index):
    """Try a single 100-unit search.list call."""
    try:
        service = build('youtube', 'v3', developerKey=api_key)
        service.search().list(
            part='snippet',
            q='test',
            type='channel',
            regionCode='LK',
            maxResults=1,
            order='relevance'
        ).execute()

        print(f"[SEARCH ✅] API Key {index} ({api_key[:10]}...) has 100-unit quota.")
        return True
    except HttpError as e:
        if e.resp.status == 403:
            reason = e.error_details[0].get('reason', 'unknown') if e.error_details else 'unknown'
            if 'quotaExceeded' in reason:
                print(f"[SEARCH ❌] API Key {index} ({api_key[:10]}...) quota exceeded.")
            else:
                print(f"[SEARCH ❌] API Key {index} ({api_key[:10]}...) error: {reason}")
        else:
            print(f"[SEARCH ❌] API Key {index} ({api_key[:10]}...) HTTP {e.resp.status}: {e}")
        return False
    except Exception as e:
        print(f"[SEARCH ⚠️] API Key {index} ({api_key[:10]}...) exception: {e}")
        return False

def test_multiple_searches(api_key, key_index, max_tests=10):
    """Test how many 100-unit searches a key can handle."""
    try:
        service = build('youtube', 'v3', developerKey=api_key)
        successful = 0

        for i in range(max_tests):
            try:
                service.search().list(
                    part='snippet',
                    q=f'test{i}',
                    type='channel',
                    regionCode='LK',
                    maxResults=1,
                    order='relevance'
                ).execute()

                successful += 1
                print(f"  ✅ Search {i+1}: Success")

            except HttpError as e:
                if e.resp.status == 403 and 'quotaExceeded' in str(e):
                    print(f"  ❌ Search {i+1}: Quota exceeded")
                    break
                else:
                    print(f"  ❌ Search {i+1}: Error - {e}")
                    break
            except Exception as e:
                print(f"  ❌ Search {i+1}: Exception - {e}")
                break

        return successful
    except Exception as e:
        print(f"  💥 Failed to initialize service: {e}")
        return 0

def main():
    print("📦 Checking YouTube API Key Quotas")
    print("=" * 60)
    api_keys = load_api_keys()

    if not api_keys:
        print("❌ No API keys found in .env")
        return

    total_capacity = 0
    light_ok = 0
    search_ok = 0

    for i, key in enumerate(api_keys, 1):
        print(f"\n🔑 API Key {i} ({key[:10]}...):")

        if check_lightweight_quota(key, i):
            light_ok += 1

        if check_search_quota(key, i):
            search_ok += 1

        print("🔁 Estimating remaining search capacity...")
        success_count = test_multiple_searches(key, i, max_tests=10)
        total_capacity += success_count

        if success_count == 0:
            print(f"  📊 Result: No quota remaining")
        else:
            estimated = success_count * 100
            print(f"  📊 Result: ~{estimated} units remaining ({success_count} searches)")

    print("\n📊 Summary")
    print("=" * 60)
    print(f"✅ Lightweight check passed: {light_ok}/{len(api_keys)}")
    print(f"🔍 Search check passed: {search_ok}/{len(api_keys)}")
    print(f"📈 Estimated total remaining search capacity: ~{total_capacity * 100} units")
    print(f"🎯 Estimated searches possible: {total_capacity}")

    if total_capacity == 0:
        print("⚠️  All keys are exhausted for search operations")
        print("🕐 Quotas reset at 1:30 PM Sri Lanka time (midnight Pacific Time)")
    elif total_capacity < 10:
        print("⚠️  Very low quota remaining – consider waiting for reset")
    else:
        print("✅ Sufficient quota available for channel discovery")

if __name__ == "__main__":
    main()
