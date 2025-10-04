"""
Test script to simulate My FPL Team page functionality with team ID 1437667
"""
import sys
import os
import pandas as pd
import streamlit as st
from unittest.mock import MagicMock

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Mock Streamlit session state
class MockSessionState:
    def __init__(self):
        self._state = {}
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def __getitem__(self, key):
        return self._state[key]
    
    def __setitem__(self, key, value):
        self._state[key] = value
    
    def __contains__(self, key):
        return key in self._state
    
    def __delitem__(self, key):
        if key in self._state:
            del self._state[key]

# Mock Streamlit functions
def mock_streamlit():
    st.header = lambda x: print(f"HEADER: {x}")
    st.write = lambda x: print(f"WRITE: {x}")
    st.divider = lambda: print("DIVIDER: ---")
    st.spinner = lambda x: MockContext(f"SPINNER: {x}")
    st.success = lambda x: print(f"SUCCESS: {x}")
    st.error = lambda x: print(f"ERROR: {x}")
    st.warning = lambda x: print(f"WARNING: {x}")
    st.info = lambda x: print(f"INFO: {x}")
    st.text_input = lambda label, value="", placeholder="", help="": f"mock_input_{label}"
    st.selectbox = lambda label, options, index=0, help="": options[index] if options else None
    st.button = lambda label, type=None: False  # Don't trigger button for test
    st.expander = lambda label, expanded=False: MockContext(f"EXPANDER: {label}")
    st.columns = lambda x: [MockContext(f"COL_{i}") for i in range(x)]
    st.metric = lambda label, value: print(f"METRIC: {label} = {value}")
    st.subheader = lambda x: print(f"SUBHEADER: {x}")
    st.rerun = lambda: print("RERUN CALLED")
    st.session_state = MockSessionState()

class MockContext:
    def __init__(self, name):
        self.name = name
    
    def __enter__(self):
        print(f"ENTER: {self.name}")
        return self
    
    def __exit__(self, *args):
        print(f"EXIT: {self.name}")

def test_my_team_page():
    """Test the My Team Page functionality"""
    print("=" * 60)
    print("TESTING MY FPL TEAM PAGE WITH ID: 1437667")
    print("=" * 60)
    
    # Mock Streamlit
    mock_streamlit()
    
    try:
        # Import the page class
        from views.my_team_page import MyTeamPage
        
        print("\n1. Creating MyTeamPage instance...")
        page = MyTeamPage()
        print("✅ MyTeamPage instance created successfully")
        
        print("\n2. Testing initial render (no team loaded)...")
        page.render()
        print("✅ Initial render completed")
        
        print("\n3. Testing data service directly...")
        team_id = "1437667"
        
        # Try multiple gameweeks to find one with picks data
        successful_gw = None
        team_data = None
        
        for gameweek in [8, 7, 6, 5, 4, 3, 2, 1]:  # Try recent gameweeks
            try:
                print(f"   Trying GW {gameweek} for team ID: {team_id}")
                test_data = page.data_service.load_team_data(team_id, gameweek)
                
                if test_data and test_data.get('picks'):
                    team_data = test_data
                    successful_gw = gameweek
                    print(f"✅ Found squad data in gameweek {gameweek}!")
                    break
                else:
                    print(f"   GW {gameweek}: No picks data")
                    
            except Exception as e:
                print(f"   GW {gameweek}: Error - {str(e)}")
        
        if team_data and successful_gw:
            print(f"\n✅ Team data loaded successfully for GW {successful_gw}!")
            print(f"   Team Name: {team_data.get('entry_name', 'Unknown')}")
            print(f"   Overall Points: {team_data.get('summary_overall_points', 'N/A')}")
            print(f"   Overall Rank: {team_data.get('summary_overall_rank', 'N/A')}")
            print(f"   Squad Size: {len(team_data.get('picks', []))}")
            print(f"   Team Value: £{team_data.get('value', 0)/10:.1f}m")
                
            # Test setting session state
            st.session_state.my_team_data = team_data
            st.session_state.my_team_id = team_id
            st.session_state.my_team_loaded = True
            
            print("\n4. Testing render with team data loaded...")
            page.render()
            print("✅ Render with team data completed")
            
        else:
            print("❌ No valid team data found in any recent gameweeks")
        
        print("\n   Testing error handling...")
        try:
            # Test with invalid team ID
            invalid_data = page.data_service.load_team_data("999999999", 1)
            print(f"   Invalid team test: {invalid_data is not None}")
        except Exception as e:
            print(f"   Invalid team handled correctly: {type(e).__name__}")
        
        print("\n5. Testing FPL data loading...")
        try:
            players_df, teams_df = page.data_service.load_fpl_data()
            print(f"✅ Player data loaded: {len(players_df)} players")
            print(f"✅ Team data loaded: {len(teams_df)} teams")
        except Exception as e:
            print(f"❌ Error loading FPL data: {str(e)}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Error testing page: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_my_team_page()
