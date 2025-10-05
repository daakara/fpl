#!/usr/bin/env python3
"""
FPL API Connection Diagnostic Tool
Comprehensive testing of network connectivity and API endpoints
"""

import requests
import time
import sys
import json
from datetime import datetime

def test_basic_internet():
    """Test basic internet connectivity"""
    print("🌐 Testing basic internet connectivity...")
    test_urls = [
        "https://www.google.com",
        "https://httpbin.org/get",
        "https://api.github.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} - OK")
                return True
        except Exception as e:
            print(f"❌ {url} - {e}")
    
    print("❌ No internet connectivity detected")
    return False

def test_fpl_api_endpoints():
    """Test all FPL API endpoints"""
    print("\n🏈 Testing FPL API endpoints...")
    
    base_url = "https://fantasy.premierleague.com/api"
    endpoints = {
        "bootstrap-static": "/bootstrap-static/",
        "fixtures": "/fixtures/",
        "manager-history": "/entry/1/history/",
        "live-gameweek": "/event/1/live/",
    }
    
    results = {}
    
    for name, endpoint in endpoints.items():
        try:
            print(f"Testing {name}...")
            url = f"{base_url}{endpoint}"
            
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    data_size = len(json.dumps(data))
                    print(f"✅ {name} - OK ({response_time:.2f}s, {data_size} bytes)")
                    results[name] = {"status": "success", "time": response_time, "size": data_size}
                except json.JSONDecodeError:
                    print(f"⚠️ {name} - Response not JSON")
                    results[name] = {"status": "invalid_json", "time": response_time}
            else:
                print(f"❌ {name} - HTTP {response.status_code}")
                results[name] = {"status": f"http_{response.status_code}", "time": response_time}
                
        except requests.exceptions.Timeout:
            print(f"⏰ {name} - Timeout")
            results[name] = {"status": "timeout"}
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 {name} - Connection Error: {e}")
            results[name] = {"status": "connection_error", "error": str(e)}
        except Exception as e:
            print(f"💥 {name} - Unexpected Error: {e}")
            results[name] = {"status": "error", "error": str(e)}
    
    return results

def test_network_configuration():
    """Test network and proxy configuration"""
    print("\n🔧 Testing network configuration...")
    
    # Check environment variables
    import os
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"🔍 {var}: {value}")
    
    # Test DNS resolution
    import socket
    try:
        ip = socket.gethostbyname('fantasy.premierleague.com')
        print(f"✅ DNS Resolution: fantasy.premierleague.com -> {ip}")
    except Exception as e:
        print(f"❌ DNS Resolution failed: {e}")

def test_requests_session():
    """Test with custom session configuration"""
    print("\n⚙️ Testing with enhanced session configuration...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    })
    
    # Disable SSL verification if needed
    session.verify = False
    
    try:
        response = session.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/",
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enhanced session test successful")
            print(f"📊 Data summary: {len(data.get('elements', []))} players, {len(data.get('teams', []))} teams")
            return True
        else:
            print(f"❌ Enhanced session test failed - HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Enhanced session test failed: {e}")
    
    return False

def main():
    """Run comprehensive connection diagnostic"""
    print("🔍 FPL API Connection Diagnostic Tool")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Basic internet
    if not test_basic_internet():
        print("\n🚨 DIAGNOSIS: No internet connection detected")
        print("💡 SOLUTION: Check your internet connection and try again")
        return
    
    # Test 2: Network configuration
    test_network_configuration()
    
    # Test 3: FPL API endpoints
    results = test_fpl_api_endpoints()
    
    # Test 4: Enhanced session
    enhanced_success = test_requests_session()
    
    # Summary
    print("\n📋 DIAGNOSTIC SUMMARY")
    print("=" * 30)
    
    failed_endpoints = [name for name, result in results.items() if result.get('status') != 'success']
    
    if not failed_endpoints and enhanced_success:
        print("✅ All tests passed - FPL API is accessible")
        print("💡 The connection error might be temporary or related to your application configuration")
    elif failed_endpoints:
        print(f"❌ Failed endpoints: {', '.join(failed_endpoints)}")
        print("💡 POSSIBLE SOLUTIONS:")
        print("   - Check if FPL website is down: https://fantasy.premierleague.com")
        print("   - Try using a VPN if there are regional restrictions")
        print("   - Check firewall settings")
        print("   - Wait and retry - FPL API might be temporarily unavailable")
    else:
        print("⚠️ Mixed results - some connectivity issues detected")
    
    print("\n🔧 RECOMMENDED NEXT STEPS:")
    print("1. Run this diagnostic again in a few minutes")
    print("2. Check FPL website directly in browser")
    print("3. Review application logs for more specific errors")
    print("4. Consider implementing retry logic with exponential backoff")

if __name__ == "__main__":
    main()
