#!/usr/bin/env python3
"""
Quick UI Test for My FPL Team Page
Run with: streamlit run test_my_team_ui.py
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
        page_title="🏆 My FPL Team - UI Test",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏆 My FPL Team - UI Test")
    
    try:
        # Try to import the rebuilt page from views folder
        from views.my_team_page_rebuilt import MyTeamPageRebuilt
        st.success("✅ Successfully imported MyTeamPageRebuilt from views folder")
        
        # Initialize the page
        my_team_page = MyTeamPageRebuilt()
        st.success("✅ Page initialized successfully")
        
        # Show version info
        version = getattr(my_team_page, 'version', 'Unknown')
        title = getattr(my_team_page, 'title', 'Unknown')
        st.info(f"📊 Version: {version} | Title: {title}")
        
        # Try to render the page
        st.divider()
        st.subheader("🎨 Page Rendering Test")
        
        # Call the page render method
        my_team_page.render()
        
    except ImportError as e:
        st.error(f"❌ Import Error: {e}")
        st.write("Let's try alternative imports...")
        
        # Try original page
        try:
            from views.my_team_page import MyTeamPage
            st.warning("⚠️ Using original MyTeamPage instead")
            
            my_team_page = MyTeamPage()
            st.success("✅ Original page initialized")
            
            # Render original page
            st.divider()
            st.subheader("🎨 Original Page Rendering")
            my_team_page.render()
            
        except ImportError as e2:
            st.error(f"❌ Original page import also failed: {e2}")
            
            # Show manual team input as fallback
            st.divider()
            st.subheader("🔧 Manual Team Input (Fallback)")
            
            team_id = st.text_input(
                "Enter your FPL Team ID:",
                placeholder="e.g., 1437667",
                help="Find your team ID in your FPL team URL"
            )
            
            if team_id:
                if team_id.isdigit() and int(team_id) > 0:
                    st.success(f"✅ Valid team ID: {team_id}")
                    st.info("In a working version, this would load your team data...")
                else:
                    st.error("❌ Please enter a valid numeric team ID")
            
    except Exception as e:
        st.error(f"❌ Unexpected Error: {e}")
        st.write("**Error Details:**")
        st.code(str(e))
        
        # Show debug info
        st.divider()
        st.subheader("🔍 Debug Information")
        st.write(f"**Python Path:** {sys.path[:3]}...")
        st.write(f"**Working Directory:** {os.getcwd()}")
        st.write(f"**Project Root:** {project_root}")
        
        # List available files
        if os.path.exists('views'):
            views_files = os.listdir('views')
            st.write(f"**Files in views/:** {views_files}")

if __name__ == "__main__":
    main()
