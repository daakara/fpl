"""
Simple My FPL Team UI Test
This will help diagnose the blank UI issue
"""

import streamlit as st
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

def main():
    st.set_page_config(
        page_title="🏆 My FPL Team",
        page_icon="⚽",
        layout="wide"
    )
    
    st.title("🏆 My FPL Team - Debug Version")
    
    # Show what's happening
    st.write("**🔍 Debugging the blank UI issue...**")
    
    try:
        # Import and test the original page
        from views.my_team_page import MyTeamPage
        st.success("✅ Successfully imported MyTeamPage")
        
        # Initialize page
        my_team_page = MyTeamPage()
        st.success("✅ Page initialized")
        
        # Check session state
        st.write("**📊 Current Session State:**")
        st.write(f"- my_team_loaded: {st.session_state.get('my_team_loaded', False)}")
        st.write(f"- data_loaded: {st.session_state.get('data_loaded', False)}")
        st.write(f"- my_team_id: {st.session_state.get('my_team_id', 'None')}")
        
        # Manual team input section (what should be showing)
        st.divider()
        st.subheader("📥 Import Your FPL Team")
        st.info("👋 Enter your FPL Team ID below to analyze your team performance!")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            team_id = st.text_input(
                "Enter your FPL Team ID:",
                placeholder="e.g., 1437667",
                help="Find your team ID in your FPL team URL"
            )
            
            gameweeks = list(range(1, 39))
            selected_gw = st.selectbox(
                "Select Gameweek:",
                gameweeks,
                index=7,  # Default to GW 8
                help="Choose which gameweek's team to analyze"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            
            if st.button("🔄 Load My Team", type="primary", use_container_width=True):
                if team_id and team_id.strip():
                    st.success(f"✅ Loading team ID: {team_id} for GW {selected_gw}")
                    
                    # Set session state to simulate loading
                    st.session_state.my_team_id = team_id
                    st.session_state.my_team_gameweek = selected_gw
                    st.session_state.my_team_loaded = True
                    
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter a valid team ID")
            
            if st.button("🧪 Quick Test", help="Test with team ID 1437667"):
                st.session_state.my_team_id = "1437667"
                st.session_state.my_team_gameweek = 7
                st.session_state.my_team_loaded = True
                st.success("✅ Test team loaded!")
                st.rerun()
        
        # Instructions
        with st.expander("💡 How to find your Team ID", expanded=False):
            st.markdown("""
            **Step 1:** Go to the official FPL website and log in
            
            **Step 2:** Navigate to your team page
            
            **Step 3:** Look at the URL - it will look like:
            `https://fantasy.premierleague.com/entry/1234567/event/15`
            
            **Step 4:** Your Team ID is the number after `/entry/` (in this example: 1234567)
            
            **Note:** Your team must be public for this to work.
            """)
        
        # If team is "loaded", show dashboard
        if st.session_state.get('my_team_loaded', False):
            st.divider()
            st.subheader("🎉 Team Dashboard")
            
            team_id = st.session_state.get('my_team_id', 'Unknown')
            gw = st.session_state.get('my_team_gameweek', 'Unknown')
            
            st.success(f"✅ Team ID {team_id} loaded for Gameweek {gw}")
            
            # Mock dashboard
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Overall Rank", "892,456")
            with col2:
                st.metric("Total Points", "1,156")
            with col3:
                st.metric("GW Points", "67")
            with col4:
                st.metric("Team Value", "£102.0m")
            
            st.info("🎨 This is a working UI! The original page might have rendering issues.")
            
            if st.button("🔄 Load Different Team"):
                # Reset session state
                st.session_state.my_team_loaded = False
                st.session_state.my_team_id = None
                st.session_state.my_team_gameweek = None
                st.rerun()
        
    except ImportError as e:
        st.error(f"❌ Import Error: {e}")
        st.write("Cannot import the My Team page. Let's check what files exist:")
        
        if os.path.exists('views'):
            files = os.listdir('views')
            st.write(f"Files in views/: {files}")
        else:
            st.write("❌ 'views' directory not found")
    
    except Exception as e:
        st.error(f"❌ Unexpected Error: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
