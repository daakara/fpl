"""
Production Test for My FPL Team Page UI
======================================

This script launches a Streamlit app to test the My FPL Team page in a real production environment.
It will start a local server and validate the UI with team ID 1437667.
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main production test app"""
    st.set_page_config(
        page_title="My FPL Team - Production Test",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚀 My FPL Team Page - Production Test")
    st.markdown("---")
    
    # Test selection
    test_option = st.sidebar.selectbox(
        "Select Test Version:",
        ["Modular Version (Recommended)", "Original Version"]
    )
    
    # Test configuration
    st.sidebar.markdown("### Test Configuration")
    test_team_id = st.sidebar.text_input("Team ID to Test", value="1437667")
    auto_load = st.sidebar.checkbox("Auto-load team data", value=False)
    show_debug = st.sidebar.checkbox("Show debug information", value=False)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Test Status")
    
    if show_debug:
        st.sidebar.success("✅ Debug mode enabled")
        st.info("🔧 Debug mode is enabled - additional information will be shown")
    
    # Test execution
    try:
        if test_option == "Modular Version (Recommended)":
            st.success("🔄 Loading Modular My FPL Team Page...")
            test_modular_version(test_team_id, auto_load, show_debug)
        else:
            st.success("🔄 Loading Original My FPL Team Page...")
            test_original_version(test_team_id, auto_load, show_debug)
            
    except Exception as e:
        st.error(f"❌ Production test failed: {str(e)}")
        if show_debug:
            st.exception(e)

def test_modular_version(team_id, auto_load, show_debug):
    """Test the modular version in production"""
    try:
        from views.my_team_page_modular import MyTeamPage
        
        st.info("✅ Successfully imported Modular MyTeamPage")
        
        if show_debug:
            st.markdown("### 🔧 Debug Information")
            st.code(f"""
Test Configuration:
- Version: Modular
- Team ID: {team_id}
- Auto-load: {auto_load}
- Debug: {show_debug}
- Timestamp: {datetime.now()}
            """)
        
        # Initialize and render the page
        if auto_load and team_id:
            # Pre-populate session state for automatic testing
            st.session_state.test_team_id = team_id
            st.session_state.auto_test_mode = True
        
        page = MyTeamPage()
        
        st.markdown("### 🏆 My FPL Team Analysis (Production Test)")
        st.markdown("---")
        
        # Render the actual page
        page.render()
        
        # Test validation
        st.sidebar.success("✅ Modular page loaded successfully")
        
        if show_debug:
            st.sidebar.markdown("### Component Status")
            components = ['team_import', 'team_overview', 'squad_analysis', 'performance_analysis']
            for component in components:
                if hasattr(page, component):
                    st.sidebar.success(f"✅ {component}")
                else:
                    st.sidebar.error(f"❌ {component}")
        
    except Exception as e:
        st.error(f"❌ Modular version test failed: {str(e)}")
        st.sidebar.error("❌ Modular test failed")
        if show_debug:
            st.exception(e)

def test_original_version(team_id, auto_load, show_debug):
    """Test the original version in production"""
    try:
        from views.my_team_page import MyTeamPage
        
        st.info("✅ Successfully imported Original MyTeamPage")
        
        if show_debug:
            st.markdown("### 🔧 Debug Information")
            st.code(f"""
Test Configuration:
- Version: Original
- Team ID: {team_id}
- Auto-load: {auto_load}
- Debug: {show_debug}
- Timestamp: {datetime.now()}
            """)
        
        # Initialize and render the page
        if auto_load and team_id:
            st.session_state.test_team_id = team_id
            st.session_state.auto_test_mode = True
        
        page = MyTeamPage()
        
        st.markdown("### 🏆 My FPL Team Analysis (Production Test)")
        st.markdown("---")
        
        # Render the actual page
        page.render()
        
        # Test validation
        st.sidebar.success("✅ Original page loaded successfully")
        
    except Exception as e:
        st.error(f"❌ Original version test failed: {str(e)}")
        st.sidebar.error("❌ Original test failed")
        if show_debug:
            st.exception(e)

if __name__ == "__main__":
    main()
