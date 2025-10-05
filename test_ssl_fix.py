"""
Test SSL certificate fix for live data page
"""
import requests
import urllib3

# Disable SSL certificate verification and suppress warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_fpl_connection():
    """Test FPL API connection with SSL verification disabled"""
    try:
        base_url = "https://fantasy.premierleague.com/api"
        
        print("🔍 Testing FPL API connection with SSL verification disabled...")
        
        # Test bootstrap endpoint
        response = requests.get(f"{base_url}/bootstrap-static/", timeout=15, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            players_count = len(data.get('elements', []))
            teams_count = len(data.get('teams', []))
            
            print("✅ SUCCESS: FPL API connection working!")
            print(f"📊 Data retrieved: {players_count} players, {teams_count} teams")
            print("🔧 SSL certificate verification is now disabled")
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL Error (should not happen now): {e}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    test_fpl_connection()
